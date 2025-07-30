import asyncio
from typing import Any

from bcodata import Client, QueryBuilder
from bcodata.exceptions import ODataConnectionError, ODataHTTPError


async def fetch_endpoint(client: Client, endpoint: str, query: dict[str, Any] | None = None) -> tuple[str, list[dict]]:
    """
    Fetch data from a single endpoint.

    Parameters
    ----------
    client : Client
        The BCOData client instance
    endpoint : str
        The endpoint to fetch data from
    query : dict[str, Any] | None
        Optional query parameters

    Returns
    -------
    tuple[str, List[dict]]
        A tuple containing the endpoint name and its data

    """
    try:
        data = await client.get_data(endpoint, query)
    except (ODataHTTPError, ODataConnectionError) as e:
        print(f"Error fetching {endpoint}: {e}")  # noqa: T201
        return endpoint, []
    else:
        return endpoint, data


async def fetch_multiple_endpoints(client: Client) -> dict[str, list[dict]]:
    """
    Fetch data from multiple endpoints concurrently.

    Parameters
    ----------
    client : Client
        The BCOData client instance

    Returns
    -------
    Dict[str, List[dict]]
        Dictionary mapping endpoint names to their data

    """
    # Define the endpoints and their queries
    endpoints_queries = {
        "companies": QueryBuilder().select(["name", "id", "systemVersion"]).build(),
        "customers": (
            QueryBuilder().select(["number", "displayName", "email", "phoneNumber"]).top(10).order_by("displayName")
        ).build(),
        "items": (
            QueryBuilder().select(["number", "displayName", "type", "unitPrice"]).filter("type eq 'Inventory'").top(5)
        ).build(),
        "salesOrders": (
            QueryBuilder()
            .select(["number", "customerNumber", "orderDate", "status"])
            .filter("status eq 'Open'")
            .top(5)
            .order_by("orderDate", descending=True)
        ).build(),
    }

    # Create tasks for each endpoint
    tasks = [fetch_endpoint(client, endpoint, query) for endpoint, query in endpoints_queries.items()]

    # Execute all tasks concurrently
    results = await asyncio.gather(*tasks)

    # Create a dictionary mapping endpoints to their results
    return dict(results)


async def main() -> None:
    """Concurrent data fetching from multiple Business Central OData endpoints."""
    # Initialize the client with custom configuration for concurrent requests
    client = Client(
        base_url="https://api.businesscentral.dynamics.com/v2.0/tenant/companies/company/environment/api/v2.0",
        credentials=("username", "password"),
        max_rate=20,  # Increased rate limit for concurrent requests
        time_period=1,
        max_concurrency=10,  # Increased concurrency limit
        max_retries=3,
        base_retry_delay=1,
        timeout=90,
    )

    async with client:
        try:
            # Fetch data from all endpoints concurrently
            results = await fetch_multiple_endpoints(client)

            # Process and display results
            for endpoint, data in results.items():
                print(f"\n=== {endpoint.upper()} ===")  # noqa: T201
                print(f"Total records: {len(data)}")  # noqa: T201

                # Display first record as sample
                if data:
                    print("\nSample record:")  # noqa: T201
                    for key, value in data[0].items():
                        print(f"{key}: {value}")  # noqa: T201

        except Exception as e:  # noqa: BLE001
            print(f"An error occurred: {e}")  # noqa: T201


if __name__ == "__main__":
    asyncio.run(main())
