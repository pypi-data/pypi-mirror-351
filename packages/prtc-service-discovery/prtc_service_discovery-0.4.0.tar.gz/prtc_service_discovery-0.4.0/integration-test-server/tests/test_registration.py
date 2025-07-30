"""
Test the integration test server's Consul registration using the testing library.

This demonstrates how consumers of service-discovery-python can use the
testing library to verify their service registrations.
"""

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

from fastapi import FastAPI  # noqa: E402

from service_discovery.testing import ConsulRegistrationTestBase, ExpectedService  # noqa: E402


class TestIntegrationServerRegistration(ConsulRegistrationTestBase):
    """Test that the integration test server correctly registers all its services."""

    def get_expected_services(self) -> list[ExpectedService]:
        """Define the services we expect to be registered."""
        return [
            # Worker service
            ExpectedService.worker(
                name="pdf-processor",
                port=8000,
            ),
            # Indexer service
            ExpectedService.indexer(
                name="document-indexer",
                port=8000,
            ),
            # Application service (registered via SERVICE_NAME config)
            ExpectedService.api_service(
                name="integration-test-server",
                port=8000,
                tags={"SERVICE"},
            ),
        ]

    def create_app(self) -> FastAPI:
        """Create the integration test server FastAPI application."""
        # Set SERVICE_NAME for automatic registration
        os.environ["SERVICE_NAME"] = "integration-test-server"

        # Import here to ensure services are registered
        from main import app

        return app


class TestWorkerOnlyRegistration(ConsulRegistrationTestBase):
    """Test registration when only workers/indexers are present (no SERVICE_NAME)."""

    def get_expected_services(self) -> list[ExpectedService]:
        """We expect only workers and indexers, no application service."""
        return [
            ExpectedService.worker(
                name="pdf-processor",
                port=8000,
            ),
            ExpectedService.indexer(
                name="document-indexer",
                port=8000,
            ),
        ]

    def create_app(self) -> FastAPI:
        """Create an app without SERVICE_NAME set."""
        # Make sure SERVICE_NAME is not set
        os.environ.pop("SERVICE_NAME", None)

        from fastapi import FastAPI
        from services import DocumentIndexerService, PDFProcessorService

        from service_discovery import create_consul_lifespan

        app = FastAPI(lifespan=create_consul_lifespan)

        # Add only workers/indexers
        pdf_processor = PDFProcessorService()
        doc_indexer = DocumentIndexerService()

        app.include_router(pdf_processor.router)
        app.include_router(doc_indexer.router)

        # Add health endpoint needed for server startup
        @app.get("/health")
        async def health():
            return {"status": "healthy"}

        return app
