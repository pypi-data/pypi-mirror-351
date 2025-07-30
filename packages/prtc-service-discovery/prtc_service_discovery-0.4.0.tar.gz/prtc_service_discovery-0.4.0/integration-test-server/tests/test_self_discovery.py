"""
Test self-discovery functionality in the integration test server.

This test demonstrates that services can discover themselves after registration.
"""

import asyncio
import os
import sys
from pathlib import Path

# Fix import paths when running from integration-test-server directory
# Add the integration-test-server directory to path for local imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Add the src directory to path for service_discovery imports
# When running from integration-test-server, we need to go up two levels to find src
project_root = Path(__file__).parent.parent.parent
src_path = project_root / "src"
if src_path.exists():
    sys.path.insert(0, str(src_path))

import httpx  # noqa: E402
import pytest  # noqa: E402

from service_discovery import DiscoveryConfig, ServiceDiscovery  # noqa: E402
from service_discovery.testing import ConsulRegistrationTestBase, ConsulTestContainer, ExpectedService  # noqa: E402


class TestIntegrationServerSelfDiscovery(ConsulRegistrationTestBase):
    """Test that the integration test server can discover its own services."""

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
                name="integration-test-server",
                port=8000,
            ),
        ]

    def create_app(self):
        """Import and return the integration test server app."""
        # Set SERVICE_NAME for automatic registration
        os.environ["SERVICE_NAME"] = "integration-test-server"

        from main import app

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

                # Check that our application service is discoverable
                assert "integration-test-server" in data["self_discovery"]
                assert data["self_discovery"]["integration-test-server"]["discoverable"] is True
                assert data["self_discovery"]["integration-test-server"]["uri"] is not None

                # Check workers/indexers
                assert "pdf-processor" in data["self_discovery"]
                assert data["self_discovery"]["pdf-processor"]["discoverable"] is True

                assert "document-indexer" in data["self_discovery"]
                assert data["self_discovery"]["document-indexer"]["discoverable"] is True

    @pytest.mark.asyncio
    async def test_discover_endpoint(self, consul_container: ConsulTestContainer):
        """Test the /discover endpoint returns all service types."""
        # Start the app with services registered
        async with self.registered_app():
            async with httpx.AsyncClient() as client:
                response = await client.get("http://localhost:8000/discover")
                assert response.status_code == 200

                data = response.json()
                services = data["discovered_services"]

                # Should discover the application service
                assert "integration-test-server" in services

                # Should also discover workers and indexers now
                assert "pdf-processor" in services
                assert "document-indexer" in services

    @pytest.mark.asyncio
    async def test_discover_specific_service(self, consul_container: ConsulTestContainer):
        """Test discovering a specific service by name."""
        # Start the app with services registered
        async with self.registered_app():
            async with httpx.AsyncClient() as client:
                # Test discovering the application service
                response = await client.get("http://localhost:8000/discover/integration-test-server")
                assert response.status_code == 200

                data = response.json()
                assert data["available"] is True
                assert data["service_name"] == "integration-test-server"
                assert data["instance_count"] >= 1
                assert len(data["all_uris"]) >= 1
                assert data["random_uri"] is not None
                # Application services should not have base routes
                assert not data["random_uri"].endswith("/api/v1")

                # Test discovering a worker
                response = await client.get("http://localhost:8000/discover/pdf-processor")
                assert response.status_code == 200

                data = response.json()
                assert data["available"] is True
                # Workers should include base routes
                assert "/api/workers/v1" in data["random_uri"]

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

                # Verify our application service is discoverable
                assert (
                    "integration-test-server" in services
                ), f"integration-test-server not found in discovered services: {services}"

                # Verify workers and indexers are also discoverable
                assert "pdf-processor" in services
                assert "document-indexer" in services

                # Verify URIs are correct
                app_uri = await discovery.get_service_uri("integration-test-server")
                assert app_uri is not None
                # Application service should not have a base route
                assert app_uri.endswith(":8000")

                worker_uri = await discovery.get_service_uri("pdf-processor")
                assert worker_uri is not None
                assert "/api/workers/v1" in worker_uri

                indexer_uri = await discovery.get_service_uri("document-indexer")
                assert indexer_uri is not None
                assert "/api/indexers/v1" in indexer_uri

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

                # Only workers/indexers should be in the decorator registry
                assert "pdf-processor" in service_by_name
                assert "document-indexer" in service_by_name

                # Check enabled status
                assert service_by_name["pdf-processor"]["enabled"] is True
                assert service_by_name["document-indexer"]["enabled"] is True

                # Check service types
                assert service_by_name["pdf-processor"]["type"] == "WORKER"
                assert service_by_name["document-indexer"]["type"] == "INDEXER"

    @pytest.mark.asyncio
    async def test_service_discovery_with_api_client(self, consul_container: ConsulTestContainer):
        """Test making actual API calls to discovered services."""
        # Start the app with services registered
        async with self.registered_app():
            # Create a discovery client
            discovery = ServiceDiscovery(DiscoveryConfig())

            try:
                # Wait for registration
                await asyncio.sleep(1)

                # Discover the application service
                app_uri = await discovery.get_service_uri("integration-test-server")
                assert app_uri is not None

                # Make an API call to the user endpoint
                async with httpx.AsyncClient() as client:
                    response = await client.get(f"{app_uri}/api/v1/users")
                    assert response.status_code == 200
                    data = response.json()
                    assert "users" in data
                    assert len(data["users"]) > 0

                    # Make an API call to auth endpoint
                    response = await client.post(
                        f"{app_uri}/api/auth/v1/login", params={"username": "admin", "password": "secret"}
                    )
                    assert response.status_code == 200
                    data = response.json()
                    assert "token" in data

            finally:
                await discovery.close()
