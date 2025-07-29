import socket
import getpass
import logging
import hashlib
from typing import Optional

from .pymongo import PyMongoWorkflowDbClient

try:
    from bson.objectid import ObjectId
except Exception:
    ObjectId = None


_logger = logging.getLogger(__name__)


class BesWorkflowDbClient(PyMongoWorkflowDbClient, register_name="besdb"):
    """Client of the BES Mongo database for storing workflow executions."""

    def __init__(
        self,
        url: str,
        request_id: Optional[str] = None,
        initiator: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[str] = None,
    ):
        if not request_id:
            raise ValueError("The request ID needs to be provided")
        if not host:
            host = socket.gethostname()
        if not initiator:
            initiator = getpass.getuser()
        if not port:
            port = ""

        self._request_id = _create_objectid(str(request_id))

        self._initial_workflow_info = {
            "_id": self._request_id,
            "initiator": str(initiator),
            "host": str(host),
            "port": str(port),
            "Request ID": str(request_id),
        }

        super().__init__(url, "bes", "bes")

    def _generateInitialWorkflowInfo(self) -> dict:
        return dict(self._initial_workflow_info)

    def generateWorkflowId(self) -> ObjectId:
        return self._request_id


def _create_objectid(request_id: str) -> ObjectId:
    try:
        return ObjectId(request_id)
    except Exception:
        pass

    hash_bytes = hashlib.blake2s(request_id.encode(), digest_size=12).digest()
    object_id = ObjectId(hash_bytes)

    _logger.warning(
        "'%s' is not a valid BSON Object ID. Use its hash '%s' instead.",
        request_id,
        object_id,
    )

    return object_id
