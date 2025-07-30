"""
Tests for service discovery functionality.
"""

from unittest.mock import AsyncMock, patch

from service_discovery import ServiceDiscovery, create_service_discovery
from service_discovery.config import ConsulConfig, DiscoveryConfig
from service_discovery.models import ServiceType


class TestServiceDiscovery:
    """Test the ServiceDiscovery class."""

    def test_create_service_discovery(self):
        """Test creating a service discovery instance."""
        discovery = create_service_discovery()
        assert isinstance(discovery, ServiceDiscovery)
        assert discovery.config is not None

    def test_create_service_discovery_with_config(self):
        """Test creating a service discovery instance with custom config."""
        config = DiscoveryConfig(consul=ConsulConfig(host="custom-host", port=9999))
        discovery = create_service_discovery(config)
        assert discovery.config == config
        assert discovery.consul_config.host == "custom-host"
        assert discovery.consul_config.port == 9999

    @patch("service_discovery.service_discovery.Consul")
    async def test_get_services_empty(self, mock_consul_class):
        """Test getting services when none are registered."""
        # Mock Consul client
        mock_consul = AsyncMock()
        mock_consul_class.return_value = mock_consul

        # Mock empty service list
        mock_consul.catalog.services = AsyncMock(return_value=(None, {}))

        discovery = ServiceDiscovery()
        services = await discovery.get_services()

        assert services == {}
        mock_consul.catalog.services.assert_called_once()

    @patch("service_discovery.service_discovery.Consul")
    async def test_get_services_with_service_tag(self, mock_consul_class):
        """Test getting services that are tagged with SERVICE."""
        # Mock Consul client
        mock_consul = AsyncMock()
        mock_consul_class.return_value = mock_consul

        # Mock service list
        mock_consul.catalog.services = AsyncMock(return_value=(None, {"user-api": [], "worker-service": []}))

        # Mock service details
        user_api_nodes = [
            {
                "ServiceAddress": "10.0.0.1",
                "ServicePort": 8080,
                "ServiceTags": [ServiceType.SERVICE.value],
                "ServiceMeta": {"base_route": "/api/v1"},
            },
            {
                "ServiceAddress": "10.0.0.2",
                "ServicePort": 8080,
                "ServiceTags": [ServiceType.SERVICE.value],
                "ServiceMeta": {"base_route": "/api/v1"},
            },
        ]

        worker_nodes = [
            {
                "ServiceAddress": "10.0.0.3",
                "ServicePort": 8081,
                "ServiceTags": [ServiceType.WORKER.value],
                "ServiceMeta": {"base_route": "/api/workers/v1"},
            }
        ]

        mock_consul.catalog.service = AsyncMock(
            side_effect=[
                (None, user_api_nodes),
                (None, worker_nodes),
            ]
        )

        discovery = ServiceDiscovery()
        services = await discovery.get_services()

        # Should only include user-api (has SERVICE tag)
        assert "user-api" in services
        assert len(services["user-api"]) == 2
        assert "http://10.0.0.1:8080/api/v1" in services["user-api"]
        assert "http://10.0.0.2:8080/api/v1" in services["user-api"]

        # Should not include worker-service (has WORKER tag)
        assert "worker-service" not in services

    @patch("service_discovery.service_discovery.Consul")
    async def test_get_service_uri_single(self, mock_consul_class):
        """Test getting a URI for a service with single instance."""
        # Mock Consul client
        mock_consul = AsyncMock()
        mock_consul_class.return_value = mock_consul

        # Mock service list
        mock_consul.catalog.services = AsyncMock(return_value=(None, {"user-api": []}))

        # Mock service details
        service_nodes = [
            {
                "ServiceAddress": "10.0.0.1",
                "ServicePort": 8080,
                "ServiceTags": [ServiceType.SERVICE.value],
                "ServiceMeta": {"base_route": "/api/v1"},
            }
        ]

        mock_consul.catalog.service = AsyncMock(return_value=(None, service_nodes))

        discovery = ServiceDiscovery()
        uri = await discovery.get_service_uri("user-api")

        assert uri == "http://10.0.0.1:8080/api/v1"

    @patch("service_discovery.service_discovery.Consul")
    @patch("service_discovery.service_discovery.random.choice")
    async def test_get_service_uri_multiple(self, mock_choice, mock_consul_class):
        """Test getting a URI for a service with multiple instances."""
        # Mock Consul client
        mock_consul = AsyncMock()
        mock_consul_class.return_value = mock_consul

        # Mock service list
        mock_consul.catalog.services = AsyncMock(return_value=(None, {"user-api": []}))

        # Mock service details
        service_nodes = [
            {
                "ServiceAddress": "10.0.0.1",
                "ServicePort": 8080,
                "ServiceTags": [ServiceType.SERVICE.value],
                "ServiceMeta": {"base_route": "/api/v1"},
            },
            {
                "ServiceAddress": "10.0.0.2",
                "ServicePort": 8080,
                "ServiceTags": [ServiceType.SERVICE.value],
                "ServiceMeta": {"base_route": "/api/v1"},
            },
        ]

        mock_consul.catalog.service = AsyncMock(return_value=(None, service_nodes))

        # Mock random choice to return second instance
        mock_choice.return_value = "http://10.0.0.2:8080/api/v1"

        discovery = ServiceDiscovery()
        uri = await discovery.get_service_uri("user-api")

        assert uri == "http://10.0.0.2:8080/api/v1"
        mock_choice.assert_called_once()

    @patch("service_discovery.service_discovery.Consul")
    async def test_get_service_uri_not_found(self, mock_consul_class):
        """Test getting a URI for a non-existent service."""
        # Mock Consul client
        mock_consul = AsyncMock()
        mock_consul_class.return_value = mock_consul

        # Mock empty service list
        mock_consul.catalog.services = AsyncMock(return_value=(None, {}))

        discovery = ServiceDiscovery()
        uri = await discovery.get_service_uri("non-existent")

        assert uri is None

    @patch("service_discovery.service_discovery.Consul")
    async def test_get_all_service_uris(self, mock_consul_class):
        """Test getting all URIs for a service."""
        # Mock Consul client
        mock_consul = AsyncMock()
        mock_consul_class.return_value = mock_consul

        # Mock service list
        mock_consul.catalog.services = AsyncMock(return_value=(None, {"user-api": []}))

        # Mock service details
        service_nodes = [
            {
                "ServiceAddress": "10.0.0.1",
                "ServicePort": 8080,
                "ServiceTags": [ServiceType.SERVICE.value],
                "ServiceMeta": {"base_route": "/api/v1"},
            },
            {
                "ServiceAddress": "10.0.0.2",
                "ServicePort": 8080,
                "ServiceTags": [ServiceType.SERVICE.value],
                "ServiceMeta": {"base_route": "/api/v1"},
            },
        ]

        mock_consul.catalog.service = AsyncMock(return_value=(None, service_nodes))

        discovery = ServiceDiscovery()
        uris = await discovery.get_all_service_uris("user-api")

        assert len(uris) == 2
        assert "http://10.0.0.1:8080/api/v1" in uris
        assert "http://10.0.0.2:8080/api/v1" in uris

    @patch("service_discovery.service_discovery.Consul")
    async def test_caching_behavior(self, mock_consul_class):
        """Test that services are cached and not fetched on every call."""
        # Mock Consul client
        mock_consul = AsyncMock()
        mock_consul_class.return_value = mock_consul

        # Mock service list
        mock_consul.catalog.services = AsyncMock(return_value=(None, {"user-api": []}))

        # Mock service details
        service_nodes = [
            {
                "ServiceAddress": "10.0.0.1",
                "ServicePort": 8080,
                "ServiceTags": [ServiceType.SERVICE.value],
                "ServiceMeta": {"base_route": "/api/v1"},
            }
        ]

        mock_consul.catalog.service = AsyncMock(return_value=(None, service_nodes))

        discovery = ServiceDiscovery()

        # First call should fetch from Consul
        services1 = await discovery.get_services()
        assert mock_consul.catalog.services.call_count == 1

        # Second call within refresh interval should use cache
        services2 = await discovery.get_services()
        assert mock_consul.catalog.services.call_count == 1
        assert services1 == services2

    @patch("service_discovery.service_discovery.Consul")
    async def test_error_handling(self, mock_consul_class):
        """Test that errors are handled gracefully."""
        # Mock Consul client
        mock_consul = AsyncMock()
        mock_consul_class.return_value = mock_consul

        # Mock service list to raise exception
        mock_consul.catalog.services = AsyncMock(side_effect=Exception("Connection error"))

        discovery = ServiceDiscovery()

        # Should not raise exception, just return empty dict
        services = await discovery.get_services()
        assert services == {}

    @patch("service_discovery.service_discovery.Consul")
    async def test_close(self, mock_consul_class):
        """Test closing the Consul client."""
        # Mock Consul client
        mock_consul = AsyncMock()
        mock_consul_class.return_value = mock_consul

        discovery = ServiceDiscovery()

        # Force client creation
        await discovery._get_consul_client()
        assert discovery._consul_client is not None

        # Close should cleanup
        await discovery.close()
        assert discovery._consul_client is None
        # python-consul2 doesn't have a close method
