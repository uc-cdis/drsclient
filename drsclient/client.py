import json
import warnings
import httpx
import backoff
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


def json_dumps(data):
    return json.dumps({k: v for (k, v) in data.items() if v is not None})


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
    def __init__(self, baseurl, auth=None):
        self.auth = auth
        self.url = baseurl

    def url_for(self, *path):
        subpath = "/".join(path).lstrip("/")
        return "{}/{}".format(self.url.rstrip("/"), subpath)

    def check_status(self):
        """Check that the API we are trying to communicate with is online"""
        resp = httpx.get(self.url + "/index")
        return resp

    def get(self, guid, endpoint="/ga4gh/drs/v1/objects", expand=False):
        params = {"expand": expand}
        response = self._get(SyncClient, endpoint, guid, params=params)
        return response

    async def async_get(self, guid, endpoint="/ga4gh/drs/v1/objects", expand=False):
        params = {"expand": expand}
        response = await self._get(httpx.AsyncClient, endpoint, guid, params=params)
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
            endpoint (str): pick between '/ga4gh/drs/v1/objects', 'bundle' or 'index' endpoint.
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
        json = {}
        if bundles is None:
            bundles = []
        json["bundles"] = bundles
        if guid:
            json["bundle_id"] = guid
        if size:
            json["size"] = size
        if name:
            json["name"] = name
        if checksums:
            json["checksum"] = checksums
        if description:
            json["description"] = description
        if version:
            json["version"] = version
        if aliases:
            json["aliases"] = aliases

        response = self._post_bundle(
            SyncClient,
            "bundle",
            headers={"content-type": "application/json"},
            data=json_dumps(json),
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
        json = {}
        if bundles is None:
            bundles = []
        json["bundles"] = bundles
        if guid:
            json["guid"] = guid
        if size:
            json["size"] = size
        if name:
            json["name"] = name
        if checksums:
            json["checksum"] = checksums
        if description:
            json["description"] = description
        if version:
            json["version"] = version
        if aliases:
            json["aliases"] = aliases

        response = await self._post_bundle(
            httpx.AsyncClient,
            "bundle",
            headers={"content-type": "application/json"},
            data=json_dumps(json),
            auth=self.auth,
        )
        return response

    def delete(self, guid):
        """
        Delete bundle according to the guid.

        Args:
            guid (str): guid to be deleted
        """
        response = self._delete_bundle(
            SyncClient,
            "bundle",
            guid,
            auth=self.auth,
        )
        return response

    async def async_delete(self, guid):
        """
        Delete bundle according to the guid.

        Args:
            guid (str): guid to be deleted
        """
        response = await self._delete_bundle(
            httpx.AsyncClient,
            "bundle",
            guid,
            auth=self.auth,
        )
        return response

    # TODO: function to get presigned url. Add both sync and async. Protocol options
    #       get_access_url
    @maybe_sync
    async def _get(self, client_cls, *path, **kwargs):
        async with client_cls() as client:
            resp = await client.get(self.url_for(*path), **kwargs)
            return resp

    @maybe_sync
    async def _post_bundle(self, client_cls, *path, **kwargs):
        async with client_cls() as client:
            resp = await client.post(self.url_for(*path), **kwargs)
            return resp

    @maybe_sync
    async def _delete_bundle(self, client_cls, *path, **kwargs):
        async with client_cls() as client:
            resp = await client.delete(self.url_for(*path), **kwargs)
            return resp