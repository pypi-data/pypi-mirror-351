"""
Integration tests for service discovery functionality.
"""

import asyncio
from collections.abc import Generator

import pytest
import pytest_asyncio
from fastapi import FastAPI

from service_discovery import (
    ConsulRegistrationService,
    DiscoveryConfig,
    ServiceDiscovery,
    create_consul_lifespan,
    register_service,
)
from service_discovery.config import AccessConfig, ConsulConfig

from .consul_container import ConsulContainer


async def wait_for_service(discovery: ServiceDiscovery, service_name: str, timeout: float = 60.0):
    """Wait for a service to appear in discovery."""
    start_time = asyncio.get_event_loop().time()
    while asyncio.get_event_loop().time() - start_time < timeout:
        services = await discovery.get_services()
        if service_name in services:
            return True
        await asyncio.sleep(0.5)
    return False


@pytest.mark.integration
class TestServiceDiscoveryIntegration:
    """Integration tests for service discovery with real Consul."""

    @pytest.fixture(scope="class")
    def consul_container(self) -> Generator[ConsulContainer, None, None]:
        """Start a Consul container for testing."""
        with ConsulContainer() as consul:
            yield consul

    @pytest_asyncio.fixture
    async def config(self, consul_container: ConsulContainer) -> DiscoveryConfig:
        """Create configuration for test."""
        config = DiscoveryConfig(
            consul=ConsulConfig(
                host=consul_container.get_container_host_ip(),
                port=consul_container.get_exposed_port(8500),
            ),
            access=AccessConfig(
                host="localhost",
                port=8080,
            ),
            ENABLE_REGISTRATION=True,  # Use the alias
        )
        return config

    @pytest_asyncio.fixture
    async def registration_service(self, config: DiscoveryConfig) -> ConsulRegistrationService:
        """Create a registration service."""
        # Clear any existing registrations
        from service_discovery import get_service_registry

        get_service_registry().clear()

        service = ConsulRegistrationService(config)
        yield service
        # Cleanup
        await service.deregister_services()
        get_service_registry().clear()

    @pytest.mark.asyncio
    async def test_discover_registered_service(
        self, config: DiscoveryConfig, registration_service: ConsulRegistrationService
    ):
        """Test discovering a service that has been registered."""

        # Register a test service
        @register_service("test-api", base_route="/api/v1")
        class TestAPI:
            pass

        # Register the service
        await registration_service.register_services()

        # Create discovery client
        discovery = ServiceDiscovery(config)

        try:
            # Wait for service to appear in discovery
            found = await wait_for_service(discovery, "test-api", timeout=30.0)
            assert found, "Service 'test-api' was not discovered within timeout"

            # Discover services
            services = await discovery.get_services()

            # Verify our service is discovered
            assert "test-api" in services
            assert len(services["test-api"]) == 1
            assert services["test-api"][0] == "http://localhost:8080/api/v1"

            # Test get_service_uri
            uri = await discovery.get_service_uri("test-api")
            assert uri == "http://localhost:8080/api/v1"

            # Test get_all_service_uris
            all_uris = await discovery.get_all_service_uris("test-api")
            assert all_uris == ["http://localhost:8080/api/v1"]

        finally:
            await discovery.close()

    @pytest.mark.asyncio
    async def test_discover_multiple_service_instances(self, config: DiscoveryConfig):
        """Test discovering multiple instances of the same service."""
        from service_discovery import get_service_registry

        # Clear registry
        get_service_registry().clear()

        # Register the service once
        @register_service("multi-api", base_route="/api/v1")
        class MultiAPI:
            pass

        # Register multiple instances with different ports
        services = []

        for i in range(3):
            port = 8080 + i
            instance_config = DiscoveryConfig(
                consul=config.consul,
                access=AccessConfig(host="localhost", port=port),
                ENABLE_REGISTRATION=True,  # Use the alias
            )
            service = ConsulRegistrationService(instance_config)
            services.append(service)

            await service.register_services()

        discovery = ServiceDiscovery(config)

        try:
            # Wait for service to appear
            found = await wait_for_service(discovery, "multi-api", timeout=30.0)
            assert found, "Service 'multi-api' was not discovered within timeout"

            # Discover services
            all_services = await discovery.get_services()

            # Should have 3 instances
            assert "multi-api" in all_services
            assert len(all_services["multi-api"]) == 3

            # Check all URIs
            uris = await discovery.get_all_service_uris("multi-api")
            assert len(uris) == 3
            expected_uris = {
                "http://localhost:8080/api/v1",
                "http://localhost:8081/api/v1",
                "http://localhost:8082/api/v1",
            }
            assert set(uris) == expected_uris

            # Test random selection works
            selected_uris = set()
            for _ in range(10):
                uri = await discovery.get_service_uri("multi-api")
                selected_uris.add(uri)

            # Should have selected multiple different URIs
            assert len(selected_uris) > 1

        finally:
            # Cleanup
            await discovery.close()
            for service in services:
                await service.deregister_services()
            get_service_registry().clear()

    @pytest.mark.asyncio
    async def test_service_type_filtering(self, config: DiscoveryConfig):
        """Test that only SERVICE tagged services are discovered."""
        from service_discovery import get_service_registry, register_indexer, register_worker

        # Clear registry
        get_service_registry().clear()

        # Register different service types
        @register_service("api-service", base_route="/api/v1")
        class APIService:
            pass

        @register_worker("background-worker", base_route="/api/workers/v1")
        class BackgroundWorker:
            pass

        @register_indexer("search-indexer", base_route="/api/indexers/v1")
        class SearchIndexer:
            pass

        # Create registration service and register all
        service = ConsulRegistrationService(config)
        await service.register_services()

        discovery = ServiceDiscovery(config)

        try:
            # Wait for service to appear
            found = await wait_for_service(discovery, "api-service", timeout=30.0)
            assert found, "Service 'api-service' was not discovered within timeout"

            # Discover services
            services = await discovery.get_services()

            # Should only find the SERVICE tagged one
            assert "api-service" in services
            assert "background-worker" not in services
            assert "search-indexer" not in services

        finally:
            await discovery.close()
            await service.deregister_services()
            get_service_registry().clear()

    @pytest.mark.asyncio
    async def test_service_not_found(self, config: DiscoveryConfig):
        """Test behavior when service is not found."""
        discovery = ServiceDiscovery(config)

        try:
            # Wait a moment to ensure cache is populated if any services exist
            await asyncio.sleep(0.5)

            # Try to get non-existent service
            uri = await discovery.get_service_uri("non-existent-service")
            assert uri is None

            all_uris = await discovery.get_all_service_uris("non-existent-service")
            assert all_uris == []

        finally:
            await discovery.close()

    @pytest.mark.asyncio
    async def test_discovery_with_fastapi_app(self, config: DiscoveryConfig):
        """Test service discovery with a real FastAPI app."""
        from service_discovery import get_service_registry

        # Clear registry
        get_service_registry().clear()

        # Create app with service registration
        app = FastAPI()

        @app.get("/api/v1/test")
        async def test_endpoint():
            return {"status": "ok"}

        @app.get("/health")
        async def health():
            return {"status": "healthy"}

        # Register the app as a service
        @register_service("fastapi-test-service", base_route="/api/v1")
        class FastAPIService:
            pass

        # Create lifespan context manager
        lifespan_cm = create_consul_lifespan(app, config)

        # Simulate app startup
        async with lifespan_cm:
            # Create discovery client
            discovery = ServiceDiscovery(config)

            try:
                # Wait for service to appear
                found = await wait_for_service(discovery, "fastapi-test-service", timeout=30.0)
                assert found, "Service 'fastapi-test-service' was not discovered within timeout"

                # Discover the service
                services = await discovery.get_services()
                assert "fastapi-test-service" in services

                # Get service URI
                uri = await discovery.get_service_uri("fastapi-test-service")
                assert uri == "http://localhost:8080/api/v1"

            finally:
                await discovery.close()
                get_service_registry().clear()
