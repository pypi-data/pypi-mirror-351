# BCOData

A Python client library for interacting with Business Central OData API.

## Features

- Async/await support for efficient API calls
- Automatic rate limiting and concurrency control
- Built-in retry mechanism for failed requests
- Query builder for constructing OData queries
- Comprehensive error handling
- Detailed logging with loguru
- Automatic pagination handling for large datasets
- Type hints and static type checking support

## Requirements

- Python >= 3.12
- Dependencies:
  - aiolimiter >= 1.2.1
  - httpx >= 0.28.1
  - loguru >= 0.7.3
  - tenacity >= 9.1.2

## Installation

```bash
pip install bcodata
```

## Quick Start

```python
import asyncio
from bcodata import Client, QueryBuilder

async def main():
    # Initialize the client
    base_url = "https://api.businesscentral.dynamics.com/v2.0/tenant/companies/company/environment/api/v2.0"
    credentials = ("username", "password")

    async with Client(base_url, credentials) as client:
        # Create a query using QueryBuilder
        query = (
            QueryBuilder()
            .filter("Name eq 'John'")  # Filter by name
            .select(["Name", "Age", "Email"])  # Select specific fields
            .top(10)  # Limit to 10 results
            .skip(20)  # Skip first 20 results
            .order_by("Age", descending=True)  # Sort by age descending
        )

        # Fetch data using the query
        data = await client.get_data("users", query.build())
        print(f"Retrieved {len(data)} items")

if __name__ == "__main__":
    asyncio.run(main())
```

## Documentation

### Query Builder

The `QueryBuilder` class provides a fluent interface for constructing OData queries:

#### Filtering

```python
# Simple equality
query = QueryBuilder().filter("Name eq 'John'")

# Multiple conditions
query = QueryBuilder().filter("Age gt 18 and City eq 'New York'")

# Using functions
query = QueryBuilder().filter("startswith(Name, 'J')")
```

#### Field Selection

```python
# Select specific fields
query = QueryBuilder().select(["Name", "Age", "Email"])

# Combine with other parameters
query = (
    QueryBuilder()
    .select(["Name", "Age"])
    .filter("Age gt 18")
)
```

#### Pagination

```python
# Get first 10 items
query = QueryBuilder().top(10)

# Skip first 20 items
query = QueryBuilder().skip(20)

# Combine for pagination
query = (
    QueryBuilder()
    .top(10)
    .skip(20)  # Get items 21-30
)
```

#### Sorting

```python
# Sort ascending
query = QueryBuilder().order_by("Name")

# Sort descending
query = QueryBuilder().order_by("Age", descending=True)
```

### Client Configuration

The `Client` class accepts the following configuration parameters:

- `base_url` (str): The base URL of the Business Central OData API
- `credentials` (tuple[str, str] | None): Username and password for authentication
- `max_rate` (int): Maximum number of requests per time period (default: 10)
- `time_period` (int): Time period in seconds for rate limiting (default: 1)
- `max_concurrency` (int): Maximum number of concurrent requests (default: 5)
- `max_retries` (int): Number of retry attempts for failed requests (default: 3)
- `base_retry_delay` (int): Base delay between retries in seconds (default: 1)
- `timeout` (int): Request timeout in seconds (default: 90)

Example:

```python
client = Client(
    base_url="https://api.businesscentral.dynamics.com/v2.0/tenant/companies/company/environment/api/v2.0",
    credentials=("username", "password"),
    max_rate=20,  # Maximum requests per time period
    time_period=1,  # Time period in seconds
    max_concurrency=5,  # Maximum concurrent requests
    max_retries=3,  # Number of retries for failed requests
    base_retry_delay=1,  # Base delay between retries in seconds
    timeout=90,  # Request timeout in seconds
)
```

### Error Handling

```python
from bcodata.exceptions import (
    ODataConnectionError,
    ODataHTTPError,
    ODataJSONDecodeError,
    ODataTimeoutError,
    ODataRequestError
)

async with Client(base_url, credentials) as client:
    try:
        data = await client.get_data("users", query.build())
    except ODataHTTPError as e:
        print(f"HTTP Error: {e.status_code} - {e.response_content}")
    except ODataConnectionError as e:
        print(f"Connection Error: {e}")
    except ODataTimeoutError as e:
        print(f"Timeout Error: {e}")
    except ODataJSONDecodeError as e:
        print(f"JSON Decode Error: {e}")
    except ODataRequestError as e:
        print(f"Request Error: {e}")
```

### Concurrent Data Fetching

```python
async def fetch_multiple_endpoints(client: Client):
    # Define the endpoints to fetch
    endpoints = [
        "companies",
        "customers",
        "items",
        "salesOrders"
    ]

    # Create tasks for each endpoint
    tasks = [client.get_data(endpoint) for endpoint in endpoints]

    # Execute all tasks concurrently
    results = await asyncio.gather(*tasks)

    # Process results
    for endpoint, data in zip(endpoints, results):
        print(f"Retrieved {len(data)} records from {endpoint}")
```

## Examples

Check out the [examples directory](examples/README.md) for comprehensive examples demonstrating various features and use cases.

## Development

### Setup

1. Clone the repository:

```bash
git clone https://github.com/yourusername/bcodata.git
cd bcodata
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install development dependencies:

```bash
pip install -e ".[dev]"
```

### Code Quality

The project uses:

- Ruff for linting and formatting
- Type hints for static type checking
- Comprehensive test suite

Run the linter:

```bash
ruff check .
```

Format code:

```bash
ruff format .
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
