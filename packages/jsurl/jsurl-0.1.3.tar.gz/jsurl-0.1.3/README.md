# jsurl

A Python implementation of the JavaScript URL and URLSearchParams APIs, bringing familiar web development patterns to Python.

## Features

- **JavaScript-compatible API**: Use the same URL manipulation patterns you know from JavaScript
- **Full URL parsing**: Support for all URL components including protocol, hostname, port, pathname, search, and hash
- **URLSearchParams**: Complete implementation of the URLSearchParams interface for query string manipulation
- **Type hints**: Full type annotation support for better IDE integration
- **Immutable-friendly**: Clean API design that supports both mutable and immutable usage patterns
- **Pure Python**: No external dependencies, pure Python implementation for maximum compatibility

## Installation

```bash
pip install jsurl
```

## Quick Start

### Basic URL Parsing

```python
from jsurl import URL

# Parse a URL
url = URL("https://example.com:8080/path?query=value#section")

print(url.protocol)  # "https:"
print(url.hostname)  # "example.com"
print(url.port)      # "8080"
print(url.pathname)  # "/path"
print(url.search)    # "?query=value"
print(url.hash)      # "#section"
```

### URL Manipulation

```python
from jsurl import URL

url = URL("https://example.com/api")

# Modify components
url.pathname = "/v2/users"
url.search = "?limit=10&page=1"

print(url.href)  # "https://example.com/v2/users?limit=10&page=1"

# Path joining with / operator
api_url = URL("https://api.example.com/v1")
users_url = api_url / "users"
user_url = users_url / "123"

print(user_url.href)  # "https://api.example.com/v1/users/123"
```

### Working with Query Parameters

```python
from jsurl import URL, URLSearchParams

# Using URLSearchParams directly
params = URLSearchParams.from_string("name=John&age=30&city=Tokyo")

print(params.get("name"))     # "John"
print(params.get_all("tag"))  # []

params.append("tag", "python")
params.append("tag", "web")
print(params.get_all("tag"))  # ["python", "web"]

# Using search_params on URL
url = URL("https://example.com/search")
url.search_params.set("q", "python url parsing")
url.search_params.set("limit", "50")

print(url.href)  # "https://example.com/search?q=python%20url%20parsing&limit=50"
```

### Authentication URLs

```python
from jsurl import URL

url = URL("https://user:password@api.example.com/secure")

print(url.username)  # "user"
print(url.password)  # "password"
print(url.host)      # "api.example.com"
print(url.origin)    # "https://api.example.com"
```

### IPv6 Support

```python
from jsurl import URL

# IPv6 addresses are properly handled
url = URL("https://[2001:db8::1]:8080/path")

print(url.hostname)  # "[2001:db8::1]"
print(url.port)      # "8080"
print(url.host)      # "[2001:db8::1]:8080"
```

## API Reference

### URL Class

#### Properties

- `protocol`: URL scheme (e.g., "https:")
- `username`: Username for authentication
- `password`: Password for authentication  
- `hostname`: Domain name or IP address
- `port`: Port number as string
- `pathname`: Path portion of URL
- `search`: Query string including "?"
- `hash`: Fragment identifier including "#"
- `search_params`: URLSearchParams instance for query manipulation
- `host`: hostname:port combination
- `origin`: protocol + "//" + host
- `href`: Complete URL string

#### Methods

- `URL(url)`: Constructor accepting string or URL instance
- `url / path`: Join path components using `/` operator

### URLSearchParams Class

#### Methods

- `URLSearchParams.from_string(query)`: Create from query string
- `get(key)`: Get first value for key
- `get_all(key)`: Get all values for key as list
- `set(key, value)`: Set single value (replaces existing)
- `append(key, value)`: Add value (preserves existing)
- `delete(key)`: Remove all values for key
- `key in params`: Check if key exists
- `params[key]`: Get all values (same as get_all)
- `params[key] = value`: Set value (same as set)

## Use Cases

### Web Scraping

```python
from jsurl import URL

base_url = URL("https://api.example.com/v1")

# Build API endpoints
users_endpoint = base_url / "users"
users_endpoint.search_params.set("page", "1")
users_endpoint.search_params.set("limit", "100")

response = requests.get(str(users_endpoint))
```

### Configuration Management

```python
from jsurl import URL

# Parse database URLs
db_url = URL("postgresql://user:pass@localhost:5432/mydb")

DATABASE_CONFIG = {
    'host': db_url.hostname,
    'port': int(db_url.port) if db_url.port else 5432,
    'username': db_url.username,
    'password': db_url.password,
    'database': db_url.pathname.lstrip('/')
}
```

### URL Validation and Normalization

```python
from jsurl import URL

def normalize_api_url(url_string):
    """Normalize API URL format"""
    url = URL(url_string)
    
    # Ensure HTTPS
    if url.protocol == "http:":
        url.protocol = "https"
    
    # Remove default ports
    if url.port == "443" and url.protocol == "https:":
        url.port = None
    elif url.port == "80" and url.protocol == "http:":
        url.port = None
    
    # Ensure trailing slash for API endpoints
    if not url.pathname.endswith('/'):
        url.pathname += '/'
    
    return str(url)
```

## Why jsurl?

If you're coming from JavaScript/TypeScript development, you'll feel right at home with `jsurl`. Instead of learning Python-specific URL libraries, you can use the same patterns you already know:

```python
# Instead of urllib.parse
from urllib.parse import urlparse, parse_qs
parsed = urlparse(url_string)
query_params = parse_qs(parsed.query)

# Use familiar JavaScript patterns
from jsurl import URL
url = URL(url_string)
url.search_params.get('param_name')
```

## Requirements

- Python 3.10 or higher
- No external dependencies

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
