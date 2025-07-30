"""
Example of using service discovery functionality.

This module demonstrates how to discover services registered in Consul.
"""

import asyncio
import logging
from typing import Any

from service_discovery import create_service_discovery

logger = logging.getLogger(__name__)


async def demonstrate_service_discovery() -> dict[str, Any]:
    """
    Demonstrate service discovery functionality.

    Returns:
        Dictionary with discovered services and example URIs
    """
    # Create a service discovery client
    discovery = create_service_discovery()

    try:
        # Get all available services
        all_services = await discovery.get_services()
        logger.info(f"Discovered {len(all_services)} services")

        # Get a specific service URI (with load balancing)
        example_uris = {}
        for service_name in all_services:
            uri = await discovery.get_service_uri(service_name)
            if uri:
                example_uris[service_name] = uri
                logger.info(f"Service '{service_name}' available at: {uri}")

        # Get all URIs for a specific service
        service_details = {}
        for service_name in all_services:
            all_uris = await discovery.get_all_service_uris(service_name)
            service_details[service_name] = {"instance_count": len(all_uris), "uris": all_uris}

        return {
            "discovered_services": list(all_services.keys()),
            "service_count": len(all_services),
            "example_uris": example_uris,
            "service_details": service_details,
        }

    finally:
        # Always close the discovery client
        await discovery.close()


async def discover_and_call_service(service_name: str) -> dict[str, Any]:
    """
    Discover a service and make a sample call.

    Args:
        service_name: Name of the service to discover

    Returns:
        Dictionary with discovery result and call status
    """
    discovery = create_service_discovery()

    try:
        # Get a URI for the service
        uri = await discovery.get_service_uri(service_name)

        if not uri:
            return {"status": "error", "message": f"Service '{service_name}' not found"}

        # In a real application, you would make an HTTP call here
        # For example using aiohttp:
        # async with aiohttp.ClientSession() as session:
        #     async with session.get(f"{uri}/health") as response:
        #         health_status = await response.json()

        return {
            "status": "success",
            "service_name": service_name,
            "discovered_uri": uri,
            "message": f"Successfully discovered service at {uri}",
        }

    finally:
        await discovery.close()


async def monitor_service_availability(service_name: str, duration: int = 10) -> list[dict[str, Any]]:
    """
    Monitor service availability over time.

    Args:
        service_name: Name of the service to monitor
        duration: How long to monitor (seconds)

    Returns:
        List of availability checks
    """
    discovery = create_service_discovery()
    checks = []

    try:
        start_time = asyncio.get_event_loop().time()

        while asyncio.get_event_loop().time() - start_time < duration:
            # Get all URIs for the service
            uris = await discovery.get_all_service_uris(service_name)

            checks.append(
                {
                    "timestamp": asyncio.get_event_loop().time() - start_time,
                    "available": len(uris) > 0,
                    "instance_count": len(uris),
                    "uris": uris,
                }
            )

            # Wait before next check
            await asyncio.sleep(2)

        return checks

    finally:
        await discovery.close()


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # Run discovery examples
    async def main():
        # Demonstrate basic discovery
        print("\n=== Service Discovery Demo ===")
        result = await demonstrate_service_discovery()
        print(f"Discovered services: {result['discovered_services']}")

        # Try to discover a specific service
        if result["discovered_services"]:
            service = result["discovered_services"][0]
            print(f"\n=== Discovering '{service}' ===")
            call_result = await discover_and_call_service(service)
            print(f"Result: {call_result}")

        # Monitor a service
        print("\n=== Monitoring Service Availability ===")
        if result["discovered_services"]:
            service = result["discovered_services"][0]
            print(f"Monitoring '{service}' for 10 seconds...")
            checks = await monitor_service_availability(service, 10)
            for check in checks:
                print(f"  t={check['timestamp']:.1f}s: {check['instance_count']} instances")

    asyncio.run(main())
