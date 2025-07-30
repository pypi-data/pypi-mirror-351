# WhoisJSON Python Client

A simple and reusable Python client for the [WhoisJSON API](https://whoisjson.com) service.

Free accounts include 500 requests per month. [Check out our full documentation](https://whoisjson.com/documentation) for more details about our API.

## Installation

```bash
pip install whoisjson
```

## Usage

```python
from whoisjson import WhoisJsonClient

# Initialize the client
client = WhoisJsonClient(api_key="your-api-key")

# 1. WHOIS Lookup
try:
    whois_result = client.whois("example.com")  # or client.lookup() for backward compatibility
    print(whois_result)
except Exception as e:
    print(f"Error: {e}")

# 2. DNS Lookup
try:
    dns_result = client.nslookup("example.com")
    print(dns_result)
except Exception as e:
    print(f"Error: {e}")

# 3. SSL Certificate Check
try:
    ssl_result = client.ssl_cert_check("example.com")
    print(ssl_result)
except Exception as e:
    print(f"Error: {e}")
```

## Available Endpoints

The client provides access to the following WhoisJSON API endpoints:

1. `whois(domain)`: Get WHOIS information for a domain
2. `nslookup(domain)`: Get DNS records for a domain
3. `ssl_cert_check(domain)`: Get SSL certificate information for a domain

## Features

- Simple and intuitive API
- Type hints for better IDE support
- Proper error handling
- Support for both free and premium API access
- Comprehensive examples included

## Examples

Check out the `examples` directory for ready-to-use example scripts demonstrating all features.

To run the demo:
```bash
python examples/demo.py
```

## Requirements

- Python 3.6+
- requests>=2.25.0

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 