import asyncio
from typing import Any

from bcodata import Client, QueryBuilder
from bcodata.exceptions import ODataConnectionError, ODataHTTPError, ODataTimeoutError


async def fetch_with_retry(
    client: Client, endpoint: str, query: dict[str, Any], max_attempts: int = 3
) -> list[dict[str, Any]]:
    """Fetch data with retry logic."""
    for attempt in range(max_attempts):
        try:
            return await client.get_data(endpoint, query)
        except ODataTimeoutError:
            if attempt == max_attempts - 1:
                raise
            print(f"Timeout occurred, retrying... (attempt {attempt + 1}/{max_attempts})")  # noqa: T201
            await asyncio.sleep(2**attempt)  # Exponential backoff
    return []  # Return empty list if all attempts fail


async def main() -> None:
    """Advanced usage example of the BCOData client."""
    # Custom client configuration
    client = Client(
        base_url="https://api.businesscentral.dynamics.com/v2.0/tenant/companies/company/environment/api/v2.0",
        credentials=("username", "password"),
        max_rate=20,  # Increased rate limit
        time_period=1,
        max_concurrency=10,  # Increased concurrency
        max_retries=3,
        base_retry_delay=1,
        timeout=120,  # Increased timeout
    )

    async with client:
        try:
            # Example 1: Complex filtering with multiple conditions
            query1 = (
                QueryBuilder()
                .filter("""
                    Age gt 18 and
                    (City eq 'New York' or City eq 'Los Angeles') and
                     startswith(Name, 'J') and
                     not contains(Email, 'test')
                """)
                .select(["Name", "Email", "Phone", "City", "Age"])
                .order_by("Age", descending=True)
                .top(100)
            )

            data1 = await fetch_with_retry(client, "customers", query1.build())
            print(f"Found {len(data1)} matching customers")  # noqa: T201

            # Example 2: Batch processing with pagination
            page_size = 50
            total_processed = 0

            while True:
                query2 = QueryBuilder().top(page_size).skip(total_processed).order_by("Id")

                batch = await client.get_data("orders", query2.build())
                if not batch:
                    break

                # Process the batch
                for _order in batch:
                    # Process order here
                    pass

                total_processed += len(batch)
                print(f"Processed {total_processed} orders so far")  # noqa: T201

                if len(batch) < page_size:
                    break

        except ODataHTTPError as e:
            print(f"HTTP Error {e.status_code}: {e.response_content}")  # noqa: T201
        except ODataConnectionError as e:
            print(f"Connection Error: {e}")  # noqa: T201
        except Exception as e:  # noqa: BLE001
            print(f"Unexpected error: {e}")  # noqa: T201


if __name__ == "__main__":
    asyncio.run(main())
