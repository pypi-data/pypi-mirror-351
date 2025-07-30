"""
Service discovery functionality for Consul-registered services.

This module provides utilities to discover services registered in Consul,
similar to the Java ServiceDiscovery interface.
"""

import asyncio
import random

from consul.aio import Consul

from .config import DiscoveryConfig
from .models import ServiceType


class ServiceDiscovery:
    """
    Service discovery client for finding services registered in Consul.

    This class provides methods to discover services by type (SERVICE, WORKER, INDEXER)
    and get their URIs. Unlike the Java version which uses Stork for load balancing,
    this implementation provides simple random selection for load balancing.
    """

    def __init__(self, config: DiscoveryConfig | None = None):
        """
        Initialize the service discovery client.

        Args:
            config: Optional discovery configuration. If not provided,
                    will use environment variables.
        """
        self.config = config or DiscoveryConfig()
        self.consul_config = self.config.consul
        self._consul_client: Consul | None = None
        self._service_cache: dict[str, list[str]] = {}
        self._last_refresh: float = 0
        self._refresh_interval: float = 30.0  # seconds

    async def _get_consul_client(self) -> Consul:
        """Get or create the Consul client."""
        if self._consul_client is None:
            self._consul_client = Consul(
                host=self.consul_config.host,
                port=self.consul_config.port,
            )
        return self._consul_client

    async def _refresh_services(self) -> None:
        """Refresh the service cache from Consul if needed."""
        current_time = asyncio.get_event_loop().time()
        if current_time - self._last_refresh < self._refresh_interval:
            return

        try:
            consul = await self._get_consul_client()

            # Get all services from Consul
            _, services = await consul.catalog.services()

            # Clear the cache
            self._service_cache.clear()

            # For each service, get its details
            for service_name in services:
                _, service_nodes = await consul.catalog.service(service_name)

                for node in service_nodes:
                    # Check service tags to determine type
                    tags = node.get("ServiceTags", [])

                    # Only process services with SERVICE tag (not WORKER or INDEXER)
                    if ServiceType.SERVICE.value in tags:
                        # Build the URI from service metadata
                        address = node.get("ServiceAddress", "")
                        port = node.get("ServicePort", 0)
                        meta = node.get("ServiceMeta", {})
                        base_route = meta.get("base_route", "")

                        if address and port:
                            # Store URI with service name as key
                            uri = f"http://{address}:{port}{base_route}"
                            if service_name not in self._service_cache:
                                self._service_cache[service_name] = []
                            self._service_cache[service_name].append(uri)

            self._last_refresh = current_time

        except Exception as e:
            # Log error but don't crash - use cached values
            print(f"Error refreshing services from Consul: {e}")

    async def get_services(self) -> dict[str, list[str]]:
        """
        Get all available services with their URIs.

        Returns:
            Dictionary mapping service names to lists of URIs.
            Only includes services tagged with SERVICE.
        """
        await self._refresh_services()
        return self._service_cache.copy()

    async def get_service_uri(self, service_name: str) -> str | None:
        """
        Get a random URI for a specific service (simulating load balancing).

        Args:
            service_name: Name of the service to look up

        Returns:
            A randomly selected URI for the service, or None if not found
        """
        await self._refresh_services()

        uris = self._service_cache.get(service_name, [])
        if not uris:
            return None

        # Simple random selection for load balancing
        return random.choice(uris)

    async def get_all_service_uris(self, service_name: str) -> list[str]:
        """
        Get all URIs for a specific service.

        Args:
            service_name: Name of the service to look up

        Returns:
            List of all URIs for the service
        """
        await self._refresh_services()
        return self._service_cache.get(service_name, []).copy()

    async def close(self) -> None:
        """Close the Consul client connection."""
        # python-consul2 doesn't have a close method
        self._consul_client = None


# Convenience function for creating a service discovery instance
def create_service_discovery(config: DiscoveryConfig | None = None) -> ServiceDiscovery:
    """
    Create a ServiceDiscovery instance.

    Args:
        config: Optional discovery configuration

    Returns:
        Configured ServiceDiscovery instance
    """
    return ServiceDiscovery(config)
