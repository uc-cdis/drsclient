import pytest
from cdisutilstest.code.conftest import (
    indexd_server,
    indexd_client,
    setup_database,
    create_user,
    clear_database,
    create_user,
)
from drsclient.client import DrsClient


@pytest.fixture(scope="function")
def index_client(indexd_client):
    return indexd_client


@pytest.fixture(scope="function")
def drs_client(indexd_server):
    """
    Returns a DrsClient. This will delete any documents,
    aliases, or users made by this
    client after the test has completed.
    Currently the default user is the admin user
    Runs once per test.
    """
    client = DrsClient(baseurl=indexd_server.baseurl, auth=create_user("user", "user"))
    yield client
    clear_database()


@pytest.fixture(scope="function")
def drsclient(drs_client):
    return drs_client
