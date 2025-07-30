# DynaFetch

A robust Python client for fetching paginated data from OData/REST APIs, with a focus on Dynamics Business Central integration. DynaFetch provides automatic pagination handling, retry logic, and comprehensive error handling.

## Features

- 🔄 Automatic pagination handling
- 🔁 Built-in retry logic with exponential backoff
- 🛡️ Comprehensive error handling
- ⏱️ Configurable timeouts and retry settings
- 🔑 Support for basic authentication
- 📊 Flexible response data extraction
- 🚀 Session management for efficient connections

## Installation

```bash
pip install dynafetch
```

## Quick Start

```python
from dynafetch import DynaFetchClient

# Initialize the client with your API credentials
client = DynaFetchClient(
    base_url="https://api.example.com",
    credentials=("username", "password")
)

# Fetch all data from an endpoint
data = client.get_data("customers")
```

## Detailed Usage

### Basic Authentication

```python
from dynafetch import DynaFetchClient

# Initialize with basic authentication
client = DynaFetchClient(
    base_url="https://api.example.com",
    credentials=("username", "password")
)
```

### Using a Custom Session

```python
import requests
from dynafetch import DynaFetchClient

# Create a custom session with specific configurations
session = requests.Session()
session.headers.update({"Custom-Header": "value"})

# Initialize with custom session
client = DynaFetchClient(
    base_url="https://api.example.com",
    session=session
)
```

### Fetching Data with Parameters

```python
# Fetch data with query parameters
data = client.get_data(
    endpoint="customers",
    params={
        "$filter": "status eq 'active'",
        "$select": "id,name,email",
        "$top": 100
    }
)
```

### Handling Single Pages

```python
# Fetch a single page of data
page = client.get_single_page(
    endpoint="customers",
    params={"$top": 50}
)
```

### Custom Headers

```python
# Set default headers for all requests
client.set_default_headers({
    "Accept": "application/json",
    "Custom-Header": "value"
})

# Or provide headers for specific requests
data = client.get_data(
    endpoint="customers",
    headers={"Custom-Header": "specific-value"}
)
```

## Configuration Options

The `DynaFetchClient` accepts the following configuration options:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `base_url` | str | Required | Base URL for the API |
| `session` | requests.Session | None | Pre-configured requests session |
| `credentials` | tuple[str, str] | None | Tuple of (username, password) for basic auth |
| `timeout` | int | 30 | Request timeout in seconds |
| `max_retries` | int | 3 | Maximum number of retry attempts |
| `retry_delay` | float | 1.0 | Initial delay between retries (uses exponential backoff) |
| `data_key` | str | "value" | Key in response JSON containing the data array |
| `next_link_key` | str | "@odata.nextLink" | Key in response JSON containing the next page URL |

## Error Handling

DynaFetch provides comprehensive error handling through the `DynaFetchError` exception:

```python
from dynafetch import DynaFetchClient, DynaFetchError

try:
    client = DynaFetchClient(
        base_url="https://api.example.com",
        credentials=("username", "password")
    )
    data = client.get_data("customers")
except DynaFetchError as e:
    print(f"Error fetching data: {e}")
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
