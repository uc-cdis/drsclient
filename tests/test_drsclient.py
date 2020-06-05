import json
import pytest
import uuid
import requests
from drsclient import __version__
from drsclient.client import DrsClient
import asyncio

from cdisutilstest.code.indexd_fixture import (
    create_random_index,
    create_random_index_version,
)


def test_version():
    assert __version__ == "0.1.0"


def get_index_doc():
    doc = {
        "form": "object",
        "size": 123,
        "urls": ["s3://endpointurl/bucket/key"],
        "hashes": {"md5": "8b9942cf415384b27cadf1f4d2d682e5"},
    }
    return doc


def create_index_record(index_client):
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
    doc = create_random_index(index_client)
    latest = index_client.get_latest_version(doc.did)
    assert latest.did == doc.did
    assert latest.file_name == doc.file_name
    assert latest.hashes == doc.hashes


def test_check_status(index_client, drs_client):
    res = drs_client.check_status()
    print(res.status_code)
    assert res.status_code == 200


def test_post_index(index_client, drs_client):
    rec = create_index_record(index_client)
    did = rec["did"]
    res2 = drs_client.get(did=did)
    print(res2.json())


def test_create_bundle(index_client, drs_client):
    rec = create_index_record(index_client)
    did = rec["did"]
    res1 = drs_client.create(bundles=[did])
    rec1 = res1.json()
    contents = json.loads(rec1["contents"])
    assert res1.status_code == 200
    assert len(contents) == 1
    assert contents[0]["id"] == did


def test_async_create_bundle(index_client, drs_client):
    rec = create_index_record(index_client)
    did = rec["did"]
    res1 = asyncio.run(drs_client.async_create(bundles=[did]))
    rec1 = res1.json()
    assert res1.status_code == 200
    contents = json.loads(rec1["contents"])
    assert len(contents) == 1
    assert contents[0]["id"] == did


def test_get_bundle(index_client, drs_client):
    rec = create_index_record(index_client)
    did = rec["did"]
    res1 = drs_client.create(bundles=[did])
    rec1 = res1.json()
    print("REC1: {}".format(rec1))
    assert res1.status_code == 200
    bundle_id = rec1["bundle_id"]
    res2 = drs_client.get(bundle_id, expand=True)
    assert res2.status_code == 200
    rec2 = res2.json()
    print("REC2: {}".format(rec2))
    assert rec2["id"] == bundle_id
    assert rec2["name"] == rec1["name"]


def test_async_get_bundle(index_client, drs_client):
    rec = create_index_record(index_client)
    did = rec["did"]
    res1 = asyncio.run(drs_client.async_create(bundles=[did]))
    rec1 = res1.json()
    print("REC1: {}".format(rec1))
    assert res1.status_code == 200
    bundle_id = rec1["bundle_id"]
    res2 = asyncio.run(drs_client.async_get(bundle_id, expand=True))
    assert res2.status_code == 200
    rec2 = res2.json()
    print("REC2: {}".format(rec2))
    assert rec2["id"] == bundle_id
    assert rec2["name"] == rec1["name"]


def test_layered_bundle(index_client, drs_client):
    """
    Bundle1
        +-Object1
        +-Bundel2
            +-Object2
            +-Object3
    """
    obj1 = create_index_record(index_client)
    obj2 = create_index_record(index_client)
    obj3 = create_index_record(index_client)
    bnd2 = drs_client.create(bundles=[obj2["did"], obj3["did"]])
    assert bnd2.status_code == 200
    rec2 = bnd2.json()
    bnd1 = drs_client.create(bundles=[obj1["did"], rec2["bundle_id"]])
    assert bnd1.status_code == 200
    rec1 = bnd1.json()
    res = drs_client.get(rec1["bundle_id"], expand=True)
    rec = res.json()
    assert len(rec["contents"]) == 2
    assert len(rec["contents"][1]["contents"]) == 2


def test_delete_bundle(index_client, drs_client):
    rec = create_index_record(index_client)
    did = rec["did"]
    res1 = drs_client.create(bundles=[did])
    rec1 = res1.json()
    bundle_id = rec1["bundle_id"]
    assert res1.status_code == 200
    res2 = drs_client.delete(bundle_id)
    assert res2.status_code == 200
    res3 = drs_client.get(bundle_id)
    assert res3.status_code == 404


def test_async_delete_bundle(index_client, drs_client):
    rec = create_index_record(index_client)
    did = rec["did"]
    res1 = drs_client.create(bundles=[did])
    rec1 = res1.json()
    bundle_id = rec1["bundle_id"]
    assert res1.status_code == 200
    res2 = asyncio.run(drs_client.async_delete(bundle_id))
    assert res2.status_code == 200
    res3 = drs_client.get(bundle_id)
    assert res3.status_code == 404


def test_get_bundle_id_not_exist(index_client, drs_client):
    res = drs_client.get("09ujh1f0938hj08hjf082jf08j")
    print(res)
    assert res.status_code == 404


def test_no_id(index_client, drs_client):
    fake_id = "20ihjf2038ehjfv0289"
    res = drs_client.create(bundles=[fake_id])
    assert res.status_code == 404
