import sys
import numpy
import pytest
import mongomock

try:
    from bson.objectid import ObjectId
except Exception:
    ObjectId = None

from pypushflow.persistence import init_db_client
from pypushflow.persistence import WorkflowDbClient
from pypushflow.persistence import DummyWorkflowDbClient
from pypushflow.persistence import PyMongoWorkflowDbClient


@pytest.fixture()
def dummy_client():
    client = init_db_client(db_type="dummy")
    client.connect()
    return client


@pytest.fixture()
def memory_client():
    if sys.version_info < (3, 7):
        pytest.skip("mongita does not support python<3.7")
    client = init_db_client(db_type="memory")
    client.connect()
    yield client
    client.disconnect()


@pytest.fixture()
def mock_mongo():
    with mongomock.patch(on_new="create"):
        yield


@pytest.fixture()
def pymongo_client(mock_mongo):
    client = init_db_client(
        db_type="pymongo",
        url="mongodb://user:pwd@localhost:27017/mydatabase",
        database="mydatabase",
        collection="mycollection",
    )
    client.connect()
    yield client
    client.disconnect()


@pytest.fixture()
def besdb_client(mock_mongo):
    client = init_db_client(
        db_type="besdb",
        url="mongodb://user:pwd@localhost:27017/bes",
        initiator="PyPushflowUnitTests",
        host="unknown",
        port=-1,
        request_id=str(ObjectId()) if ObjectId else "unknown",
    )
    client.connect()
    yield client
    client.disconnect()


def test_workflow_dummy(dummy_client) -> None:
    _test_workflow_persistency(dummy_client)


def test_workflow_memory(memory_client) -> None:
    _test_workflow_persistency(memory_client)


def test_workflow_pymongo(pymongo_client) -> None:
    _test_workflow_persistency(pymongo_client)


def test_workflow_bes(besdb_client) -> None:
    _test_workflow_persistency(besdb_client)


def test_actor_dummy(dummy_client) -> None:
    _test_actor_persistency(dummy_client)


def test_actor_memory(memory_client) -> None:
    _test_actor_persistency(memory_client)


def test_actor_pymongo(pymongo_client) -> None:
    _test_actor_persistency(pymongo_client)


def test_actor_bes(besdb_client) -> None:
    _test_actor_persistency(besdb_client)


def _test_workflow_persistency(client: WorkflowDbClient) -> None:
    is_dummy = isinstance(client, DummyWorkflowDbClient)
    is_pymongo = isinstance(client, PyMongoWorkflowDbClient)

    name = "test_startWorkflow"
    client.startWorkflow(name)
    info = client.getWorkflowInfo()
    if is_dummy:
        assert info is None
    else:
        assert info["status"], "started"

    client.updateWorkflowInfo({"status": "error"})
    info = client.getWorkflowInfo()
    if is_dummy:
        assert info is None
    else:
        assert info["status"], "error"

    client.updateWorkflowInfo({"data": {"a": 1}})
    info = client.getWorkflowInfo()
    if is_dummy:
        assert info is None
    else:
        assert info["data"], {"a": 1}

    client.updateWorkflowInfo({"data": {"a": 2}})
    info = client.getWorkflowInfo()
    if is_dummy:
        assert info is None
    else:
        assert info["data"], {"a": 2}

    bad_data = {"exception": RuntimeError("error"), "numpy_array": numpy.arange(3)}
    client.updateWorkflowInfo(bad_data)
    info = client.getWorkflowInfo()
    if is_dummy:
        assert info is None
    elif is_pymongo:
        for k, v in bad_data.items():
            assert info[k] == repr(v)
    else:
        for k, v in bad_data.items():
            assert type(info[k]) is type(v)
            assert repr(info[k]) == repr(v)

    client.endWorkflow()
    info = client.getWorkflowInfo()
    if is_dummy:
        assert info is None
    else:
        assert info["status"], "error"


def _test_actor_persistency(client: WorkflowDbClient) -> None:
    is_dummy = isinstance(client, DummyWorkflowDbClient)
    is_pymongo = isinstance(client, PyMongoWorkflowDbClient)

    name = "test_startWorkflow"
    client.startWorkflow(name=name)

    actorName1 = "TestActor1"
    actorId1 = client.startActor(actorName1)
    info = client.getActorInfo(actorId1)
    if is_dummy:
        assert info is None
    else:
        assert info["status"], "started"

    client.updateActorInfo(actorId1, {"status": "error"})
    info = client.getActorInfo(actorId1)
    if is_dummy:
        assert info is None
    else:
        assert info["status"], "error"

    client.endActor(actorId1)
    info = client.getActorInfo(actorId1)
    if is_dummy:
        assert info is None
    else:
        assert info["status"], "error"

    actorName2 = "TestActor2"
    actorId2 = client.startActor(name=actorName2)
    info = client.getActorInfo(actorId2)
    if is_dummy:
        assert info is None
    else:
        assert info["status"], "started"

    client.updateActorInfo(actorId2, {"data": {"a": 1}})
    info = client.getActorInfo(actorId2)
    if is_dummy:
        assert info is None
    else:
        assert info["data"], {"a": 1}

    client.updateActorInfo(actorId2, {"data": {"a": 2}})
    info = client.getActorInfo(actorId2)
    if is_dummy:
        assert info is None
    else:
        assert info["data"], {"a": 1}

    client.endActor(actorId2)
    info = client.getActorInfo(actorId2)
    if is_dummy:
        assert info is None
    else:
        assert info["status"], "finished"

    actorName3 = "TestActor3"
    bad_data = {"exception1": RuntimeError("error1"), "numpy_array1": numpy.arange(3)}
    actorId3 = client.startActor(name=actorName3, info=bad_data)
    info = client.getActorInfo(actorId3)
    if is_dummy:
        assert info is None
    elif is_pymongo:
        # The type is unexpectidly preserved (might be because of mongomock)
        for k, v in bad_data.items():
            assert type(info[k]) is type(v)
            assert repr(info[k]) == repr(v)
    else:
        for k, v in bad_data.items():
            assert type(info[k]) is type(v)
            assert repr(info[k]) == repr(v)

    bad_data = {"exception2": RuntimeError("error2"), "numpy_array2": numpy.arange(4)}
    client.updateActorInfo(actorId3, bad_data)
    info = client.getActorInfo(actorId3)
    if is_dummy:
        assert info is None
    elif is_pymongo:
        for k, v in bad_data.items():
            assert info[k] == repr(v)
    else:
        for k, v in bad_data.items():
            assert type(info[k]) is type(v)
            assert repr(info[k]) == repr(v)
