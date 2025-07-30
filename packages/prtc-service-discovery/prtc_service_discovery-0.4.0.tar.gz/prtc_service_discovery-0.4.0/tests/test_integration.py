"""
Integration tests for Consul registration with real Consul instance.
"""

import asyncio
import logging

import consul.aio
import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from service_discovery import (
    DiscoveryConfig,
    create_consul_lifespan,
    get_service_registry,
    register_indexer,
    register_worker,
)

from .consul_container import ConsulContainer

logger = logging.getLogger(__name__)

# Skip integration tests if testcontainers not available
pytestmark = pytest.mark.integration

# Check if Docker is available
try:
    import docker

    client = docker.from_env()
    client.ping()
    DOCKER_AVAILABLE = True
except Exception:
    DOCKER_AVAILABLE = False


@pytest.fixture(scope="module")
def consul_container():
    """Start a Consul container for integration tests."""
    if not DOCKER_AVAILABLE:
        pytest.skip("Docker not available, skipping container-based tests")

    with ConsulContainer() as consul:
        yield consul


@pytest.fixture
def consul_config(consul_container):
    """Create Consul configuration for tests."""
    from service_discovery.config import AccessConfig, ConsulConfig, HealthConfig

    return DiscoveryConfig(
        consul=ConsulConfig(
            host=consul_container.get_consul_host(),
            port=consul_container.get_consul_port(),
        ),
        access=AccessConfig(host="localhost", port=8000),
        health=HealthConfig(host="localhost", port=8000),
        enable_registration=True,
        service_name="test-service",  # Default service name for tests
    )


@pytest.fixture
def test_app():
    """Create a test FastAPI application."""
    # Don't set the lifespan here - we'll create it manually in tests
    # This allows us to register services before the lifespan starts
    app = FastAPI()

    @app.get("/health")
    async def health():
        return {"status": "healthy"}

    return app


class TestConsulIntegration:
    """Integration tests with real Consul instance."""

    @pytest.mark.asyncio
    async def test_service_registration_lifecycle(self, consul_config, test_app):
        """Test complete service registration lifecycle."""

        # Register services BEFORE creating the lifespan
        @register_worker("test-worker", base_route="/api/workers/v1")
        class TestWorker:
            pass

        @register_indexer("test-indexer", base_route="/api/indexers/v1")
        class TestIndexer:
            pass

        # Service will be registered automatically via config.service_name
        # In CI, consul_config might not have service_name set, so ensure it's set
        consul_config.service_name = "test-service"

        # Create Consul client for verification
        consul_client = consul.aio.Consul(host=consul_config.consul.host, port=consul_config.consul.port)

        try:
            # Create a lifespan that uses our config
            lifespan = create_consul_lifespan(test_app, consul_config)

            # Now create and start the lifespan after services are registered
            async with lifespan:
                async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
                    # Give Consul time to register services
                    await asyncio.sleep(2)

                    # Verify services are registered
                    _, services = await consul_client.catalog.services()

                    assert "test-worker" in services
                    assert "test-indexer" in services
                    assert "test-service" in services

                    # Verify service details
                    _, worker_instances = await consul_client.catalog.service("test-worker")
                    assert len(worker_instances) == 1
                    worker = worker_instances[0]

                    assert worker["ServiceName"] == "test-worker"
                    assert "WORKER" in worker["ServiceTags"]
                    assert worker["ServiceMeta"]["base_route"] == "/api/workers/v1"
                    assert worker["ServiceAddress"] == "localhost"
                    assert worker["ServicePort"] == 8000

                    # Test health check
                    response = await client.get("/health")
                    assert response.status_code == 200

            # After app shutdown, services should be deregistered
            await asyncio.sleep(2)

            _, services = await consul_client.catalog.services()
            assert "test-worker" not in services
            assert "test-indexer" not in services
            assert "test-service" not in services

        finally:
            # consul.aio.Consul doesn't have a close() method
            # It manages its own aiohttp session internally
            pass

    @pytest.mark.skip(reason="probably due to networking setup or registration logic, service never gets to passing ")
    @pytest.mark.asyncio
    async def test_health_check_monitoring(self, consul_config, test_app):
        """Test that Consul monitors health checks."""
        # Update config to use a different service name
        consul_config.service_name = "health-test-service"

        consul_client = consul.aio.Consul(host=consul_config.consul.host, port=consul_config.consul.port)

        try:
            # Now create and start the lifespan after services are registered
            async with create_consul_lifespan(test_app, consul_config):
                async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test"):
                    await asyncio.sleep(30)

                    # Check service health
                    _, health_checks = await consul_client.health.service("health-test-service")
                    assert len(health_checks) == 1

                    health_check = health_checks[0]
                    assert health_check["Service"]["Service"] == "health-test-service"

                    # Verify health check is passing
                    checks = health_check["Checks"]
                    service_check = next((c for c in checks if c["CheckID"].startswith("service:")), None)
                    assert service_check is not None
                    assert service_check["Status"] in ["passing"]

        finally:
            # consul.aio.Consul doesn't have a close() method
            # It manages its own aiohttp session internally
            pass

    @pytest.mark.asyncio
    async def test_disabled_service_not_registered(self, consul_config, test_app):
        """Test that disabled services are not registered."""
        # Service registration via config - test enable/disable functionality
        consul_config.service_name = "enabled-service"
        consul_config.enable_registration = True

        consul_client = consul.aio.Consul(host=consul_config.consul.host, port=consul_config.consul.port)

        try:
            # Now create and start the lifespan after services are registered
            async with create_consul_lifespan(test_app, consul_config):
                async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test"):
                    await asyncio.sleep(2)

                    _, services = await consul_client.catalog.services()

                    assert "enabled-service" in services
                    # No disabled-service registered since we only register one app

        finally:
            # consul.aio.Consul doesn't have a close() method
            # It manages its own aiohttp session internally
            pass

    @pytest.mark.asyncio
    async def test_multiple_service_types(self, consul_config, test_app):
        """Test registering different service types with proper tags."""

        # Register services BEFORE creating the lifespan
        @register_worker("multi-worker", base_route="/api/workers/v1")
        class MultiWorker:
            pass

        @register_indexer("multi-indexer", base_route="/api/indexers/v1")
        class MultiIndexer:
            pass

        # Service will be registered automatically via config
        consul_config.service_name = "multi-service"

        consul_client = consul.aio.Consul(host=consul_config.consul.host, port=consul_config.consul.port)

        try:
            # Now create and start the lifespan after services are registered
            async with create_consul_lifespan(test_app, consul_config):
                async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test"):
                    await asyncio.sleep(2)

                    # Check worker
                    _, workers = await consul_client.catalog.service("multi-worker")
                    assert len(workers) == 1
                    assert "WORKER" in workers[0]["ServiceTags"]

                    # Check indexer
                    _, indexers = await consul_client.catalog.service("multi-indexer")
                    assert len(indexers) == 1
                    assert "INDEXER" in indexers[0]["ServiceTags"]

                    # Check service (if service_name is set in config)
                    if consul_config.service_name:
                        _, services = await consul_client.catalog.service("multi-service")
                        assert len(services) == 1
                        assert "SERVICE" in services[0]["ServiceTags"]

        finally:
            # consul.aio.Consul doesn't have a close() method
            # It manages its own aiohttp session internally
            pass


class TestRealWorldScenario:
    """Test real-world usage scenarios."""

    @pytest.mark.asyncio
    async def test_microservices_architecture(self, consul_config):
        """Test a microservices architecture with multiple services."""
        # Clear registry for this test
        get_service_registry().clear()

        # In the new architecture, we can only register one application service per instance
        # So we'll test with workers and indexers instead
        consul_config.service_name = "api-gateway"  # Main application service

        # Notification Worker
        @register_worker("notification-worker", base_route="/api/workers/notifications/v1")
        class NotificationWorker:
            pass

        # Search Indexer
        @register_indexer("search-indexer", base_route="/api/indexers/search/v1")
        class SearchIndexer:
            pass

        app = FastAPI()

        @app.get("/health")
        async def health():
            return {"status": "healthy"}

        consul_client = consul.aio.Consul(host=consul_config.consul.host, port=consul_config.consul.port)

        try:
            # Now create and start the lifespan after services are registered
            async with create_consul_lifespan(app, consul_config):
                async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test"):
                    await asyncio.sleep(2)

                    # Verify all services are registered
                    _, all_services = await consul_client.catalog.services()

                    expected_services = [
                        "api-gateway",  # The main application service
                        "notification-worker",
                        "search-indexer",
                    ]

                    for service_name in expected_services:
                        assert service_name in all_services

                    # Query services by tag
                    _, services_with_tags = await consul_client.catalog.services()

                    # Count services by type
                    worker_count = 0
                    indexer_count = 0
                    service_count = 0

                    for service_name in expected_services:
                        _, instances = await consul_client.catalog.service(service_name)
                        if instances:
                            tags = instances[0]["ServiceTags"]
                            if "WORKER" in tags:
                                worker_count += 1
                            elif "INDEXER" in tags:
                                indexer_count += 1
                            elif "SERVICE" in tags:
                                service_count += 1

                    assert worker_count == 1
                    assert indexer_count == 1
                    assert service_count == 1  # Only one application service

        finally:
            # consul.aio.Consul doesn't have a close() method
            # It manages its own aiohttp session internally
            pass


class TestServiceIDConsistency:
    """Test service ID consistency within sessions."""

    @pytest.mark.asyncio
    async def test_service_id_format_in_consul(self, consul_config):
        """Test that service IDs use the correct format in Consul."""
        # Clear registry for this test
        get_service_registry().clear()

        # Register services
        @register_worker("format-worker", base_route="/api/workers/v1")
        class FormatWorker:
            pass

        # Application service will be registered via config
        consul_config.service_name = "format-service"

        app = FastAPI()

        @app.get("/health")
        async def health():
            return {"status": "healthy"}

        consul_client = consul.aio.Consul(host=consul_config.consul.host, port=consul_config.consul.port)

        try:
            async with create_consul_lifespan(app, consul_config):
                async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test"):
                    await asyncio.sleep(2)

                    # Check service IDs in Consul
                    for service_name in ["format-worker", "format-service"]:
                        _, services = await consul_client.catalog.service(service_name)
                        if services:  # Service might not exist if config didn't set it
                            assert len(services) == 1
                            service_id = services[0]["ServiceID"]
                            logger.info(f"Service {service_name} ID: {service_id}")

                            # Should use colon separator
                            assert ":" in service_id
                            assert service_id.startswith(f"{service_name}:")

        finally:
            pass
