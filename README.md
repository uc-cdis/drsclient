drsclient
===
This is the client library for making requests to the GA4GH DRS compatible services. It provides a simple way to interact with a GA4GH DRS server and specifically [DRS running on Indexd servers](https://github.com/uc-cdis/indexd/blob/master/docs/drs.md).

## Installation
### From PyPi:
```
pip install drsclient
```
### From source code:
Install poetry with:
```
pip install poetry
```
Create a virtual environment:
```
poetry shell
```
Install all the dependencies:
```
poetry install
```

## Usage
### Initialization
To start, initialize the drsclient. There are only two fields required to initialize the client:
- `baseurl` (required): url of the server we're trying to connect with.
- `auth` (optional): auth info to access object bytes.
```python
from drsclient.client import DrsClient

client = DrsClient(baseurl="somedrsserver.io", auth="some_token")

```

### Create a bundle
#### Method: `create`
```python
client.create(
    bundles=["object1", "bundle1", ...], # required list of bundles and objects to bundle
    name="bundle_name", # optional
    guid="bundleA", # optional
    size=500, # optional
    checksums="checksum", # optional
    description="description". # optional
    version="abc123", # optional
    aliases=["A", "B"] #optional
)
```

#### Method: `async_create`
```python
asyncio.run(client.async_create(
    bundles=["object1", "bundle1", ...], # required list of bundles and objects to bundle
    name="bundle_name", # optional
    guid="bundleA", # optional
    size=500, # optional
    checksums="checksum", # optional
    description="description". # optional
    version="abc123", # optional
    aliases=["A", "B"] #optional
))
```

### Get DRS object
#### Method: `get`
```python
client.get(guid="object1")
client.get(guid="bundle1", expand=True) # expand parameter for bundle expansion
```

#### Method: `async_get`
```python
asyncio.run(client.get(guid="object1"))
asyncio.run(client.get(guid="bundle1", expand=True)) # expand parameter for bundle expansion
```

### Get all objects
#### Method: `get_all`
```python
client.get_all()
```

#### Method: `async_get_all`
```python
asyncio.run(client.async_get_all())
```

### Download object bytes
#### Method: `download`
```python
client.download(guid="object1", protocol="s3") # protocol parameter to specify cloud storage type
```

#### Method: `async_download`
```python
asyncio.run(client.async_download(guid="object1", protocol="s3")) # protocol parameter to specify cloud storage type
```

### Delete bundles
#### Method: `delete`
```python
client.delete(guid="bundle")
```

### Method: `async_delete`
```python
asyncio.run(client.async_delete(guid="bundle"))
```
