"""
Example FastAPI application with Consul registration.

This example demonstrates:
1. Multiple service types (worker, indexer, service)
2. Different registration patterns
3. Health endpoint configuration
4. Custom metadata

To run:
    # Start Consul (using Docker)
    docker run -d -p 8500:8500 hashicorp/consul:latest

    # Set environment variables
    export CONSUL_HOST=localhost
    export CONSUL_PORT=8500
    export ACCESS_HOST=localhost
    export ACCESS_PORT=8000
    export ENABLE_REGISTRATION=true

    # Run the application
    uvicorn example.main:app --reload
"""

import logging

from fastapi import FastAPI

from service_discovery import create_consul_lifespan

# Import our example services
from .services import (
    AuthService,
    DisabledService,
    DocumentIndexerService,
    PDFProcessorService,
    UserService,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Create FastAPI app with Consul registration
app = FastAPI(
    title="Example Service with Consul Registration",
    description="Demonstrates automatic Consul service registration",
    version="1.0.0",
    lifespan=create_consul_lifespan,
)

# Create service instances
pdf_processor = PDFProcessorService()
doc_indexer = DocumentIndexerService()
user_service = UserService()
auth_service = AuthService()
disabled_service = DisabledService()

# Include all routers
app.include_router(pdf_processor.router, tags=["Worker"])
app.include_router(doc_indexer.router, tags=["Indexer"])
app.include_router(user_service.router, tags=["Users"])
app.include_router(auth_service.router, tags=["Auth"])
# Note: disabled_service router is included but won't be registered with Consul
app.include_router(disabled_service.router, tags=["Disabled"])


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "Example Multi-Service Application",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "openapi": "/openapi.json",
            "services": {
                "worker": "/api/workers/v1",
                "indexer": "/api/indexers/v1",
                "users": "/api/v1",
                "auth": "/api/auth/v1",
            },
        },
    }


# Health endpoint (required for Consul health checks)
@app.get("/health")
async def health() -> dict[str, str]:
    """
    Health check endpoint for all services.

    In a real application, this would check:
    - Database connections
    - External service availability
    - Resource usage
    - etc.
    """
    return {"status": "healthy", "application": "example-service"}


# Service discovery endpoint (demonstrates querying Consul)
@app.get("/services")
async def list_registered_services():
    """
    List all services registered by this application.

    Note: This just shows what we registered, not querying Consul directly.
    In a real app, you might query Consul's API to show all services.
    """
    from service_discovery import get_service_registry

    services = get_service_registry().get_all_services()
    return {
        "registered_services": [
            {
                "name": service.name,
                "type": service.service_type.value,
                "base_route": service.base_route,
                "health_endpoint": service.health_endpoint,
                "enabled": service.enabled,
            }
            for service in services
        ],
        "total": len(services),
    }


# Service discovery endpoints
@app.get("/discover")
async def discover_services():
    """
    Discover all services registered in Consul (tagged as SERVICE).

    This demonstrates the service discovery functionality.
    """
    from service_discovery import create_service_discovery

    discovery = create_service_discovery()

    try:
        # Get all available services
        services = await discovery.get_services()

        # Get details for each service
        service_details = {}
        for service_name, uris in services.items():
            service_details[service_name] = {
                "instance_count": len(uris),
                "uris": uris,
                "random_uri": await discovery.get_service_uri(service_name),
            }

        return {"discovered_services": service_details, "total_services": len(services)}
    finally:
        await discovery.close()


@app.get("/discover/{service_name}")
async def discover_specific_service(service_name: str):
    """
    Discover a specific service by name.

    Args:
        service_name: Name of the service to discover
    """
    from service_discovery import create_service_discovery

    discovery = create_service_discovery()

    try:
        # Get all URIs for the service
        all_uris = await discovery.get_all_service_uris(service_name)

        if not all_uris:
            return {"error": f"Service '{service_name}' not found", "available": False}

        # Get a random URI (simulating load balancing)
        random_uri = await discovery.get_service_uri(service_name)

        return {
            "service_name": service_name,
            "available": True,
            "instance_count": len(all_uris),
            "all_uris": all_uris,
            "random_uri": random_uri,
            "load_balanced": len(all_uris) > 1,
        }
    finally:
        await discovery.close()


# Self-discovery endpoint
@app.get("/self-discover")
async def self_discover():
    """
    Demonstrate self-discovery - discover this service itself.

    This is useful for testing that registration and discovery work together.
    """
    from service_discovery import create_service_discovery

    discovery = create_service_discovery()

    try:
        # Try to discover our own registered services
        all_services = await discovery.get_services()

        # Check which of our services are discoverable
        our_services = ["user-service", "auth-service"]
        discovered = {}

        for service_name in our_services:
            uri = await discovery.get_service_uri(service_name)
            discovered[service_name] = {
                "registered": service_name in all_services,
                "uri": uri,
                "discoverable": uri is not None,
            }

        return {"self_discovery": discovered, "all_discovered_services": list(all_services.keys())}
    finally:
        await discovery.close()


if __name__ == "__main__":
    import uvicorn

    # Run the application
    uvicorn.run(
        "example.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
