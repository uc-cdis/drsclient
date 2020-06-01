import pytest
from cdisutilstest.code.conftest import (
    indexd_server,
    indexd_client,
    setup_database,
    create_user,
    clear_database,
)
from drsclient.client import DrsClient


@pytest.fixture(scope="function")
def index_client(indexd_client):
    """
    Handles getting all the docs from an
    indexing endpoint. Currently this is changing from
    signpost to indexd, so we'll use just indexd_client now.
    I.E. test to a common interface this could be multiply our
    tests:
    https://docs.pytest.org/en/latest/fixture.html#parametrizing-fixtures
    """
    return indexd_client

@pytest.fixture(scope="function")
def drs_client(indexd_server):
    """
    Returns a IndexClient. This will delete any documents,
    aliases, or users made by this
    client after the test has completed.
    Currently the default user is the admin user
    Runs once per test.
    """
    # setup_database()
    client = DrsClient(
        baseurl=indexd_server.baseurl, auth="admin"
    )
    yield client
    clear_database()

@pytest.fixture(scope="function")
def drsclient(drs_client):
    """
    Handles getting all the docs from an
    indexing endpoint. Currently this is changing from
    signpost to indexd, so we'll use just indexd_client now.
    I.E. test to a common interface this could be multiply our
    tests:
    https://docs.pytest.org/en/latest/fixture.html#parametrizing-fixtures
    """
    return drs_client