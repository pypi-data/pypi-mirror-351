# BCOData Examples

This directory contains example scripts demonstrating various features and use cases of the BCOData library.

## Available Examples

### Basic Usage (`basic_usage.py`)

Demonstrates fundamental features of the library:

- Client initialization and basic configuration
- Simple query building with QueryBuilder
- Basic filtering and field selection
- Pagination and sorting
- Simple error handling

Run it with:

```bash
python examples/basic_usage.py
```

### Advanced Usage (`advanced_usage.py`)

Shows more complex scenarios and best practices:

- Custom client configuration with rate limiting
- Complex filtering with multiple conditions
- Batch processing with pagination
- Advanced error handling with retry logic
- Exponential backoff for timeouts
- Concurrent data fetching
- Logging configuration

Run it with:

```bash
python examples/advanced_usage.py
```

## Prerequisites

Before running the examples:

1. Install the package in development mode:

```bash
pip install -e .
```

2. Configure your environment:
   - Create a `.env` file in the examples directory with your credentials:
     ```
     BC_USERNAME=your_username
     BC_PASSWORD=your_password
     BC_BASE_URL=your_base_url
     ```
   - Or update the example files directly with your credentials:
     - Replace `"username"` with your actual username
     - Replace `"password"` with your actual password
     - Update the `base_url` with your actual Business Central API URL

## Example Structure

Each example file follows a similar structure:

1. Imports and configuration
2. Helper functions
3. Main async function
4. Example usage with error handling
5. Logging setup

## Best Practices Demonstrated

The examples demonstrate several best practices:

1. **Resource Management**

   - Using context managers (`async with`) for proper cleanup
   - Proper error handling and logging

2. **Performance Optimization**

   - Rate limiting configuration
   - Concurrent data fetching
   - Efficient pagination

3. **Error Handling**

   - Comprehensive exception handling
   - Retry logic with exponential backoff
   - Proper logging of errors

4. **Code Organization**
   - Clear separation of concerns
   - Reusable helper functions
   - Type hints for better code maintainability

## Notes

- The examples use dummy data and endpoints. Replace them with actual Business Central endpoints and data structures.
- Error handling examples are included to demonstrate proper exception handling in production environments.
- The advanced example includes retry logic with exponential backoff, which is useful for handling temporary failures.
- All examples include logging to help understand what's happening during execution.

## Contributing Examples

If you'd like to contribute new examples:

1. Create a new Python file in the examples directory
2. Follow the existing structure and best practices
3. Include clear comments and documentation
4. Add a description of your example to this README
5. Submit a pull request

## Need Help?

If you have questions about the examples or need help implementing specific features:

1. Check the [main documentation](../README.md)
2. Open an issue on GitHub
3. Submit a pull request with your improvements
