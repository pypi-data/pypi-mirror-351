try:
    from bson.objectid import ObjectId
    from mongita import MongitaClientMemory
except Exception:
    ObjectId = None
    MongitaClientMemory = None
from .mongo import MongoWorkflowDbClient


class MemoryWorkflowDbClient(MongoWorkflowDbClient, register_name="memory"):
    """Client of an in-memory Mongo database for storing workflow executions.
    Used for testing purposes.
    """

    def connect(self):
        if MongitaClientMemory is None:
            return
        self._collection = MongitaClientMemory()["ppf"]["ppf"]

    def disconnect(self):
        self._collection = None

    def generateWorkflowId(self) -> ObjectId:
        return ObjectId()

    def generateActorId(self) -> ObjectId:
        return ObjectId()

    def _appendActorInfo(self, actorInfo: dict):
        workflowInfo = self._getWorkflowInfo()
        workflowInfo["actors"].append(actorInfo)
        self._setWorkflowInfo(workflowInfo)
