"""Persistent recording of a workflow executions."""

import os
import warnings
from typing import Optional, Callable

from .interface import WorkflowDbClient
from .pymongo import PyMongoWorkflowDbClient  # noqa F401
from .besdb import BesWorkflowDbClient  # noqa F401
from .mongita import MemoryWorkflowDbClient  # noqa F401
from .dummy import DummyWorkflowDbClient  # noqa F401

DEFAULT_DB_TYPE = "dummy"


def init_db_client(*args, db_type: Optional[str] = None, **kwargs) -> WorkflowDbClient:
    """Initializes a database client based on the specified `db_type`.

    :param db_type: The type of database client to initialize.
                    If not specified, defaults to `DEFAULT_DB_TYPE`.
                    Supported values include:

                    - **"besdb"**: Requires the following additional parameters:
                      - **url** (str): URL for connecting to the BES database.
                      - **initiator** (str): Initiator from which the request originates.
                      - **host** (str): Hostname from which the request originates.
                      - **port** (int): Port number from which the request originates.
                      - **request_id** (str): Unique identifier for the request.

                    - **"pymongo"**: Requires the following additional parameters:
                      - **url** (str): Connection URL for the MongoDB instance.
                      - **database** (str): Name of the database to access.
                      - **collection** (str): Name of the collection within the database.

                    - **"memory"**: An in-memory database type. No additional parameters required.

                    - **"dummy"**: A placeholder database type for testing or development purposes. No additional parameters required.

    :param args: see `db_type`.
    :param kwargs: see `db_type`.

    :return: An instance of `WorkflowDbClient` specific to the specified `db_type`.
    """
    if db_type is None:
        url = os.environ.get("PYPUSHFLOW_MONGOURL", None)
        if url:
            warnings.warn(
                "Using BESDB environment variables is deprecated", DeprecationWarning
            )
            db_type = "besdb"
            kwargs = {
                "url": url,
                "initiator": os.environ.get("PYPUSHFLOW_INITIATOR"),
                "host": os.environ.get("PYPUSHFLOW_HOST"),
                "port": os.environ.get("PYPUSHFLOW_PORT"),
                "request_id": os.environ.get("PYPUSHFLOW_OBJECTID"),
            }
        else:
            db_type = DEFAULT_DB_TYPE
    db_client_class = WorkflowDbClient.get_dbclient_class(db_type)
    return db_client_class(*args, **kwargs)


def register_actorinfo_filter(method: Callable):
    WorkflowDbClient.register_actorinfo_filter(method)
