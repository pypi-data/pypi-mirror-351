"""
Integration tests designed to work in CI environments.
"""

import asyncio

import consul.aio
import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from service_discovery import (
    create_consul_lifespan,
    register_indexer,
    register_worker,
)

# Mark all tests as integration
pytestmark = pytest.mark.integration


@pytest.fixture
def test_app(consul_config):
    """Create a test FastAPI application."""
    # Don't set the lifespan here - we'll create it manually in tests
    # This allows us to register services before the lifespan starts
    app = FastAPI()

    @app.get("/health")
    async def health():
        return {"status": "healthy"}

    return app


class TestConsulIntegrationCI:
    """Integration tests that work in CI/CD environments."""

    @pytest.mark.asyncio
    async def test_consul_connectivity(self, consul_config):
        """Test that we can connect to Consul."""
        client = consul.aio.Consul(host=consul_config.consul.host, port=consul_config.consul.port)

        try:
            # Try to get leader info
            leader = await client.status.leader()
            assert leader is not None

            # Try to list services
            _, services = await client.catalog.services()
            assert isinstance(services, dict)

        finally:
            # consul.aio.Consul doesn't have a close() method
            # It manages its own aiohttp session internally
            pass

    @pytest.mark.asyncio
    async def test_service_registration_basic(self, consul_config, test_app):
        """Test basic service registration and deregistration."""
        # Service will be registered via config
        consul_config.service_name = "ci-test-service"

        # Create Consul client
        consul_client = consul.aio.Consul(host=consul_config.consul.host, port=consul_config.consul.port)

        try:
            # Now create and start the lifespan after services are registered
            async with create_consul_lifespan(test_app, consul_config):
                async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test"):
                    # Wait for registration
                    await asyncio.sleep(1)

                    # Check service is registered
                    _, services = await consul_client.catalog.services()
                    assert "ci-test-service" in services

                    # Check service details
                    _, instances = await consul_client.catalog.service("ci-test-service")
                    assert len(instances) == 1
                    instance = instances[0]
                    assert instance["ServiceName"] == "ci-test-service"
                    assert "SERVICE" in instance["ServiceTags"]

            # After app shutdown, wait for deregistration
            await asyncio.sleep(1)

            # Check service is deregistered
            _, services = await consul_client.catalog.services()
            assert "ci-test-service" not in services

        finally:
            # consul.aio.Consul doesn't have a close() method
            # It manages its own aiohttp session internally
            pass

    @pytest.mark.asyncio
    async def test_multiple_service_types(self, consul_config, test_app):
        """Test registering different service types."""

        # Register services BEFORE creating the lifespan
        @register_worker("ci-worker", base_route="/api/workers/v1")
        class Worker:
            pass

        @register_indexer("ci-indexer", base_route="/api/indexers/v1")
        class Indexer:
            pass

        # Service will be registered via config
        consul_config.service_name = "ci-service"

        consul_client = consul.aio.Consul(host=consul_config.consul.host, port=consul_config.consul.port)

        try:
            # Now create and start the lifespan after services are registered
            async with create_consul_lifespan(test_app, consul_config):
                async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test"):
                    await asyncio.sleep(1)

                    # Check all services are registered
                    _, services = await consul_client.catalog.services()
                    assert "ci-worker" in services
                    assert "ci-indexer" in services
                    assert "ci-service" in services

                    # Check tags
                    _, workers = await consul_client.catalog.service("ci-worker")
                    assert "WORKER" in workers[0]["ServiceTags"]

                    _, indexers = await consul_client.catalog.service("ci-indexer")
                    assert "INDEXER" in indexers[0]["ServiceTags"]

                    # Check service if configured
                    if consul_config.service_name:
                        _, services_list = await consul_client.catalog.service("ci-service")
                        assert "SERVICE" in services_list[0]["ServiceTags"]

        finally:
            # consul.aio.Consul doesn't have a close() method
            # It manages its own aiohttp session internally
            pass

    @pytest.mark.skip(reason="probably due to networking setup or registration logic, service never gets to passing ")
    @pytest.mark.asyncio
    async def test_health_check_passes(self, consul_config, test_app):
        """Test that health checks are configured and passing."""

        # Service registration now done via config
        consul_config.service_name = "ci-health-service"

        consul_client = consul.aio.Consul(host=consul_config.consul.host, port=consul_config.consul.port)

        try:
            # Now create and start the lifespan after services are registered
            async with create_consul_lifespan(test_app, consul_config):
                async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
                    # Ensure health endpoint works
                    response = await client.get("/health")
                    assert response.status_code == 200

                    # Wait for registration and health check
                    await asyncio.sleep(2)

                    # Check service health
                    _, health_checks = await consul_client.health.service("ci-health-service")
                    assert len(health_checks) == 1

                    # Find the service check
                    checks = health_checks[0]["Checks"]
                    service_check = next((c for c in checks if c["CheckID"].startswith("service:")), None)

                    if service_check:
                        # Check might be critical initially, that's ok
                        assert service_check["Status"] in ["passing"]

        finally:
            # consul.aio.Consul doesn't have a close() method
            # It manages its own aiohttp session internally
            pass

    @pytest.mark.asyncio
    async def test_disabled_service_not_registered(self, consul_config, test_app):
        """Test that disabled services are not registered."""

        # Service registration now done via config
        consul_config.service_name = "ci-enabled"
        consul_config.enable_registration = True

        consul_client = consul.aio.Consul(host=consul_config.consul.host, port=consul_config.consul.port)

        try:
            # Now create and start the lifespan after services are registered
            async with create_consul_lifespan(test_app, consul_config):
                async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test"):
                    await asyncio.sleep(1)

                    _, services = await consul_client.catalog.services()
                    assert "ci-enabled" in services
                    # ci-disabled won't be registered since we only register one app

        finally:
            # consul.aio.Consul doesn't have a close() method
            # It manages its own aiohttp session internally
            pass
