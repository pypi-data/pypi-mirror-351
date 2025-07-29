import pprint
from pypushflow.ThreadCountingActor import ThreadCountingActor


class AbstractActor(ThreadCountingActor):
    def __init__(self, parent=None, name=None, **kw):
        super().__init__(name=name, parent=parent, **kw)
        self.listDownStreamActor = []
        self.actorId = None
        self.started = False
        self.finished = False

    def __str__(self) -> str:
        return self.name

    def connect(self, actor):
        self.logger.debug("connect to actor '%s'", actor.name)
        self.listDownStreamActor.append(actor)

    def trigger(self, inData):
        self.logger.info("triggered with inData =\n %s", pprint.pformat(inData))
        self.setStarted()
        self.setFinished()
        for actor in self.listDownStreamActor:
            actor.trigger(inData)

    def uploadInDataToMongo(self, actorData=None, script=None):
        if self.parent is not None:
            name = self.getActorPath() + "/" + self.name
            if actorData:
                info = dict(actorData)
            else:
                info = dict()
            if script:
                info["script"] = script
            self.actorId = self.parent.db_client.startActor(name=name, info=info)

    def uploadOutDataToMongo(self, actorData=None):
        if actorData and self.actorId is not None:
            self.parent.db_client.updateActorInfo(self.actorId, info=actorData)

    def setMongoAttribute(self, attribute, value):
        if self.actorId is not None:
            self.parent.db_client.updateActorInfo(self.actorId, info={attribute: value})

    def getActorPath(self):
        return self.parent.getActorPath()

    def hasStarted(self):
        return self.started

    def setStarted(self):
        self.logger.info("started")
        self.started = True

    def hasFinished(self):
        return self.finished

    def setFinished(self):
        self.logger.info("finished")
        self.finished = True
