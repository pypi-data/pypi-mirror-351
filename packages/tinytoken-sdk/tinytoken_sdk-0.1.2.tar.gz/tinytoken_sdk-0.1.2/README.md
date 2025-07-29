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
result = tinytoken.compress("Your text here")
print(result)

# With optional quality parameter
result = tinytoken.compress("Your text here", 0.97)
print(result)

# Or use the class
client = tinytoken.TinyToken()
result = client.compress("Your text here")
print(result)
```

