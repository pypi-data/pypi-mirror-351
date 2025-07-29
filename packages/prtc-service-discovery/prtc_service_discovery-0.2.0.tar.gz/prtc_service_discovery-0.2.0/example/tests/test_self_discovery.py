"""
Test self-discovery functionality in the example application.

This test demonstrates that services can discover themselves after registration.
"""

import asyncio

import httpx
import pytest

from service_discovery import DiscoveryConfig, ServiceDiscovery
from service_discovery.testing import ConsulRegistrationTestBase, ConsulTestContainer, ExpectedService


class TestExampleAppSelfDiscovery(ConsulRegistrationTestBase):
    """Test that the example app can discover its own services."""

    def get_expected_services(self) -> list[ExpectedService]:
        """Define the services we expect to be registered."""
        return [
            ExpectedService.worker(
                name="pdf-processor",
                port=8000,
            ),
            ExpectedService.indexer(
                name="document-indexer",
                port=8000,
            ),
            ExpectedService.api_service(
                name="user-service",
                port=8000,
            ),
            ExpectedService.api_service(
                name="auth-service",
                port=8000,
            ),
            # Note: disabled-api should NOT be registered
        ]

    def create_app(self):
        """Import and return the example app."""
        from example.main import app

        return app

    @pytest.mark.asyncio
    async def test_self_discovery_endpoint(self, consul_container: ConsulTestContainer):
        """Test the /self-discover endpoint."""
        # Start the app with services registered
        async with self.registered_app():
            async with httpx.AsyncClient() as client:
                # Test self-discovery endpoint
                response = await client.get("http://localhost:8000/self-discover")
                assert response.status_code == 200

                data = response.json()

                # Check that our SERVICE-tagged services are discoverable
                assert "user-service" in data["self_discovery"]
                assert data["self_discovery"]["user-service"]["discoverable"] is True
                assert data["self_discovery"]["user-service"]["uri"] is not None

                assert "auth-service" in data["self_discovery"]
                assert data["self_discovery"]["auth-service"]["discoverable"] is True
                assert data["self_discovery"]["auth-service"]["uri"] is not None

    @pytest.mark.asyncio
    async def test_discover_endpoint(self, consul_container: ConsulTestContainer):
        """Test the /discover endpoint returns only SERVICE-tagged services."""
        # Start the app with services registered
        async with self.registered_app():
            async with httpx.AsyncClient() as client:
                response = await client.get("http://localhost:8000/discover")
                assert response.status_code == 200

                data = response.json()
                services = data["discovered_services"]

                # Should only discover SERVICE-tagged services
                assert "user-service" in services
                assert "auth-service" in services

                # Should NOT discover WORKER or INDEXER tagged services
                assert "pdf-processor" not in services
                assert "document-indexer" not in services

    @pytest.mark.asyncio
    async def test_discover_specific_service(self, consul_container: ConsulTestContainer):
        """Test discovering a specific service by name."""
        # Start the app with services registered
        async with self.registered_app():
            async with httpx.AsyncClient() as client:
                # Test discovering an existing service
                response = await client.get("http://localhost:8000/discover/user-service")
                assert response.status_code == 200

                data = response.json()
                assert data["available"] is True
                assert data["service_name"] == "user-service"
                assert data["instance_count"] >= 1
                assert len(data["all_uris"]) >= 1
                assert data["random_uri"] is not None

                # Test discovering a non-existent service
                response = await client.get("http://localhost:8000/discover/non-existent-service")
                assert response.status_code == 200

                data = response.json()
                assert data["available"] is False
                assert "error" in data

    @pytest.mark.asyncio
    async def test_service_discovery_integration(self, consul_container: ConsulTestContainer):
        """Test that service discovery works with our registered services."""
        # Start the app with services registered
        async with self.registered_app():
            # Create a discovery client - it will pick up env vars set by setup_consul_env
            discovery = ServiceDiscovery(DiscoveryConfig())

            try:
                # Wait a bit more for services to fully register
                await asyncio.sleep(1)

                # Discover all services
                services = await discovery.get_services()

                # Verify our SERVICE-tagged services are discoverable
                assert "user-service" in services, f"user-service not found in discovered services: {services}"
                assert "auth-service" in services, f"auth-service not found in discovered services: {services}"

                # Verify URIs are correct
                user_service_uri = await discovery.get_service_uri("user-service")
                assert user_service_uri is not None
                assert "/api/v1" in user_service_uri

                auth_service_uri = await discovery.get_service_uri("auth-service")
                assert auth_service_uri is not None
                assert "/api/auth/v1" in auth_service_uri

                # Verify WORKER/INDEXER services are not in the SERVICE discovery
                assert "pdf-processor" not in services
                assert "document-indexer" not in services

            finally:
                await discovery.close()

    @pytest.mark.asyncio
    async def test_registered_services_endpoint(self, consul_container: ConsulTestContainer):
        """Test the /services endpoint shows all registered services."""
        # Start the app with services registered
        async with self.registered_app():
            async with httpx.AsyncClient() as client:
                response = await client.get("http://localhost:8000/services")
                assert response.status_code == 200

                data = response.json()
                services = data["registered_services"]

                # Map services by name for easier checking
                service_by_name = {s["name"]: s for s in services}

                # All services should be in the registry (including disabled)
                assert "pdf-processor" in service_by_name
                assert "document-indexer" in service_by_name
                assert "user-service" in service_by_name
                assert "auth-service" in service_by_name
                assert "disabled-service" in service_by_name

                # Check enabled status
                assert service_by_name["pdf-processor"]["enabled"] is True
                assert service_by_name["document-indexer"]["enabled"] is True
                assert service_by_name["user-service"]["enabled"] is True
                assert service_by_name["auth-service"]["enabled"] is True
                assert service_by_name["disabled-service"]["enabled"] is False

                # Check service types
                assert service_by_name["pdf-processor"]["type"] == "WORKER"
                assert service_by_name["document-indexer"]["type"] == "INDEXER"
                assert service_by_name["user-service"]["type"] == "SERVICE"
                assert service_by_name["auth-service"]["type"] == "SERVICE"
                assert service_by_name["disabled-service"]["type"] == "SERVICE"
