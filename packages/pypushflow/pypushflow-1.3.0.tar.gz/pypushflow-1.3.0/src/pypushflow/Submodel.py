import pprint
from typing import Optional
from pypushflow.ThreadCountingActor import ThreadCountingActor
from pypushflow.logutils import PyPushflowLoggedObject


class Port(ThreadCountingActor):
    def __init__(self, errorHandler, name, **kw):
        super().__init__(name=errorHandler.name + "." + name, **kw)
        self.errorHandler = errorHandler
        self.listActor = []
        self.inPortTrigger = None

    def connect(self, actor):
        self.logger.debug("connectig to '%s'", actor.name)
        self.listActor.append(actor)

    def setTrigger(self, trigger):
        self.inPortTrigger = trigger

    def trigger(self, inData):
        self.logger.info(
            "triggered with inData =\n %s",
            pprint.pformat(inData),
        )
        if len(self.listActor) > 0:
            for actor in self.listActor:
                self.logger.debug(
                    "In trigger '%s' -> actorName '%s'",
                    self.errorHandler.name,
                    actor.name,
                )
                actor.trigger(inData)
        if self.inPortTrigger is not None:
            self.logger.debug(
                "In '%s' trigger, trigger = '%s'",
                self.errorHandler.name,
                self.inPortTrigger,
            )
            self.inPortTrigger(inData)


class Submodel(PyPushflowLoggedObject):
    def __init__(
        self,
        parent=None,
        errorHandler=None,
        name=None,
        portNames=["In", "Out"],
        thread_counter=None,
    ):
        super().__init__(log_metadata={"submodel": name}, parent=parent)
        self.parent = parent
        self.name = name
        if errorHandler is None:
            self.errorHandler = parent
        else:
            self.errorHandler = errorHandler
        self.dictPort = {}
        self.listOnErrorActor = []
        for portName in portNames:
            self.dictPort[portName] = Port(
                self, portName, thread_counter=thread_counter
            )

    @property
    def db_client(self):
        return self.parent.db_client

    def setStatus(self, status):
        self.parent.setStatus(status)

    def getActorPath(self):
        return self.parent.getActorPath() + "/" + self.name.replace("%", " ")

    def getPort(self, portName):
        return self.dictPort[portName]

    def connect(self, actor, portName="Out"):
        self.dictPort[portName].connect(actor)

    def connectOnError(self, actor):
        self.logger.debug("connect to error handler '%s'", actor.name)
        self.listOnErrorActor.append(actor)

    def triggerOnError(self, inData):
        self.logger.info(
            "triggered due to error with inData =\n %s", pprint.pformat(inData)
        )
        for onErrorActor in self.listOnErrorActor:
            onErrorActor.trigger(inData)
        if self.errorHandler is not None:
            self.errorHandler.triggerOnError(inData)

    def addActorRef(self, actorRef):
        if self.parent is not None:
            self.parent.addActorRef(actorRef)

    @property
    def pool(self):
        if self.parent is not None:
            return self.parent.pool

    @property
    def stop_exception(self) -> Optional[BaseException]:
        if self.parent is not None:
            return self.parent.stop_exception

    def stop(self, *args, **kw):
        if self.parent is not None:
            return self.parent.stop(*args, **kw)
