import json
import pytest
import uuid
import requests

# import responses
from drsclient import __version__
from drsclient.client import DrsClient
import asyncio

from cdisutilstest.code.indexd_fixture import (
    create_random_index,
    create_random_index_version,
)


def test_version():
    assert __version__ == "0.1.0"


def get_index_doc(has_version=True, urls=list(), add_bundle=False):
    doc = {
        "form": "object",
        "size": 123,
        "urls": ["s3://endpointurl/bucket/key"],
        "hashes": {"md5": "8b9942cf415384b27cadf1f4d2d682e5"},
    }
    if has_version:
        doc["version"] = "1"
    if urls:
        doc["urls"] = urls

    return doc
def create_index_record(index_client):
    i_data = get_index_doc()
    res1 = index_client.create(
        hashes=i_data["hashes"],
        size=i_data["size"],
        urls=i_data["urls"]
        )
    rec1 = res1._doc
    assert rec1

    return rec1["did"], rec1

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
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print(res.status_code)
    assert res.status_code == 200

def test_post_index(index_client, drsclient):
    did, rec1 = create_index_record(index_client)
    assert rec1["did"] == did
    res2 = drsclient.get(did=None)
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print(res2)
    assert res2.status_code == 200

def test_create_bundle(index_client, drsclient):
    did, rec = create_index_record(index_client)
    assert rec["did"]
    res1 = drsclient.create(bundles=[did])
    assert res1.status_code == 200


# def test_bundle_get():
#     client = DrsClient(baseurl="https://binamb.planx-pla.net/", auth=None)
#     assert client.url == "https://binamb.planx-pla.net/"
#     print(client.get("068a03ae-40d2-4360-97f9-defbdf923814"))


# def test_async_bundle_get():
#     client = DrsClient(baseurl="https://binamb.planx-pla.net/", auth=None)
#     assert client.url == "https://binamb.planx-pla.net/"
#     print(asyncio.run(client.async_get("068a03ae-40d2-4360-97f9-defbdf923814")))

# def test_bundle_post():
#     auth="Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImtpZCI6ImZlbmNlX2tleV8yMDIwLTAxLTEzVDIxOjE4OjE3WiJ9.eyJwdXIiOiJhY2Nlc3MiLCJhdWQiOlsib3BlbmlkIiwidXNlciIsImNyZWRlbnRpYWxzIiwiZGF0YSIsImFkbWluIiwiZ29vZ2xlX2NyZWRlbnRpYWxzIiwiZ29vZ2xlX3NlcnZpY2VfYWNjb3VudCIsImdvb2dsZV9saW5rIl0sInN1YiI6IjciLCJpc3MiOiJodHRwczovL2JpbmFtYi5wbGFueC1wbGEubmV0L3VzZXIiLCJpYXQiOjE1OTA2Nzk5OTAsImV4cCI6MTU5MDY4MTE5MCwianRpIjoiNzI2NTY1NmQtN2FjMS00ODU1LWE0ZjctYWQxOGJkYjg1OTZhIiwiY29udGV4dCI6eyJ1c2VyIjp7Im5hbWUiOiJiaW5hbWJAdWNoaWNhZ28uZWR1IiwiaXNfYWRtaW4iOnRydWUsImdvb2dsZSI6eyJwcm94eV9ncm91cCI6bnVsbH0sInByb2plY3RzIjp7fX19LCJhenAiOiIifQ.ihxK74UrAba5Yb0j2nGKUmt_mVtzrLngaURw-gdDEKlQelHOETulQBewFgR4hbjguPLZ8GhhhBO3WleShMNqo-r33A-9AQyqjdQFvlkEXIVNBCE4qLdBJX2JdRkfnVvlskCaZEXptBMLCyEGRlVknv8DkhW1iJIsAYBUhhSeJVDJpZ30981rqdCP_4_0tWl9NTi6f3TwoRTwSPVDfJ_Su3A5KHHcMmngjhCMOLm-fd7VQye5ibaaJjdgcTOCutxRnbr9e6pt5YscJX9tc_8RUiJuM0WeO4pG6WrxgAiAw_yTmKp3Zd4c-aaD4cmi_nHilk7fgbLHsKsZ52YMSPJQBQ"
#     client = DrsClient(baseurl="https://binamb.planx-pla.net/", auth=auth)
#     assert client.url == "https://binamb.planx-pla.net/"
#     print(client.create(bundles=["068a03ae-40d2-4360-97f9-defbdf923814"]))

# def test_async_bundle_post():
#     auth= "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImtpZCI6ImZlbmNlX2tleV8yMDIwLTAxLTEzVDIxOjE4OjE3WiJ9.eyJwdXIiOiJhY2Nlc3MiLCJhdWQiOlsib3BlbmlkIiwidXNlciIsImNyZWRlbnRpYWxzIiwiZGF0YSIsImFkbWluIiwiZ29vZ2xlX2NyZWRlbnRpYWxzIiwiZ29vZ2xlX3NlcnZpY2VfYWNjb3VudCIsImdvb2dsZV9saW5rIl0sInN1YiI6IjciLCJpc3MiOiJodHRwczovL2JpbmFtYi5wbGFueC1wbGEubmV0L3VzZXIiLCJpYXQiOjE1OTA2ODEyNjgsImV4cCI6MTU5MDY4MjQ2OCwianRpIjoiYTg3NWU3NWMtMjllOC00ODhiLTgzNGQtMjBlZWZmNDI0NmE5IiwiY29udGV4dCI6eyJ1c2VyIjp7Im5hbWUiOiJiaW5hbWJAdWNoaWNhZ28uZWR1IiwiaXNfYWRtaW4iOnRydWUsImdvb2dsZSI6eyJwcm94eV9ncm91cCI6bnVsbH0sInByb2plY3RzIjp7fX19LCJhenAiOiIifQ.ey2sP7A_xWf8HWSONRVjXzKf0os-_X17PL8cMhI-BMEr2wMXwvvrIOpZBo7g9AFLmPuiJFVTyfd4a0ljUVp1WGu1j5ZoGMTOfEhOiSusdOogNqcLNoeXyILnUDR4i6CIu1OqDKQmL5L6H1f3e7VBb4Lh9eC5QxS-lF0n1gcWFApyArOaIh5lz0oKeyuk3XgNMMFiUEvXLwn076iyoQNNbyESeYhYIYwtbenAMf5EkrIn8qKVjABHOlfKfYX-AB4uX_oTGz10L2FlWJ4CQtZBaB0nqMQHDJqQsh73-gTDRGHRxv3CycQDOY8JdaiCYKOWpbK4vfBDXdyaSHD_0qnU2Q"
#     client = DrsClient(baseurl="https://binamb.planx-pla.net/", auth=auth)
#     assert client.url == "https://binamb.planx-pla.net/"
#     print(asyncio.run(client.async_create(bundles=["068a03ae-40d2-4360-97f9-defbdf923814"])))

# def test_bundle_delete():
#     auth = "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImtpZCI6ImZlbmNlX2tleV8yMDIwLTAxLTEzVDIxOjE4OjE3WiJ9.eyJwdXIiOiJhY2Nlc3MiLCJhdWQiOlsib3BlbmlkIiwidXNlciIsImNyZWRlbnRpYWxzIiwiZGF0YSIsImFkbWluIiwiZ29vZ2xlX2NyZWRlbnRpYWxzIiwiZ29vZ2xlX3NlcnZpY2VfYWNjb3VudCIsImdvb2dsZV9saW5rIl0sInN1YiI6IjciLCJpc3MiOiJodHRwczovL2JpbmFtYi5wbGFueC1wbGEubmV0L3VzZXIiLCJpYXQiOjE1OTA2OTEwMjIsImV4cCI6MTU5MDY5MjIyMiwianRpIjoiYThkZjdkNWItNmQ2ZS00ZWVhLWJiNGYtMTdlYjdhY2JkOGY0IiwiY29udGV4dCI6eyJ1c2VyIjp7Im5hbWUiOiJiaW5hbWJAdWNoaWNhZ28uZWR1IiwiaXNfYWRtaW4iOnRydWUsImdvb2dsZSI6eyJwcm94eV9ncm91cCI6bnVsbH0sInByb2plY3RzIjp7fX19LCJhenAiOiIifQ.EHZgSa1qmQrG-ArHeMUP4pI7jzKNE2F-Rs4k5BEQzrfx3tai0iKvpJ64eLV8FjMhQl4V-ytDbnQbjiq9f9r6Kjg0Z5KqUqYhJtiqSpTMIL9ce9iPNS8uqlGwQVYXxEheO9Qlc8XGgNymPF-XA42v45qVEROvjQ05Q8qajDngCQ8IYulTfKdXxXCt8VR1O9rk-GosSooxbxnCykYkJF2CMOtY0V51OrIe_YqAhD_1UVXjRTfAi--RY06iwfCwgksx_6sspZlQpKhzfvXPdyb8UyHKMxOaEp-sesdteP562DUKTtKbmqV5M-uvxP91qxVGoexHAxkJ_sj-P90mkSeUUw"
#     client = DrsClient(baseurl="https://binamb.planx-pla.net/", auth=auth)
#     assert client.url == "https://binamb.planx-pla.net/"
#     guid = str(uuid.uuid4())
#     resp = client.create(bundles=["068a03ae-40d2-4360-97f9-defbdf923814"], guid=guid)
#     assert resp.status_code == 200
#     resp1 = client.delete(guid)
#     assert resp1.status_code == 200


# def test_async_bundle_delete():
#     auth = "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImtpZCI6ImZlbmNlX2tleV8yMDIwLTAxLTEzVDIxOjE4OjE3WiJ9.eyJwdXIiOiJhY2Nlc3MiLCJhdWQiOlsib3BlbmlkIiwidXNlciIsImNyZWRlbnRpYWxzIiwiZGF0YSIsImFkbWluIiwiZ29vZ2xlX2NyZWRlbnRpYWxzIiwiZ29vZ2xlX3NlcnZpY2VfYWNjb3VudCIsImdvb2dsZV9saW5rIl0sInN1YiI6IjciLCJpc3MiOiJodHRwczovL2JpbmFtYi5wbGFueC1wbGEubmV0L3VzZXIiLCJpYXQiOjE1OTA2OTEwMjIsImV4cCI6MTU5MDY5MjIyMiwianRpIjoiYThkZjdkNWItNmQ2ZS00ZWVhLWJiNGYtMTdlYjdhY2JkOGY0IiwiY29udGV4dCI6eyJ1c2VyIjp7Im5hbWUiOiJiaW5hbWJAdWNoaWNhZ28uZWR1IiwiaXNfYWRtaW4iOnRydWUsImdvb2dsZSI6eyJwcm94eV9ncm91cCI6bnVsbH0sInByb2plY3RzIjp7fX19LCJhenAiOiIifQ.EHZgSa1qmQrG-ArHeMUP4pI7jzKNE2F-Rs4k5BEQzrfx3tai0iKvpJ64eLV8FjMhQl4V-ytDbnQbjiq9f9r6Kjg0Z5KqUqYhJtiqSpTMIL9ce9iPNS8uqlGwQVYXxEheO9Qlc8XGgNymPF-XA42v45qVEROvjQ05Q8qajDngCQ8IYulTfKdXxXCt8VR1O9rk-GosSooxbxnCykYkJF2CMOtY0V51OrIe_YqAhD_1UVXjRTfAi--RY06iwfCwgksx_6sspZlQpKhzfvXPdyb8UyHKMxOaEp-sesdteP562DUKTtKbmqV5M-uvxP91qxVGoexHAxkJ_sj-P90mkSeUUw"
#     client = DrsClient(baseurl="https://binamb.planx-pla.net/", auth=auth)
#     assert client.url == "https://binamb.planx-pla.net/"
#     guid = str(uuid.uuid4())
#     resp = client.create(bundles=["068a03ae-40d2-4360-97f9-defbdf923814"], guid=guid)
#     assert resp.status_code == 200
#     resp1 = asyncio.run(client.async_delete(guid))
#     assert resp1.status_code == 200