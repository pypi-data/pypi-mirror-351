"""
Unit tests for ApplicationRegistration class.
"""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from service_discovery import ApplicationRegistration, DiscoveryConfig
from service_discovery.models import ServiceType


@pytest.mark.asyncio
class TestApplicationRegistration:
    """Tests for ApplicationRegistration class."""

    @pytest.fixture
    def mock_config(self):
        """Create a mock DiscoveryConfig."""
        config = Mock(spec=DiscoveryConfig)

        # Create nested mocks for consul and access
        config.consul = Mock()
        config.consul.host = "localhost"
        config.consul.port = 8500

        config.access = Mock()
        config.access.host = "app-host"
        config.access.port = 8080

        config.enable_registration = True
        config.get_health_host = Mock(return_value="app-host")
        config.get_health_port = Mock(return_value=8080)
        config.is_valid_for_registration = Mock(return_value=True)
        return config

    @pytest.fixture
    def app_registration(self, mock_config):
        """Create an ApplicationRegistration instance with mocked config."""
        with patch("service_discovery.application_registration.DiscoveryConfig", return_value=mock_config):
            return ApplicationRegistration(mock_config)

    async def test_register_application_success(self, app_registration, mock_config):
        """Test successful application registration."""
        # Mock Consul client
        mock_consul = AsyncMock()
        mock_consul.agent.service.register = AsyncMock(return_value=True)

        with patch("service_discovery.application_registration.consul.aio.Consul", return_value=mock_consul):
            await app_registration.register_application("test-app")

            # Verify Consul registration was called
            mock_consul.agent.service.register.assert_called_once()
            call_args = mock_consul.agent.service.register.call_args

            # Check registration parameters
            assert call_args.kwargs["name"] == "test-app"
            assert call_args.kwargs["address"] == "app-host"
            assert call_args.kwargs["port"] == 8080
            assert ServiceType.SERVICE.value in call_args.kwargs["tags"]
            assert call_args.kwargs["meta"] == {}  # No base_route for services

            # Check service ID was stored
            assert app_registration._current_service_id is not None
            assert app_registration._current_service_id.startswith("test-app:")

    async def test_register_application_custom_health_endpoint(self, app_registration, mock_config):
        """Test registration with custom health endpoint."""
        mock_consul = AsyncMock()
        mock_consul.agent.service.register = AsyncMock(return_value=True)

        with patch("service_discovery.application_registration.consul.aio.Consul", return_value=mock_consul):
            await app_registration.register_application("test-app", "/custom/health")

            # Check health check URL
            call_args = mock_consul.agent.service.register.call_args
            check = call_args.kwargs["check"]
            # The check is a dictionary when passed to consul
            assert isinstance(check, dict)
            assert check["http"] == "http://app-host:8080/custom/health"

    async def test_register_application_disabled(self, mock_config):
        """Test registration when disabled in config."""
        mock_config.enable_registration = False
        app_registration = ApplicationRegistration(mock_config)

        mock_consul = AsyncMock()
        with patch("service_discovery.application_registration.consul.aio.Consul", return_value=mock_consul):
            await app_registration.register_application("test-app")

            # Should not attempt to register
            mock_consul.agent.service.register.assert_not_called()

    async def test_register_application_empty_name(self, app_registration):
        """Test registration with empty application name."""
        with pytest.raises(ValueError, match="Application name cannot be null or empty"):
            await app_registration.register_application("")

        with pytest.raises(ValueError, match="Application name cannot be null or empty"):
            await app_registration.register_application("   ")

    async def test_register_application_invalid_config(self, app_registration, mock_config):
        """Test registration with invalid configuration."""
        mock_config.is_valid_for_registration.return_value = False

        with pytest.raises(ValueError, match="Invalid configuration for registration"):
            await app_registration.register_application("test-app")

    async def test_register_application_consul_failure(self, app_registration, mock_config):
        """Test registration when Consul returns False."""
        mock_consul = AsyncMock()
        mock_consul.agent.service.register = AsyncMock(return_value=False)

        with patch("service_discovery.application_registration.consul.aio.Consul", return_value=mock_consul):
            with pytest.raises(Exception, match="Consul registration returned False"):
                await app_registration.register_application("test-app")

    async def test_deregister_application_success(self, app_registration, mock_config):
        """Test successful application deregistration."""
        # First register
        mock_consul = AsyncMock()
        mock_consul.agent.service.register = AsyncMock(return_value=True)
        mock_consul.agent.service.deregister = AsyncMock(return_value=True)

        with patch("service_discovery.application_registration.consul.aio.Consul", return_value=mock_consul):
            await app_registration.register_application("test-app")
            service_id = app_registration._current_service_id

            # Then deregister
            await app_registration.deregister_application("test-app")

            # Verify deregistration was called with correct ID
            mock_consul.agent.service.deregister.assert_called_once_with(service_id=service_id)
            assert app_registration._current_service_id is None

    async def test_deregister_application_no_service_id(self, app_registration):
        """Test deregistration when no service was registered."""
        mock_consul = AsyncMock()

        with patch("service_discovery.application_registration.consul.aio.Consul", return_value=mock_consul):
            # Should not raise error
            await app_registration.deregister_application("test-app")

            # Should not attempt to deregister
            mock_consul.agent.service.deregister.assert_not_called()

    async def test_deregister_application_disabled(self, app_registration, mock_config):
        """Test deregistration when disabled in config."""
        mock_config.enable_registration = False

        mock_consul = AsyncMock()
        with patch("service_discovery.application_registration.consul.aio.Consul", return_value=mock_consul):
            await app_registration.deregister_application("test-app")

            # Should not attempt to deregister
            mock_consul.agent.service.deregister.assert_not_called()

    async def test_health_config_fallback(self, mock_config):
        """Test health config falls back to access config."""
        # No health config specified
        mock_config.get_health_host.return_value = None
        mock_config.get_health_port.return_value = None
        mock_config.health = None

        app_registration = ApplicationRegistration(mock_config)

        mock_consul = AsyncMock()
        mock_consul.agent.service.register = AsyncMock(return_value=True)

        with patch("service_discovery.application_registration.consul.aio.Consul", return_value=mock_consul):
            await app_registration.register_application("test-app")

            # Should use access config for health checks
            call_args = mock_consul.agent.service.register.call_args
            assert call_args.kwargs["address"] == "app-host"
            assert call_args.kwargs["port"] == 8080
