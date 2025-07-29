# TinyToken SDK

Text compression API client.

## Install

```bash
pip install tinytoken-sdk
```

## Usage

```python
import tinytoken

# Compress text
result = tinytoken.compress("Your text here", 0.8, "your-api-key")
print(result)

# Or use the class
client = tinytoken.TinyToken("your-api-key")
result = client.compress("Your text here", 0.8)
print(result)
```

Get your API key at https://tinytoken.org
