import logging
import time
import asyncio
import os
import re
import json
import threading
from typing import Dict, List, Union, Any, Optional, Tuple

from pydantic import BaseModel
from scipy.special import softmax
from fastapi import FastAPI, HTTPException
from starlette.requests import Request
from starlette.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware

from ray import serve
import httpx
import requests

logger = logging.getLogger("ray.serve")


class MetricsCollector:
    """Collects and processes latency metrics.
    
    service_id is the name of the deployment used for auto-scaling.
    When the system detects the need for scaling, it will scale based on the service_id.
    When using service_id, ensure it is unique and refers to the deployment that actually needs scaling.
    (e.g., if DeploymentA receives external HTTP requests but DeploymentB provides the service internally,
    service_id should be set to DeploymentB's name, not DeploymentA's).
    By default, service_id is set to the name of the current deployment. It can also be specified manually.

    manually create a metrics collector and report latency metrics to the metrics server.
    ```python
    # create a metrics collector
    deployment.metrics_collector = MetricsCollector(
        service_id=service_id,
        metric_server_url=metrics_server_url,
        report_interval_seconds=config.get("metrics_report_interval", 10),
        use_threading=config.get("use_threading", False) # use threading or async for reporting
    )
    # start the metrics reporting
    deployment.metrics_collector.start()
    
    # add a latency measurement
    deployment.metrics_collector.add_latency_measurement(
        request_path=request.url.path,
        latency_ms=process_time_ms,
        error=False
    )
    ```

    """
    
    def __init__(self, 
                 service_id: str = None,
                 metric_server_url: str = None, 
                 report_interval_seconds: int = 10,
                 use_threading: bool = False):
        assert metric_server_url is not None, "metric_server_url is required"
        assert type(report_interval_seconds) == int and report_interval_seconds > 0, "report_interval_seconds must be a positive integer and greater than 0"

        self.service_id = service_id
        self.metric_server_url = metric_server_url
        self.report_interval_seconds = report_interval_seconds
        self.use_threading = use_threading
        
        # Store latency measurements
        self.request_latency_ms = []
        self.request_count = 0
        self.request_error_count = 0
        
        # Buffer for fast, lock-free measurements
        self.buffer_latency_ms = []
        self.buffer_request_count = 0
        self.buffer_error_count = 0
        
        # Additional metadata
        self.replica_tag = None
        self.deployment = None
        self.app_name = None
        try:
            replica_context = serve.get_replica_context()
            self.replica_tag = replica_context.replica_tag
            self.deployment = replica_context.deployment
            self.app_name = replica_context.app_name
        except:
            self.replica_tag = f"replica-{hash(self)}"
            self.deployment = 'unknown'
            self.app_name = 'unknown'

        # get the kuberay serve name from the environment variable, k8s and kuberay will set it
        kuberay_serve_name = os.getenv("RAY_CLUSTER_NAME", None)
        if kuberay_serve_name is None:
            kuberay_serve_name = 'unknown'
        else:
            match = re.search(r"(.*)-raycluster-", kuberay_serve_name)
            if match:
                kuberay_serve_name = match.group(1)
            else:
                kuberay_serve_name = 'unknown'
        self.kuberay_serve_name = kuberay_serve_name

        if self.service_id is None:
            self.service_id = self.deployment
        self.reporter = f"{self.kuberay_serve_name}.{self.app_name}.{self.deployment}.{self.replica_tag}"
        self.labels = {
            "deployment": self.deployment,
            "app_name": self.app_name,
            "replica": self.replica_tag,
            "kuberay_serve_name": self.kuberay_serve_name,
            "reporter": self.reporter
        }

        # Background task for reporting
        self.running = False
        self.reporting_task = None
        self._async_client = None  # Added for async client
        
        # Thread-related attributes
        self.reporting_thread = None
        self.thread_event = None
        self.buffer_transfer_task = None
        
        # Lock for thread safety
        self._lock = None
        if self.use_threading:
            self._lock = threading.Lock()
            self.thread_event = threading.Event()
        else:
            # Create async client for async mode
            self._async_client = httpx.AsyncClient()

        logger.info(f"MetricsCollector initialized for {self.service_id} done running in {'thread' if self.use_threading else 'async'} mode, serve labels: {json.dumps(self.labels, indent=4)}")

    def start(self):
        """Start the metrics reporting loop."""
        if self.running:
            logger.warning("Metrics collector already running")
            return
            
        self.running = True
        
        if self.use_threading:
            self._start_threaded_reporting()
        else:
            self._start_async_reporting()
        
        # Start buffer transfer task if using threading
        if self.use_threading:
            self._start_buffer_transfer()
        
        logger.info(f"Started latency metrics reporting for {self.service_id} using {'threaded' if self.use_threading else 'async'} mode")
    
    def _start_async_reporting(self):
        """Start the async reporting loop."""
        self.reporting_task = asyncio.create_task(self._reporting_loop())
    
    def _start_threaded_reporting(self):
        """Start the threaded reporting loop."""
        self.thread_event = threading.Event()
        self.reporting_thread = threading.Thread(
            target=self._reporting_thread_loop,
            daemon=True
        )
        self.reporting_thread.start()
    
    def _start_buffer_transfer(self):
        """Start the buffer transfer task."""
        self.buffer_transfer_task = asyncio.create_task(self._buffer_transfer_loop())
        logger.debug("Started buffer transfer task")
        
    async def stop(self):
        """Stop the metrics reporting loop."""
        if not self.running:
            return
            
        self.running = False
        
        if self.use_threading:
            await self._stop_threaded_reporting()
        else:
            await self._stop_async_reporting()
            await self._close_async_client() # Close client in async mode
        
        # Stop buffer transfer task if it exists
        await self._stop_buffer_transfer()

    async def _stop_async_reporting(self):
        """Stop the async reporting loop."""
        if self.reporting_task:
            self.reporting_task.cancel()
            try:
                await self.reporting_task
            except asyncio.CancelledError:
                pass

    async def _stop_threaded_reporting(self):
        """Stop the threaded reporting loop."""
        if self.reporting_thread:
            self.thread_event.set()  # Signal thread to exit
            
            # Wait for thread to complete, but don't block in async context
            await asyncio.to_thread(self._join_reporting_thread)

    async def _stop_buffer_transfer(self):
        """Stop the buffer transfer task."""
        if self.buffer_transfer_task:
            self.buffer_transfer_task.cancel()
            try:
                await self.buffer_transfer_task
            except asyncio.CancelledError:
                pass

    def _join_reporting_thread(self):
        """Join the reporting thread with timeout."""
        if self.reporting_thread and self.reporting_thread.is_alive():
            self.reporting_thread.join(timeout=5)
            if self.reporting_thread.is_alive():
                logger.warning("Metrics reporting thread did not terminate gracefully")
                
    async def _close_async_client(self):
        """Close the httpx.AsyncClient."""
        if self._async_client:
            await self._async_client.close()
            logger.debug("httpx.AsyncClient closed")

    async def _reporting_loop(self):
        """Background task that reports metrics at regular intervals (async mode)."""
        while self.running:
            try:
                await self._report_metrics_async()
                await asyncio.sleep(self.report_interval_seconds)
            except asyncio.CancelledError:
                logger.info("Async latency reporting loop cancelled")
                break
            except Exception:
                logger.exception("Error in async latency reporting loop")
                await asyncio.sleep(1)
    
    def _reporting_thread_loop(self):
        """Background thread that reports metrics at regular intervals."""
        while self.running and not self.thread_event.is_set():
            try:
                self._report_metrics_sync()
                self.thread_event.wait(self.report_interval_seconds)
            except Exception:
                logger.exception("Error in threaded latency reporting loop")
                time.sleep(1)
    
    async def _buffer_transfer_loop(self):
        """Transfer metrics from buffer to thread-safe storage periodically."""
        while self.running:
            try:
                self._transfer_buffer_data()
                # Shorter interval to ensure data is transferred quickly
                await asyncio.sleep(0.1)
            except asyncio.CancelledError:
                # Final transfer to ensure buffer is emptied
                self._transfer_buffer_data()
                break
            except Exception:
                logger.exception("Error in buffer transfer loop")
                await asyncio.sleep(0.1)

    def _transfer_buffer_data(self):
        """Transfer data from buffer to thread-safe storage."""
        # Quickly get and reset buffer
        buffer_latency = self.buffer_latency_ms
        buffer_count = self.buffer_request_count
        buffer_error = self.buffer_error_count
        
        self.buffer_latency_ms = []
        self.buffer_request_count = 0
        self.buffer_error_count = 0
        
        if not buffer_latency and buffer_count == 0:
            return  # No data to transfer
        
        # Thread-safely add to main storage
        with self._lock:
            self.request_latency_ms.extend(buffer_latency)
            self.request_count += buffer_count
            self.request_error_count += buffer_error
                
    async def _report_metrics_async(self):
        """Generate and report latency metrics to the metrics server (async version)."""
        if not self.metric_server_url:
            logger.debug("No metrics server URL provided, skipping report")
            return
            
        logger.info(f"Reporting latency metrics for {self.service_id} (async mode)")
        
        start_time = time.time()

        # Get metrics data
        metrics_list, payload = self._prepare_metrics_payload()
        if not metrics_list:
            return
        
        # Use async HTTP client to report
        try:
            # Use the initialized async client
            response = await self._async_client.post(
                f"{self.metric_server_url}/metrics",
                json=payload,
                timeout=5.0
            )
            if response.status_code != 200:
                logger.error(f"Failed to report latency metrics: {response.status_code} {response.text}")
            else:
                logger.debug(f"Reported {len(metrics_list)} latency metrics to {self.metric_server_url}")
        except Exception as e:
            logger.exception(f"Error reporting latency metrics")
        
        logger.info(f"Reported {self.service_id} {len(metrics_list)} latency metrics to {self.metric_server_url} done, used {(time.time() - start_time) * 1000:.2f} ms")

    def _report_metrics_sync(self):
        """Generate and report latency metrics to the metrics server (sync version)."""
        if not self.metric_server_url:
            logger.debug("No metrics server URL provided, skipping report")
            return
            
        logger.info(f"Reporting latency metrics for {self.service_id} (threaded mode)")

        start_time = time.time()

        # Get metrics data
        metrics_list, payload = self._prepare_metrics_payload()
        if not metrics_list:
            return
        
        # Use sync HTTP client to report
        try:
            response = requests.post(
                f"{self.metric_server_url}/metrics",
                json=payload,
                timeout=5.0
            )
            if response.status_code != 200:
                logger.error(f"Failed to report latency metrics: {response.status_code} {response.text}")
            else:
                logger.debug(f"Reported {len(metrics_list)} latency metrics to {self.metric_server_url}")
        except Exception as e:
            logger.exception(f"Error reporting latency metrics")
        
        logger.info(f"Reported {self.service_id} {len(metrics_list)} latency metrics to {self.metric_server_url} done, used {(time.time() - start_time) * 1000:.2f} ms")
    
    def _prepare_metrics_payload(self) -> Tuple[List[Dict], Dict]:
        """Prepare metrics payload for reporting."""
        metrics_list = []
        current_time = int(time.time()*1000)  # use milliseconds
        
        # Get and reset metrics data (thread-safe)
        if self.use_threading:
            with self._lock:
                if not self.request_latency_ms:
                    return [], {}
                    
                latencies = self.request_latency_ms.copy()
                self.request_latency_ms = []
                
                local_request_count = self.request_count
                local_error_count = self.request_error_count
                self.request_count = 0
                self.request_error_count = 0
        else:
            # Async mode, no lock needed
            if not self.request_latency_ms:
                return [], {}
                
            latencies = self.request_latency_ms.copy()
            self.request_latency_ms = []
            
            local_request_count = self.request_count
            local_error_count = self.request_error_count
            self.request_count = 0
            self.request_error_count = 0
        
        # Build metrics list
        for i, latency in enumerate(latencies):
            metrics_list.append({
                "value": latency["latency_ms"],
                "timestamp": current_time,
                "labels": {"name": "request_latency", 
                          "unit": "ms", 
                          "request_id": f"req-{i}",
                          "request_path": latency["request_path"]}
            })
        
        # Calculate request rate and error rate
        request_rate = local_request_count / self.report_interval_seconds
        error_rate = local_error_count / max(1, local_request_count)
        
        metrics_list.extend([
            {
                "value": request_rate,
                "timestamp": current_time,
                "labels": {"name": "request_rate", "unit": "rps"}
            },
            {
                "value": error_rate,
                "timestamp": current_time,
                "labels": {"name": "error_rate", "unit": "ratio"}
            }
        ])
        
        # Build complete payload
        payload = {
            "service_id": self.service_id,
            "metrics": metrics_list,
            "metadata": {
                **self.labels,
            },
            "metrics_complete": False
        }
        
        return metrics_list, payload
    
    # Legacy method for backward compatibility
    async def report_metrics(self):
        """Generate and report latency metrics to the metrics server."""
        return await self._report_metrics_async()
            
    def add_latency_measurement(self, request_path: str, latency_ms: float, error: bool = False):
        """Add a latency measurement to the collector."""
        if self.use_threading:
            # Fast, lock-free buffer for threaded mode
            self.buffer_latency_ms.append(
                {
                    "latency_ms": latency_ms,
                    "request_path": request_path,
                }
            )
            self.buffer_request_count += 1
            if error:
                self.buffer_error_count += 1
        else:
            # Direct addition for async mode
            self.request_latency_ms.append(
                {
                    "latency_ms": latency_ms,
                    "request_path": request_path,
                }
            )
            self.request_count += 1
            if error:
                self.request_error_count += 1


class LatencyMiddleware(BaseHTTPMiddleware):
    """Middleware to measure request latency."""
    
    def __init__(self, app, metrics_collector: MetricsCollector):
        super().__init__(app)
        self.metrics_collector = metrics_collector

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        try:
            response = await call_next(request)
            process_time_ms = (time.time() - start_time) * 1000
            
            # Record latency
            self.metrics_collector.add_latency_measurement(
                request_path=request.url.path,
                latency_ms=process_time_ms,
                error=False
            )
            
            # Add latency headers for debugging
            response.headers["X-Process-Time-Ms"] = f"{process_time_ms:.2f}"
            return response
            
        except Exception as e:
            process_time_ms = (time.time() - start_time) * 1000
            
            # Record error latency
            self.metrics_collector.add_latency_measurement(
                request_path=request.url.path,
                latency_ms=process_time_ms,
                error=True
            )
            
            # Re-raise the exception
            raise e


def setup_metrics_to_deployment(deployment, app: FastAPI, config: Dict[str, Any]):
    """
    Setup the metrics collector settings to the deployment.
    automatically add the latency middleware to the app(fastapi).
    
    Args:
        service_id: The service id of the deployment
        deployment: The deployment object
        app: The FastAPI app object
        config: Dictionary containing configuration parameters
            - service_id: The service ID for metrics reporting
            - metrics_server_url: URL of the metrics server
            - metrics_report_interval: Interval in seconds between reports
            - use_threading: Whether to use thread-based reporting (default: False)

    example:
    setup_metrics_to_serve(deployment, app, {
        "service_id": "my-example-service",
        "metrics_server_url": "http://localhost:8000/metrics",
        "metrics_report_interval": 10,
        "use_threading": True  # Use thread-based reporting
    })
    """
    service_id = config.get("service_id", None)
    metrics_server_url = config.get("metrics_server_url", None)
    use_threading = config.get("use_threading", False)
    
    if metrics_server_url is None:
        raise ValueError("metrics_server_url is required")
    
    # Shutdown existing metrics collector if it exists
    if hasattr(deployment, "metrics_collector") and deployment.metrics_collector:
        asyncio.create_task(deployment.metrics_collector.stop())

    
    # Create new metrics collector
    deployment.metrics_collector = MetricsCollector(
        service_id=service_id,
        metric_server_url=metrics_server_url,
        report_interval_seconds=config.get("metrics_report_interval", 10),
        use_threading=use_threading
    )
    
    # Start metrics reporting if URL is provided
    if metrics_server_url:
        deployment.metrics_collector.start()
        
        # Add latency middleware to the app if not already added
        if not any(isinstance(m, LatencyMiddleware) for m in app.user_middleware):
            app.add_middleware(LatencyMiddleware, metrics_collector=deployment.metrics_collector)
            logger.info("Added metrics (LatencyMiddleware) middleware to the FastAPI app")
