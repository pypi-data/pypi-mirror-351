# VercelPy

A Python wrapper for Vercel's storage services, providing a clean, Pythonic interface to Vercel Blob Storage and Edge Config.

[![PyPI version](https://badge.fury.io/py/vercelpy.svg)](https://badge.fury.io/py/vercelpy)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Installation

```bash
# Install with pip
pip3 install vercelpy
```

## Features

- **Blob Storage**: Upload, download, list, copy, and delete files with Vercel's Blob Storage
- **Edge Config**: Store and retrieve configuration values with Vercel's Edge Config

## Blob Storage

Vercel Blob is a global object storage service designed for serving content directly at the edge. VercelPy provides a simple interface for working with Vercel Blob.

### Setup

Set your Blob Storage credentials via environment variables:

```bash
# In your .env file
BLOB_READ_WRITE_TOKEN=your_read_write_token
```

### Usage Examples

#### Importing the Module

```python
import vercelpy.blob_store as blob_store
# or with an alias
import vercelpy.blob_store as vb_store
```

#### List all files in the Blob Storage

```python
# List all blobs with default limit (1000)
blobs = blob_store.list()

# With a limit
blobs = blob_store.list({
    'limit': '5',
})

# With pagination using cursor
blobs = blob_store.list({
    'limit': '4',
    'cursor': cursor,
})

# The response contains:
# blobs: List of blob objects with size, uploadedAt, pathname, url, downloadUrl
# cursor: Pagination cursor (if available)
# hasMore: Boolean indicating if more blobs are available
# folders: List of folder names (if available)
```

#### Upload File / Blob to the Storage

```python
# Upload a file with random suffix
with open('file.txt', 'rb') as f:
    response = blob_store.put('test.txt', f.read())
    print(response)

# Upload without random suffix
with open('file.txt', 'rb') as f:
    response = blob_store.put('test.txt', f.read(), {
        "addRandomSuffix": "false",
    })
    print(response)

# The response contains:
# pathname: Path to the blob
# contentType: Content type of the blob
# contentDisposition: Content disposition of the blob
# url: URL of the blob
# downloadUrl: URL to download the blob
```

#### Downloading Files

```python
# Download a file on the server
blob_store.download_file('blob_url', 'path/to/directory/', {'token': 'my_token'})

# If no directory is specified, it will download to the program's base directory
```

#### Checking Blob Metadata

```python
# Get blob metadata
metadata = blob_store.head('blob_url')
print(metadata)

# The response contains:
# size: Size of the blob in bytes
# uploadedAt: Date when the blob was uploaded
# pathname: Path to the blob
# contentType: Content type of the blob
# contentDisposition: Content disposition of the blob
# url: URL of the blob
# downloadUrl: URL to download the blob
# cacheControl: Cache control header
```

#### Copying Blobs

```python
# Copy a blob to a new location (without random suffix by default)
response = blob_store.copy("https://example.blob.vercel-storage.com/test.txt", "new-folder/test.txt")
print(response)

# To add random suffix when copying
response = blob_store.copy("https://example.blob.vercel-storage.com/test.txt", "new-folder/test.txt", {
    "addRandomSuffix": "true"
})

# The response contains pathname, contentType, contentDisposition, url, and downloadUrl
```

#### Deleting Blobs

```python
# Delete a single blob
blob_store.delete('blob_url')

# Delete multiple blobs
blob_store.delete([
    'blob_url_1',
    'blob_url_2'
])

# The delete method doesn't return anything
```

## Edge Config

Vercel Edge Config allows you to store and retrieve configuration values at the edge. VercelPy provides a convenient interface for working with Edge Config.

### Setup

Set your Edge Config credentials via environment variables:

```bash
# In your .env file
EDGE_CONFIG=your_edge_config_connection_string
```

The connection string can be in either of these formats:
- `edge-config:id=your_id&token=your_token`
- `https://edge-config.vercel.com/your_id?token=your_token`

### Usage Examples

#### Creating a Client

```python
import vercelpy.edge_config as edge

# Create a client with environment variables
# This happens automatically when using module functions

# Create a client with a connection string
connection_string = "edge-config:id=your_id&token=your_token"
client = edge.create_client(connection_string)

# With options
client = edge.create_client(connection_string, {"consistentRead": True})
```

#### Getting a Value

```python
import vercelpy.edge_config as edge

# Get a value with the default client (using EDGE_CONFIG env var)
value = edge.get("api_key")
print(f"API Key: {value}")

# Get with options for consistent reads
value = edge.get("feature_flags", {"consistentRead": True})

# Using a specific client
client = edge.create_client("your_connection_string")
value = client.get("database_url")
```

#### Checking if a Key Exists

```python
import vercelpy.edge_config as edge

# Check if a key exists
if edge.has("feature_flag_new_ui"):
    print("Feature flag is set")

# With a specific client
client = edge.create_client("your_connection_string")
if client.has("rate_limit"):
    print("Rate limit is configured")
```

#### Getting Multiple Values

```python
import vercelpy.edge_config as edge

# Get all values
all_config = edge.get_all()
print(f"All config: {all_config}")

# Get specific keys
settings = edge.get_all(["api_url", "timeout", "retry_count"])
print(f"API URL: {settings['api_url']}")
print(f"Timeout: {settings['timeout']}")

# With options
settings = edge.get_all(["api_key", "secret"], {"consistentRead": True})
```

#### Getting Configuration Digest

```python
import vercelpy.edge_config as edge

# Get the configuration digest (for caching purposes)
digest_info = edge.digest()
print(f"Digest: {digest_info['digest']}")
print(f"Items Count: {digest_info['itemsCount']}")
```

## Error Handling

```python
import vercelpy.edge_config as edge
from vercelpy.edge_config.errors import EdgeConfigError, UnexpectedNetworkError

try:
    value = edge.get("api_key")
except Exception as e:
    if str(e) == EdgeConfigError.UNAUTHORIZED:
        print("Authentication failed")
    elif str(e) == EdgeConfigError.EDGE_CONFIG_NOT_FOUND:
        print("Edge Config not found")
    else:
        print(f"Unexpected error: {e}")
```

## Common Issues

1. Since Vercel Blob Storage is still in beta, requests may sometimes result in unexpected Connection Errors. The implementation uses a retry mechanism with exponential backoff to mitigate this issue.

## Environment Variables

- `BLOB_READ_WRITE_TOKEN`: Your Vercel Blob read-write token
- `EDGE_CONFIG`: Your Edge Config connection string

## License

MIT - See the [LICENSE](LICENSE) file for details.

## Author

Surya Sekhar Datta <hello@surya.dev>

## Links

- [GitHub Repository](https://github.com/SuryaSekhar14/vercelpy)
- [PyPI Package](https://pypi.org/project/vercelpy/)