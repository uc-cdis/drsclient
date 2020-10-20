import json
import httpx
import asyncio
import requests
from functools import wraps

MAX_RETRIES = 10


def maybe_sync(m):
    @wraps(m)
    def _wrapper(*args, **kwargs):
        coro = m(*args, **kwargs)
        if asyncio._get_running_loop() is not None:
            return coro
        result = None
        try:
            while True:
                result = coro.send(result)
        except StopIteration as si:
            return si.value

    return _wrapper


class SyncClient(httpx.Client):
    async def __aenter__(self):
        return self.__enter__()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.__exit__(exc_type, exc_val, exc_tb)

    async def request(self, *args, **kwargs):
        return super().request(*args, **kwargs)


def timeout_wrapper(func):
    def timeout(*args, **kwargs):
        kwargs.setdefault("timeout", 60)
        return func(*args, **kwargs)

    return timeout


def retry_and_timeout_wrapper(func):
    def retry_logic_with_timeout(*args, **kwargs):
        kwargs.setdefault("timeout", 60)
        retries = 0
        while retries < MAX_RETRIES:
            try:
                return func(*args, **kwargs)
            except requests.exceptions.ReadTimeout:
                retries += 1
                if retries == MAX_RETRIES:
                    raise

    return retry_logic_with_timeout


class DrsClient(object):
    def __init__(self, baseurl, auth=None, token=None):
        self.auth = auth
        self.url = baseurl
        self.token = token

    def url_for(self, *path):
        subpath = "/".join(path).lstrip("/")
        return "{}/{}".format(self.url.rstrip("/"), subpath)

    def check_status(self, status_endpoint="/index"):
        """Check that the API we are trying to communicate with is online"""
        resp = httpx.get(self.url + status_endpoint)
        return resp

    def get(self, guid, endpoint="/ga4gh/drs/v1/objects", expand=False):
        params = {"expand": expand}
        response = self._get(SyncClient, endpoint, guid, params=params)
        return response

    async def async_get(self, guid, endpoint="/ga4gh/drs/v1/objects", expand=False):
        params = {"expand": expand}
        response = await self._get(httpx.AsyncClient, endpoint, guid, params=params)
        return response

    def download(self, guid, protocol, endpoint="/ga4gh/drs/v1/objects"):
        headers = {}
        if self.token:
            headers["Authorization"] = "Bearer " + self.token
        endpoint += "/" + guid + "/access/" + protocol
        response = self._get(SyncClient, endpoint, headers=headers)
        return response

    async def async_download(self, guid, protocol, endpoint="/ga4gh/drs/v1/objects"):
        headers = {}
        if self.token:
            headers["Authorization"] = "Bearer " + self.token
        endpoint += "/" + guid + "/access/" + protocol
        response = await self._get(httpx.AsyncClient, endpoint, headers=headers)
        return response

    def get_all(
        self,
        endpoint="/ga4gh/drs/v1/objects",
        start=None,
        limit=None,
        page=None,
        form=None,
    ):
        """
        Get a list of bundle, object or both.

        Args:
            endpoint (str): pick between '/ga4gh/drs/v1/objects', 'bundle' or 'index' endpoint. (If calling a Gen3 Indexd instance)
            form (str): pick between 'bundle', 'object' or 'all' to return any one of them.
        """
        params = {}

        if start:
            params["start"] = start
        if limit:
            params["limit"] = limit
        if page:
            params["page"] = page
        if form:
            params["form"] = form

        response = self._get(SyncClient, endpoint, params=params)
        return response

    async def async_get_all(
        self,
        endpoint="/ga4gh/drs/v1/objects",
        start=None,
        limit=None,
        page=None,
        form=None,
    ):
        """
        Get a list of bundle, object or both asynchronously.

        Args:
            endpoint (str): pick between '/ga4gh/drs/v1/objects', 'bundle' or 'index' endpoint. (If calling a Gen3 Indexd instance)
            form (str): pick between 'bundle', 'object' or 'all' to return any one of them.
        """
        params = {}

        if start:
            params["start"] = start
        if limit:
            params["limit"] = limit
        if page:
            params["page"] = page
        if form:
            params["form"] = form

        response = await self._get(httpx.AsyncClient, endpoint, params=params)
        return response

    def create(
        self,
        bundles,
        name=None,
        guid=None,
        size=None,
        checksums=None,
        description=None,
        version=None,
        aliases=None,
    ):
        """
        Create a new bundle.

        Args:
            name (str): optional but if not provided will default to guid
            guid (str): optional but if not provided indexd crerates one
            bundles (list): required list of bundle ids and object guids to add in the bundle
            size (int): optional but if not provided indexd calculates it
            checksums (list): list of checksums with type. Optional but if not provided indexd caluclates it
            description (str): optional description of the bundle object
            version (str): optional version of the bundle object
            aliases (list): optional list of aliases related to the bundle
        """
        data = {}
        headers = {"content-type": "application/json"}
        if bundles is None:
            bundles = []
        data["bundles"] = bundles
        if guid:
            data["bundle_id"] = guid
        if size:
            data["size"] = size
        if name:
            data["name"] = name
        if checksums:
            data["checksum"] = checksums
        if description:
            data["description"] = description
        if version:
            data["version"] = version
        if aliases:
            data["aliases"] = aliases
        if self.token:
            headers["Authorization"] = "Bearer " + self.token

        response = self._post(
            SyncClient,
            "bundle",
            headers=headers,
            data=json.dumps(data),
            auth=self.auth,
        )
        return response

    async def async_create(
        self,
        bundles,
        name=None,
        guid=None,
        size=None,
        checksums=None,
        description=None,
        version=None,
        aliases=None,
    ):
        """
        Asynchronously Create a new bundle.

        Args:
            name (str): optional but if not provided will default to guid
            guid (str): optional but if not provided indexd crerates one
            bundles (list): required list of bundle ids and object guids to add in the bundle
            size (int): optional but if not provided indexd calculates it
            checksums (list): list of checksums with type. Optional but if not provided indexd caluclates it
            description (str): optional description of the bundle object
            version (str): optional version of the bundle object
            aliases (list): optional list of aliases related to the bundle
        """
        data = {}
        headers = {"content-type": "application/json"}
        if bundles is None:
            bundles = []
        data["bundles"] = bundles
        if guid:
            data["guid"] = guid
        if size:
            data["size"] = size
        if name:
            data["name"] = name
        if checksums:
            data["checksum"] = checksums
        if description:
            data["description"] = description
        if version:
            data["version"] = version
        if aliases:
            data["aliases"] = aliases
        if self.token:
            headers["Authorization"] = "Bearer " + self.token

        response = await self._post(
            httpx.AsyncClient,
            "bundle",
            headers=headers,
            data=json.dumps(data),
            auth=self.auth,
        )
        return response

    def delete(self, guid):
        """
        Delete bundle according to the guid.

        Args:
            guid (str): guid to be deleted
        """
        headers = {}
        if self.token:
            headers["Authorization"] = "Bearer " + self.token
        response = self._delete(
            SyncClient,
            "bundle",
            guid,
            auth=self.auth,
            headers=headers,
        )
        return response

    async def async_delete(self, guid):
        """
        Delete bundle according to the guid.

        Args:
            guid (str): guid to be deleted
        """
        headers = {}
        if self.token:
            headers["Authorization"] = "Bearer " + self.token
        response = await self._delete(
            httpx.AsyncClient,
            "bundle",
            guid,
            auth=self.auth,
            headers=headers,
        )
        return response

    @retry_and_timeout_wrapper
    @maybe_sync
    async def _get(self, client_cls, *path, **kwargs):
        async with client_cls() as client:
            resp = await client.get(self.url_for(*path), **kwargs)
            return resp

    @timeout_wrapper
    @maybe_sync
    async def _post(self, client_cls, *path, **kwargs):
        async with client_cls() as client:
            resp = await client.post(self.url_for(*path), **kwargs)
            return resp

    @timeout_wrapper
    @maybe_sync
    async def _delete(self, client_cls, *path, **kwargs):
        async with client_cls() as client:
            resp = await client.delete(self.url_for(*path), **kwargs)
            return resp
