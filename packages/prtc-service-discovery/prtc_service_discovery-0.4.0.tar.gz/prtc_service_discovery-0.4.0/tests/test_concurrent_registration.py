"""
Tests for concurrent service registration to detect race conditions.
"""

import asyncio
import os

import pytest

from service_discovery import DiscoveryConfig
from service_discovery.config import AccessConfig, ConsulConfig, HealthConfig

# Import the consul_container fixture if not in CI
if not os.environ.get("CI"):
    from tests.test_integration import consul_container  # noqa: F401


@pytest.fixture
def consul_config(request):
    """Create Consul configuration for tests."""
    if os.environ.get("CI"):
        # In CI, use localhost:8500
        return DiscoveryConfig(
            consul=ConsulConfig(
                host=os.environ.get("CONSUL_HOST", "localhost"),
                port=int(os.environ.get("CONSUL_PORT", "8500")),
            ),
            access=AccessConfig(host="localhost", port=8000),
            health=HealthConfig(host="localhost", port=8000),
            ENABLE_REGISTRATION=True,
        )
    else:
        # For local tests, use the consul_container fixture
        consul_container = request.getfixturevalue("consul_container")
        return DiscoveryConfig(
            consul=ConsulConfig(
                host=consul_container.get_consul_host(),
                port=consul_container.get_consul_port(),
            ),
            access=AccessConfig(host="localhost", port=8000),
            health=HealthConfig(host="localhost", port=8000),
            ENABLE_REGISTRATION=True,
        )


@pytest.mark.integration
class TestConcurrentRegistration:
    """Test concurrent registration scenarios."""

    @pytest.mark.asyncio
    async def test_concurrent_application_registration(self, consul_config):
        """Test multiple applications registering concurrently."""
        from service_discovery import ApplicationRegistration

        # Create multiple application registrations
        registrations = []
        for i in range(10):
            reg = ApplicationRegistration(consul_config)
            registrations.append((reg, f"concurrent-app-{i}"))

        # Register all applications concurrently
        tasks = []
        for reg, app_name in registrations:
            tasks.append(asyncio.create_task(reg.register_application(app_name)))

        # Wait for all to complete
        await asyncio.gather(*tasks)

        # Verify all applications are registered
        from consul.aio import Consul

        consul_client = Consul(host=consul_config.consul.host, port=consul_config.consul.port)
        services = await consul_client.agent.services()

        # Count how many of our apps are registered
        app_names = {f"concurrent-app-{i}" for i in range(10)}
        registered_apps = {s.get("Service") for s in services.values() if s.get("Service") in app_names}
        assert len(registered_apps) == 10, f"Expected 10 apps, found {len(registered_apps)}"

        # Clean up
        for reg, app_name in registrations:
            await reg.deregister_application(app_name)

    @pytest.mark.asyncio
    async def test_concurrent_same_application_registration(self, consul_config):
        """Test the same application being registered multiple times concurrently."""
        from service_discovery import ApplicationRegistration

        # Create multiple instances trying to register the same app
        registrations = [ApplicationRegistration(consul_config) for _ in range(10)]

        # Try to register the same application multiple times concurrently
        async def register(reg):
            try:
                await reg.register_application("duplicate-app")
                return True
            except Exception:
                return False

        # Run concurrent registrations
        tasks = [asyncio.create_task(register(reg)) for reg in registrations]
        results = await asyncio.gather(*tasks)

        # All should succeed (multiple instances can register same app name)
        assert all(results), "All registrations should succeed"

        # Verify the application is registered in Consul
        from consul.aio import Consul

        consul_client = Consul(host=consul_config.consul.host, port=consul_config.consul.port)
        services = await consul_client.agent.services()

        # Should have multiple instances of the same service
        duplicate_instances = [s for s in services.values() if s.get("Service") == "duplicate-app"]
        assert len(duplicate_instances) >= 1, "At least one instance should be registered"

        # Clean up
        for reg in registrations:
            await reg.deregister_application("duplicate-app")

    @pytest.mark.asyncio
    async def test_registration_deregistration_race(self, consul_config):
        """Test race condition between registration and deregistration."""
        from service_discovery import ApplicationRegistration

        reg = ApplicationRegistration(consul_config)

        # Start registration
        reg_task = asyncio.create_task(reg.register_application("race-app"))

        # Give registration a tiny head start to increase chance of race
        await asyncio.sleep(0.01)

        # Try to deregister while registration might be in progress
        dereg_task = asyncio.create_task(reg.deregister_application("race-app"))

        # Wait for both
        reg_result, dereg_result = await asyncio.gather(reg_task, dereg_task, return_exceptions=True)

        # The service should handle this gracefully without exceptions
        if isinstance(reg_result, Exception):
            pytest.fail(f"Registration failed with: {reg_result}")
        if isinstance(dereg_result, Exception):
            pytest.fail(f"Deregistration failed with: {dereg_result}")

        # Since we have a race condition, the service might still be registered
        # This is expected behavior - deregister only removes services it knows about
        # at the time it runs. If registration completes after deregistration starts,
        # the service will remain registered.

        # To properly clean up, we need to deregister again
        await reg.deregister_application("race-app")

        # Now verify no services remain in Consul
        await asyncio.sleep(0.5)  # Give Consul time to update

        from consul.aio import Consul

        consul_client = Consul(host=consul_config.consul.host, port=consul_config.consul.port)
        services = await consul_client.agent.services()
        assert "race-app" not in [s.get("Service") for s in services.values()]
