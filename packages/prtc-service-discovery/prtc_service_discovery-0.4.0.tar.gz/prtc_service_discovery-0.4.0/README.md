# Service Discovery

A Python library for microservice registration and discovery using Consul. This is the Python counterpart to [service-discovery-java](https://github.com/perceptic/service-discovery-java), providing configuration-based service registration and client-side load balancing for FastAPI applications.

## Installation

```bash
pip install prtc-service-discovery
```

**Note:** While the package is named `prtc-service-discovery` on PyPI, you import it as `service_discovery` in your code.

## Prerequisites

- Python 3.10+
- FastAPI application
- Consul server (for service registration/discovery)

## Quick Start

### Service Registration

**Option A: Automatic Configuration-Based Registration (Recommended)**

Register your entire application as a service using configuration - no code required!

```python
from fastapi import FastAPI
from service_discovery import create_consul_lifespan

# Set SERVICE_NAME environment variable or in config
# export SERVICE_NAME=perceptic-core

app = FastAPI(lifespan=create_consul_lifespan)

@app.get("/health")
async def health():
    return {"status": "healthy"}

# Your API routes are automatically part of the registered service
@app.get("/api/v1/users/{id}")
async def get_user(id: str):
    return {"id": id, "name": "John Doe"}
```

**Option B: Programmatic Registration**

```python
from fastapi import FastAPI
from service_discovery import ApplicationRegistration, create_consul_lifespan

app = FastAPI(lifespan=create_consul_lifespan)

async def startup():
    registration = ApplicationRegistration()
    await registration.register_application("perceptic-core")

app.add_event_handler("startup", startup)
```

### Service Discovery

```python
from service_discovery import create_service_discovery

# Discover services
discovery = create_service_discovery()

# Get all services (SERVICE, WORKER, and INDEXER types)
services = await discovery.get_services()
# Returns: {
#   "perceptic-core": ["http://10.0.0.1:8080", "http://10.0.0.2:8080"],  # No base route for services
#   "pdf-processor": ["http://10.0.0.3:8080/api/workers/v1"],            # Base route included for workers
#   "document-indexer": ["http://10.0.0.4:8080/api/indexers/v1"]         # Base route included for indexers
# }

# Get a random URI (client-side load balancing)
uri = await discovery.get_service_uri("perceptic-core")
# Returns: "http://10.0.0.1:8080"

# Get all URIs for a service
uris = await discovery.get_all_service_uris("perceptic-core")
# Returns: ["http://10.0.0.1:8080", "http://10.0.0.2:8080"]

# Cleanup
await discovery.close()
```

## Configuration

Configuration is handled through environment variables. All settings are optional with sensible defaults:

```bash
# Consul connection
CONSUL_HOST=localhost           # Consul server host (default: localhost)
CONSUL_PORT=8500               # Consul server port (default: 8500)

# Service networking
ACCESS_HOST=my-service.local   # Hostname/IP other services use to reach this service
ACCESS_PORT=8080              # Port other services use to reach this service

# Feature flags
ENABLE_REGISTRATION=true       # Enable/disable Consul registration (default: true)
SERVICE_NAME=perceptic-core    # Application name for automatic registration (optional)

# Health check networking (optional, defaults to ACCESS_HOST:ACCESS_PORT)
HEALTH_HOST=0.0.0.0           # Interface for health checks
HEALTH_PORT=8080              # Port for health checks
```

## Service Types

The library supports three types of service registration:

| Type | Registration Method | Consul Tag | Discoverable | Base Route Included | Use Case |
|------|-------------------|------------|--------------|-------------------|----------|
| Application Service | `SERVICE_NAME` config or `ApplicationRegistration` | `SERVICE` | ✅ Yes | ❌ No | REST APIs, gRPC services, and other client-facing services |
| Worker | `@register_worker` decorator | `WORKER` | ✅ Yes | ✅ Yes | Registering a worker for perceptic-core to discover |
| Indexer | `@register_indexer` decorator | `INDEXER` | ✅ Yes | ✅ Yes | Registering an indexer for perceptic-core to discover |

All service types are discoverable via the `ServiceDiscovery` client. Application services return base URIs without routes (clients specify full paths), while workers and indexers include their base routes in the discovered URIs.

## Testing

### Unit Testing

```python
from service_discovery import get_service_registry

def test_worker_registration():
    get_service_registry().clear()
    
    @register_worker("test-worker", base_route="/api/workers/v1")
    class TestWorker:
        pass
    
    services = get_service_registry().get_all_services()
    assert len(services) == 1
    assert services[0].name == "test-worker"
    assert services[0].service_type.value == "WORKER"
```

### Integration Testing

```python
from service_discovery.testing import ConsulRegistrationTestBase, ExpectedService

class TestMyApp(ConsulRegistrationTestBase):
    def get_expected_services(self) -> list[ExpectedService]:
        return [
            ExpectedService.api_service("my-app", 8080),  # Registered via SERVICE_NAME
            ExpectedService.worker("pdf-processor", 8080),
            ExpectedService.indexer("document-indexer", 8080),
        ]
    
    def create_app(self) -> FastAPI:
        import os
        os.environ["SERVICE_NAME"] = "my-app"
        from my_app import app
        return app
```

The base test class automatically verifies:
- Service registration with correct metadata
- Health check configuration
- Service deregistration on shutdown

## Advanced Usage

### Custom Configuration

```python
from service_discovery import DiscoveryConfig, create_consul_lifespan

config = DiscoveryConfig(
    consul__host="consul.prod",
    consul__port=8500,
    access__host="api.example.com",
    access__port=443,
    health__host="internal.example.com",  # Separate health check network
    health__port=8080,
    enable_registration=True,
    service_name="perceptic-core"  # Application service name
)

app = FastAPI(lifespan=lambda app: create_consul_lifespan(app, config))
```

### Worker and Indexer Registration

```python
@register_worker("pdf-processor", base_route="/api/workers/v1")
class PDFWorker:
    router = APIRouter()

@register_indexer("document-indexer", base_route="/api/indexers/v1")
class DocumentIndexer:
    router = APIRouter()

# Include routers
app.include_router(PDFWorker().router)
app.include_router(DocumentIndexer().router)
```

### Service Discovery Patterns

```python
# Singleton pattern
discovery = create_service_discovery()

async def make_user_service_call(user_id: str):
    # Get a random instance (client-side load balancing)
    uri = await discovery.get_service_uri("perceptic-core")
    if not uri:
        raise ServiceUnavailableError("perceptic-core not found")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{uri}/api/v1/users/{user_id}")
        return response.json()

# Context manager pattern
async def get_all_services():
    discovery = create_service_discovery()
    try:
        return await discovery.get_services()
    finally:
        await discovery.close()
```

## Architecture Notes

### Service Discovery
- Discovers all service types (`SERVICE`, `WORKER`, and `INDEXER`)
- Application services (SERVICE) return base URIs without routes
- Worker/Indexer services include their base routes in URIs
- Uses Consul's catalog API for real-time service discovery
- Implements client-side random load balancing
- Caches service data with configurable refresh interval (default: 30s)
- Automatic retry and error handling for network failures

### Service Registration
- Application services use configuration-based registration (SERVICE_NAME)
- Workers/Indexers use decorator-based registration with base routes
- Automatic registration on app startup via FastAPI lifespan events
- Built-in health check endpoint configuration
- Generates unique service IDs per instance (consistent within a session)
- Graceful deregistration on shutdown

### Key Differences from Java Library
- No Stork integration (uses simple random selection for load balancing)
- Discovery returns HTTP URIs directly instead of stork:// URIs
- No static service configuration fallback
- Async-first design using python-consul2
- Decorator-based registration instead of annotations

## Development

### Setup

This project uses Hatchling for packaging (not Poetry, as libraries should not pin dependencies). For development, create a virtual environment:

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On macOS/Linux
# .venv\Scripts\activate   # On Windows

# Install package in editable mode with dev dependencies
pip install -e ".[dev,test]"
```

### Running Tests & Quality Checks

```bash
# Run tests
make test           # All tests
make test-unit      # Unit tests only
make test-example   # Example app tests

# Code quality
make format         # Format with black
make lint          # Lint with ruff
make type-check    # Type check with mypy
make all           # All checks + tests
```

## Troubleshooting

### Services not registering
- Ensure `ENABLE_REGISTRATION=true` (or not set, as `true` is the default)
- Check that `ACCESS_HOST` and `ACCESS_PORT` are set correctly
- Verify Consul is reachable at `CONSUL_HOST:CONSUL_PORT`
- Check application logs for registration errors

### Services not discoverable
- Verify the service is registered with `@register_service` (not `@register_worker` or `@register_indexer`)
- Check that the service is healthy in Consul UI
- Ensure the service has the `SERVICE` tag in Consul

### Health checks failing
- Verify the `/health` endpoint is accessible at `HEALTH_HOST:HEALTH_PORT`
- If using separate health check networking, ensure `HEALTH_HOST` is reachable from Consul
- Check that the health endpoint returns a 2xx status code

## License

Proprietary - Perceptic Technologies Ltd.
