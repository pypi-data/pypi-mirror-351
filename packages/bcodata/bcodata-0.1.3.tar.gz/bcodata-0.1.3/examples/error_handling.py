import asyncio
from typing import Any

from bcodata import Client, QueryBuilder
from bcodata.exceptions import (
    ODataConnectionError,
    ODataHTTPError,
    ODataJSONDecodeError,
    ODataRequestError,
    ODataTimeoutError,
)


async def fetch_with_retry(
    client: Client,
    endpoint: str,
    query: dict[str, Any] | None = None,
    max_attempts: int = 3,
) -> list[dict[str, Any]] | None:
    """
    Fetch data from an endpoint with retry logic.

    Parameters
    ----------
    client : Client
        BCOData client instance
    endpoint : str
        API endpoint to fetch
    query : dict[str, Any] | None
        Optional query parameters
    max_attempts : int
        Maximum number of retry attempts

    Returns
    -------
    list[dict[str, Any]]
        Fetched data

    Raises
    ------
    ODataRequestError
        If all retry attempts fail

    """
    for attempt in range(max_attempts):
        try:
            return await client.get_data(endpoint, query)
        except (ODataConnectionError, ODataTimeoutError) as e:
            if attempt == max_attempts - 1:
                raise ODataRequestError(f"Failed after {max_attempts} attempts: {e!s}") from e
            print(f"Attempt {attempt + 1} failed: {e!s}. Retrying...")  # noqa: T201
            await asyncio.sleep(2**attempt)  # Exponential backoff
    return None


async def main():  # noqa: C901, PLR0912, ANN201
    """Error handling with BCOData."""
    client = Client(
        base_url="https://api.businesscentral.dynamics.com/v2.0/tenant/companies/company/environment/api/v2.0",
        credentials=("username", "password"),
        max_rate=10,
        time_period=1,
        max_concurrency=5,
        max_retries=2,  # Reduced retries for demonstration
        base_retry_delay=1,
        timeout=30,  # Shorter timeout for demonstration
    )

    async with client:
        try:
            # Example 1: Handle specific error types with QueryBuilder
            try:
                # Create a query that might fail
                query = (
                    QueryBuilder()
                    .select(["name", "id", "systemVersion"])
                    .filter("name eq 'Invalid Company'")  # This might not exist
                    .top(1)
                ).build()

                data = await client.get_data("companies", query)
                print(f"Successfully retrieved {len(data)} companies")  # noqa: T201
            except ODataConnectionError as e:
                print(f"Connection error occurred: {e}")  # noqa: T201
            except ODataTimeoutError as e:
                print(f"Request timed out: {e}")  # noqa: T201
            except ODataHTTPError as e:
                print(f"HTTP error occurred: {e}")  # noqa: T201
                if e.status_code == 401:
                    print("Authentication failed. Please check your credentials.")  # noqa: T201
                elif e.status_code == 403:
                    print("Access forbidden. Please check your permissions.")  # noqa: T201
                elif e.status_code == 404:
                    print("Resource not found. Please check the endpoint and query.")  # noqa: T201
            except ODataJSONDecodeError as e:
                print(f"Failed to parse response: {e}")  # noqa: T201

            try:
                query = (
                    QueryBuilder()
                    .select(["number", "displayName", "email"])
                    .filter("displayName startswith 'A'")
                    .top(10)
                    .order_by("displayName")
                ).build()

                data = await fetch_with_retry(client, "customers", query)
                print(f"Successfully retrieved {len(data)} customers after retries")  # noqa: T201

                # Display sample data
                if data:
                    print("\nSample customer:")  # noqa: T201
                    for key, value in data[0].items():
                        print(f"{key}: {value}")  # noqa: T201
            except ODataRequestError as e:
                print(f"All retry attempts failed: {e}")  # noqa: T201

            # Example 3: Handle rate limiting
            try:
                # Create multiple queries to demonstrate rate limiting
                queries = [
                    QueryBuilder().select(["number"]).top(1).build(),
                    QueryBuilder().select(["displayName"]).top(1).build(),
                    QueryBuilder().select(["email"]).top(1).build(),
                ]

                # Execute queries in quick succession
                for i, query in enumerate(queries, 1):
                    data = await client.get_data("customers", query)
                    print(f"Query {i} completed successfully")  # noqa: T201
            except ODataHTTPError as e:
                if e.status_code == 429:
                    print("Rate limit exceeded. Consider increasing the time period or reducing max_rate.")  # noqa: T201
                else:
                    print(f"HTTP error occurred: {e}")  # noqa: T201

        except Exception as e:  # noqa: BLE001
            print(f"Unexpected error: {e}")  # noqa: T201


if __name__ == "__main__":
    asyncio.run(main())
