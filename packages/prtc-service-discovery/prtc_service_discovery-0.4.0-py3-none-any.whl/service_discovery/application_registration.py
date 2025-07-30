"""
Programmatic API for registering applications with Consul service discovery.

This module provides a simple way to register an entire application as a single
service in Consul, rather than registering individual controllers or resources.
"""

import logging
import uuid

import consul.aio

from .config import DiscoveryConfig
from .models import ServiceType

logger = logging.getLogger(__name__)


class ApplicationRegistration:
    """
    Programmatic API for registering applications with Consul service discovery.

    This service provides a simple way to register an entire application as a single
    service in Consul, rather than registering individual controllers or resources.
    Applications should call register_application() once during startup.

    Usage Example:
        ```python
        from service_discovery import ApplicationRegistration

        async def startup():
            registration = ApplicationRegistration()
            await registration.register_application("perceptic-core")
        ```

    Service Discovery:
        Once registered, clients can discover your application using:
        ```python
        discovery = create_service_discovery()
        uri = await discovery.get_service_uri("perceptic-core")
        ```
    """

    def __init__(self, config: DiscoveryConfig | None = None):
        """
        Initialize the application registration service.

        Args:
            config: Discovery configuration. If None, will be loaded from environment.
        """
        self.config = config or DiscoveryConfig()
        self._consul_client: consul.aio.Consul | None = None
        self._current_service_id: str | None = None

    async def _get_consul_client(self) -> consul.aio.Consul:
        """Get or create the Consul client."""
        if self._consul_client is None:
            self._consul_client = consul.aio.Consul(
                host=self.config.consul.host,
                port=self.config.consul.port,
            )
        return self._consul_client

    async def register_application(self, application_name: str, health_endpoint: str = "/health") -> None:
        """
        Register the application with Consul using the specified health check endpoint.

        This method should be called once during application startup. It registers
        the entire application as a single service in Consul with a health check
        at the specified endpoint.

        Args:
            application_name: The name of the application (e.g., "perceptic-core")
            health_endpoint: The health check endpoint path (default: "/health")

        Raises:
            ValueError: If application name is empty or registration config is invalid
            Exception: If Consul registration fails
        """
        if not self.config.enable_registration:
            logger.info("Service registration is disabled")
            return

        if not application_name or not application_name.strip():
            raise ValueError("Application name cannot be null or empty")

        if not self.config.is_valid_for_registration():
            raise ValueError(
                "Invalid configuration for registration. "
                f"Consul host: {self.config.consul.host}, "
                f"Access host: {self.config.access.host}, "
                f"Access port: {self.config.access.port}"
            )

        try:
            client = await self._get_consul_client()

            # Generate service ID
            self._current_service_id = f"{application_name}:{uuid.uuid4()}"

            # Get networking config
            access_host = self.config.access.host or "localhost"
            access_port = self.config.access.port or 8000
            health_host = self.config.get_health_host() or access_host
            health_port = self.config.get_health_port() or access_port

            # Build health check URL
            health_url = f"http://{health_host}:{health_port}{health_endpoint}"

            # Register with Consul
            success = await client.agent.service.register(
                name=application_name,
                service_id=self._current_service_id,
                address=access_host,
                port=access_port,
                tags=[ServiceType.SERVICE.value],
                # No base_route metadata for services
                meta={},
                check=consul.Check.http(
                    url=health_url,
                    interval="15s",
                    timeout="10s",
                    deregister="1m",
                ),
            )

            if success:
                logger.info(
                    f"Successfully registered application '{application_name}' with Consul "
                    f"(ID: {self._current_service_id}, Address: {access_host}:{access_port})"
                )
            else:
                raise Exception("Consul registration returned False")

        except Exception as e:
            logger.error(f"Failed to register application with Consul: {e}")
            raise

    async def deregister_application(self, application_name: str) -> None:
        """
        Deregister the application from Consul.

        This method should be called during application shutdown to cleanly remove
        the service registration from Consul. If not called, Consul will eventually
        remove the registration after health checks fail.

        Args:
            application_name: The name of the application to deregister
        """
        if not self.config.enable_registration:
            return

        if not self._current_service_id:
            logger.warning(f"No service ID found for application '{application_name}', " "skipping deregistration")
            return

        try:
            client = await self._get_consul_client()
            success = await client.agent.service.deregister(service_id=self._current_service_id)

            if success:
                logger.info(
                    f"Successfully deregistered application '{application_name}' "
                    f"from Consul (ID: {self._current_service_id})"
                )
            else:
                logger.warning(f"Failed to deregister application '{application_name}' - " "Consul returned False")

            self._current_service_id = None

        except Exception as e:
            logger.warning(f"Failed to deregister application '{application_name}' " f"from Consul: {e}")

    async def close(self) -> None:
        """Close the Consul client connection."""
        self._consul_client = None
