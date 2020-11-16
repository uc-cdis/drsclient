import json
import uuid
import asyncio
import respx
import pytest


def get_index_doc():
    doc = {
        "form": "object",
        "size": 123,
        "urls": ["s3://endpointurl/bucket/key"],
        "hashes": {"md5": "8b9942cf415384b27cadf1f4d2d682e5"},
    }
    return doc


def create_index_record(index_client):
    """
    Create an indexd record
    """
    i_data = get_index_doc()
    res1 = index_client.create(
        hashes=i_data["hashes"], size=i_data["size"], urls=i_data["urls"]
    )
    rec1 = res1._doc
    return rec1


def test_get_latest_version(index_client):
    """
    Args:
        index_client (indexclient.client.IndexClient): IndexClient Pytest Fixture
    """
    doc = create_index_record(index_client)
    latest = index_client.get_latest_version(doc["did"])
    assert latest.did == doc["did"]
    assert latest.file_name == doc["file_name"]
    assert latest.hashes == doc["hashes"]


def test_check_status(index_client, drs_client):
    """
    Check status of the indexd server
    """
    res = drs_client.check_status()
    assert res.status_code == 200


def test_post_index(index_client, drs_client):
    rec = create_index_record(index_client)
    did = rec["did"]
    res2 = drs_client.get(guid=did)
    assert res2.status_code == 200


@pytest.mark.parametrize("async_client", [True, False])
def test_create_bundle(index_client, drs_client, async_client):
    """
    Test to create bundle using both sync and async method in an indexd server.
    """
    rec = create_index_record(index_client)
    did = rec["did"]
    loop = asyncio.get_event_loop()
    res1 = (
        loop.run_until_complete(drs_client.async_create(bundles=[did]))
        if async_client
        else drs_client.create(bundles=[did])
    )
    rec1 = res1.json()
    contents = json.loads(rec1["contents"])
    assert res1.status_code == 200
    assert len(contents) == 1
    assert contents[0]["id"] == did


@pytest.mark.parametrize("async_client", [True, False])
def test_create_bundle_with_optional_fields(index_client, drs_client, async_client):
    """
    Test to create bundle with optional fields checksums and size
    """
    rec = create_index_record(index_client)
    did = rec["did"]
    size = 10
    bundle_id = str(uuid.uuid4())
    checksums = [
        {
            "checksum": "bc52d6bfe3ac965e069109dbd7d15e0ccaaa55678f6e2a6664bee2edf8ae1b2b",  # pragma: allowlist secret
            "type": "sha256",
        },
        {
            "checksum": "a8f5f167f44f4964e6c998dee827110c",  # pragma: allowlist secret
            "type": "md5",
        },
    ]
    loop = asyncio.get_event_loop()
    res1 = (
        loop.run_until_complete(
            drs_client.async_create(
                bundles=[did], guid=bundle_id, checksums=checksums, size=size
            )
        )
        if async_client
        else drs_client.create(
            bundles=[did], guid=bundle_id, checksums=checksums, size=size
        )
    )
    assert res1.status_code == 200
    rec1 = res1.json()
    res2 = drs_client.get(bundle_id)
    rec2 = res2.json()
    for checksum in rec2["checksums"]:
        assert checksum in checksums
    assert rec2["size"] == size


@pytest.mark.parametrize("async_client", [True, False])
def test_create_bundle_with_incorrect_optional_fields(
    index_client, drs_client, async_client
):
    """
    Test to create bundle using incorrect checksums
    """
    rec = create_index_record(index_client)
    did = rec["did"]
    bundle_id = str(uuid.uuid4())
    checksums = [
        {
            "checksum": "bc52d6bfe3ac965e069109dbd7d15e0ccaaa55678f6e2a6664bee2edf8ae1b2basd",
            "type": "sha256",
        },
        {"checksum": "a8f5f167f44f4964e6c998dee827110casdsa", "type": "md5"},
    ]
    loop = asyncio.get_event_loop()
    res1 = (
        loop.run_until_complete(
            drs_client.async_create(bundles=[did], guid=bundle_id, checksums=checksums)
        )
        if async_client
        else drs_client.create(bundles=[did], guid=bundle_id, checksums=checksums)
    )
    assert res1.status_code == 400


@pytest.mark.parametrize("async_client", [True, False])
def test_get_drs_record(index_client, drs_client, async_client):
    """
    Test to get a drs record using both sync and async method.
    """
    rec = create_index_record(index_client)
    did = rec["did"]
    loop = asyncio.get_event_loop()
    res2 = (
        loop.run_until_complete(drs_client.async_get(guid=did))
        if async_client
        else drs_client.get(guid=did)
    )
    assert res2.status_code == 200


@pytest.mark.parametrize("async_client", [True, False])
def test_get_bundle(index_client, drs_client, async_client):
    """
    Test to get bundle format record using sync and async method in an indexd server.
    """
    rec = create_index_record(index_client)

    did = rec["did"]
    bundle_id = str(uuid.uuid4())
    name = "Small Bundle"
    size = 50
    description = "This is a small bundle"
    version = "123"
    aliases = ["abcde", "efghi"]

    res1 = drs_client.create(
        bundles=[did],
        name=name,
        guid=bundle_id,
        size=size,
        description=description,
        version=version,
        aliases=aliases,
    )

    # get with /bundle endpoint
    rec1 = res1.json()
    assert res1.status_code == 200
    bundle_id = rec1["bundle_id"]
    loop = asyncio.get_event_loop()
    res2 = (
        loop.run_until_complete(drs_client.async_get(bundle_id, "bundle", expand=True))
        if async_client
        else drs_client.get(bundle_id, "bundle", expand=True)
    )
    assert res2.status_code == 200
    rec2 = res2.json()
    assert rec2["id"] == bundle_id
    assert rec2["name"] == rec1["name"]
    assert rec2["size"] == size
    assert rec2["description"] == description
    assert rec2["version"] == version
    assert rec2["aliases"] == aliases

    # get with /ga4gh/drs/v1/objects endpoint
    rec3 = (
        loop.run_until_complete(drs_client.async_get(bundle_id, expand=True))
        if async_client
        else drs_client.get(bundle_id, expand=True)
    )
    assert rec3.status_code == 200
    rec3 = rec3.json()
    assert rec3["id"] == bundle_id
    assert rec3["name"] == rec1["name"]
    assert rec3["size"] == size
    assert rec3["description"] == description
    assert rec3["version"] == version
    assert rec3["aliases"] == aliases


@pytest.mark.parametrize("async_client", [True, False])
def test_get_all(index_client, drs_client, async_client):
    """
    Test to get all 300 records using sync and async method with all the bundle, object and drs endpoint from indexd.
    """
    # create 100 files and bundles
    for _ in range(100):
        rec = create_index_record(index_client)
        drs_client.create(bundles=[rec["did"]])

    loop = asyncio.get_event_loop()

    res1 = (
        loop.run_until_complete(drs_client.async_get_all(limit=300))
        if async_client
        else drs_client.get_all(limit=300)
    )
    assert res1.status_code == 200
    rec1 = res1.json()
    assert len(rec1["drs_objects"]) == 200

    res2 = (
        loop.run_until_complete(drs_client.async_get_all(form="bundle", limit=300))
        if async_client
        else drs_client.get_all(form="bundle", limit=300)
    )
    assert res2.status_code == 200
    rec2 = res2.json()
    assert len(rec2["drs_objects"]) == 100

    res3 = (
        loop.run_until_complete(drs_client.async_get_all(form="object", limit=300))
        if async_client
        else drs_client.get_all(form="object", limit=300)
    )
    assert res3.status_code == 200
    rec3 = res3.json()
    assert len(rec3["drs_objects"]) == 100


@pytest.mark.parametrize("async_client", [True, False])
def test_delete_bundle(index_client, drs_client, async_client):
    """
    Test to delete bundle using sync and async method in the indexd server.
    """
    rec = create_index_record(index_client)
    did = rec["did"]
    res1 = drs_client.create(bundles=[did])
    rec1 = res1.json()
    bundle_id = rec1["bundle_id"]
    assert res1.status_code == 200
    loop = asyncio.get_event_loop()

    res2 = (
        loop.run_until_complete(drs_client.async_delete(bundle_id))
        if async_client
        else drs_client.delete(bundle_id)
    )
    assert res2.status_code == 200
    res3 = drs_client.get(bundle_id)
    assert res3.status_code == 404


@pytest.mark.parametrize("async_client", [True, False])
@respx.mock
def test_access_endpoint(index_client, drs_client, async_client):
    """
    Test to get a presigned url using both sync and async client.
    """
    rec = create_index_record(index_client)
    did = rec["did"]
    protocol = "s3"
    full_url = drs_client.url + "/ga4gh/drs/v1/objects/" + did + "/access/" + protocol
    request = respx.get(full_url, status_code=200)
    loop = asyncio.get_event_loop()

    res3 = (
        loop.run_until_complete(drs_client.async_download(did, protocol))
        if async_client
        else drs_client.download(did, protocol)
    )
    assert request.called
    assert res3.status_code == 200


def test_get_bundle_id_not_exist(index_client, drs_client):
    res = drs_client.get("09ujh1f0938hj08hjf082jf08j")
    assert res.status_code == 404
