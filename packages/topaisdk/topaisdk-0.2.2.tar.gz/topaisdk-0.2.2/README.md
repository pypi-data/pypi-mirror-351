# topaisdk

## setup

```shell
pip install topaisdk
```

```shell
python setup.py sdist bdist_wheel
python -m twine upload dist/*
```

## Features

This SDK provides the following features for Ray Serve services:

- **Latency Metrics Collection**: Collects and reports request latency, request rate, and error rate.
- **Consecutive Failure Health Check**: Provides a decorator to add consecutive failure tracking and health check for model service methods.

## Usage

### Latency Metrics Collection

To collect latency metrics, you need to use the `setup_metrics_to_serve` function and the `LatencyMiddleware`.

First, import the necessary components:

```python
from topaisdk.metrics import setup_metrics_to_serve, LatencyMiddleware
from ray import serve
from fastapi import FastAPI
```

Then, in your Ray Serve application setup, call `setup_metrics_to_serve` and add `LatencyMiddleware` to your FastAPI app:
service_id is the name of the deployment used for auto-scaling.
When the system detects the need for scaling, it will scale based on the service_id.
When using service_id, ensure it is unique and refers to the deployment that actually needs scaling.
(e.g., if DeploymentA receives external HTTP requests but DeploymentB provides the service internally,service_id should be set to DeploymentB's name, not DeploymentA's).
By default, service_id is set to the name of the current deployment. It can also be specified manually.

```python
app = FastAPI()
serve.init()

# Configure metrics
metrics_config = {
    "service_id": "myService", # service id
    "metrics_server_url": "http://your-metrics-server:port/metrics", # Replace with your metrics server URL
    "metrics_report_interval": 10 # Reporting interval in seconds
}
setup_metrics_to_serve(deployment, app, metrics_config)

# Add latency middleware
app.add_middleware(LatencyMiddleware, metrics_collector=serve.metrics_collector)

# Define your Ray Serve deployment
@serve.deployment()
@serve.ingress(app)
class MyModel:
    # Your model serving logic here
    pass

# Deploy your model
MyModel.deploy()
```

Alternatively, you can manually collect and report latency metrics using the `MetricsCollector` instance associated with the deployment:

```python
from topaisdk.metrics import MetricsCollector

# Assuming you have a deployment object, access its metrics_collector
# deployment.metrics_collector = MetricsCollector(...)

# Then, within your service logic, report metrics like this:
self.metrics_collector.add_latency_measurement(
    request_path=request.url.path,
    latency_ms=process_time_ms,
    error=False
)
```

Ensure you have a metrics server running at the specified `metrics_server_url` to receive the reported metrics.

### Consecutive Failure Health Check

To use the consecutive failure health check, import the `ModelService` and use the `consecutive_failure` decorator on your model service methods.

```python
from topaisdk.modelservice import ModelService
from ray import serve

@serve.deployment()
class MyModelService(ModelService): # Inherit from ModelService
    def __init__(self):
        super().__init__()
        # Your initialization

    @ModelService.consecutive_failure(max_failures_num=5) # Apply the decorator
    async def predict(self, input_data):
        # Your prediction logic
        # If this method raises exceptions consecutively for 5 times,
        # the service health check will fail.
        pass

    # Ray Serve health check method
    async def check_health(self):
        self.check_health() # This will raise an error if the service is unhealthy

# Deploy your service
MyModelService.deploy()
```

## Examples

### Ray Serve Metrics Example

This example demonstrates how to use the latency metrics collection feature in a Ray Serve application.

1. **Install Dependencies**:
   Navigate to the `examples` directory and install the required packages.

   ```bash
   cd examples
   pip install -r requirements.txt
   ```
2. **Start Dummy Metrics Server**:
   This script simulates a server that receives metrics. Run it in a separate terminal.

   ```bash
   python dummy_metrics_server.py
   ```

   This server will listen on `http://localhost:8000`.
3. **Generate Serve Config (Optional)**:
   You can use `serve build` to generate a configuration file for the application. By default, it will save to `serve_config.yaml`.

   ```bash
   cd examples
   serve build serve_example:my_service_app
   # This will create serve_config.yaml in the examples directory.
   # You can then edit serve_config.yaml to change the HTTP port or other settings.
   cd .. # Go back to project root
   ```

   Alternatively, you can manually create `examples/serve_config.yaml` with the desired HTTP port (e.g., 1234):

   ```yaml
   http_options:
     port: 1234
   ```
4. **Start Ray Serve Application**:
   In the project root directory (where `README.md` is located), run the Ray Serve application using the generated or manual config file. Make sure you are in the project root directory before running this command.

   ```bash
   serve run examples/serve_config.yaml
   or
   serve run examples.serve_example:my_service_app
   ```
5. **Send Requests**:
   Once the Ray Serve application is running, you can send requests to the endpoints on the configured port (e.g., 1234).

   * For a quick response:
     ```bash
     curl http://localhost:1234/hello
     ```
   * To simulate a slower request and see latency metrics:
     ```bash
     curl http://localhost:1234/slow
     ```

   Send multiple requests to `/slow` to trigger metrics reporting more frequently. You should see the reported metrics in the terminal where you ran `dummy_metrics_server.py`.

**Note**: The `metrics_server_url` in `examples/serve_example.py` is set to `http://localhost:8000`, which is the port the dummy metrics server listens on. This should **not** be changed unless you also change the port of the `dummy_metrics_server.py` script.
