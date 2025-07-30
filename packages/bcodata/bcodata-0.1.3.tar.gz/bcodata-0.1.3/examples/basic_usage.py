import asyncio

from bcodata import Client, QueryBuilder


async def main() -> None:
    """Usage example of the BCOData client."""
    # Initialize the client
    base_url = "https://api.businesscentral.dynamics.com/v2.0/tenant/companies/company/environment/api/v2.0"
    credentials = ("username", "password")

    async with Client(base_url, credentials) as client:
        # Example 1: Simple query with filter
        query1 = QueryBuilder().filter("Name eq 'John'")
        data1 = await client.get_data("users", query1.build())
        print(f"Found {len(data1)} users named John")  # noqa: T201

        # Example 2: Pagination
        query2 = QueryBuilder().top(10).skip(20).order_by("CreatedAt", descending=True)
        await client.get_data("orders", query2.build())
        print("Retrieved orders 21-30, sorted by creation date")  # noqa: T201

        # Example 3: Field selection and filtering
        query3 = QueryBuilder().select(["Name", "Email", "Phone"]).filter("Age gt 18 and City eq 'New York'").top(5)
        data3 = await client.get_data("customers", query3.build())
        print(f"Retrieved {len(data3)} adult customers from New York")  # noqa: T201


if __name__ == "__main__":
    asyncio.run(main())
