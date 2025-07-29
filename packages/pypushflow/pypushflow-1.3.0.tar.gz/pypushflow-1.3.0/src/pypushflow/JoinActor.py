import pprint
from pypushflow.AbstractActor import AbstractActor


class JoinActor(AbstractActor):
    def __init__(self, parent=None, name="Join actor", **kw):
        super().__init__(parent=parent, name=name, **kw)
        self.numberOfThreads = 0
        self.listInData = []

    def increaseNumberOfThreads(self):
        self.numberOfThreads += 1

    def trigger(self, inData):
        self.logger.info("triggered with inData =\n %s", pprint.pformat(inData))
        self.setStarted()
        self.setFinished()
        self.listInData.append(inData)
        if len(self.listInData) == self.numberOfThreads:
            newInData = {}
            for data in self.listInData:
                newInData.update(data)
            for actor in self.listDownStreamActor:
                actor.trigger(newInData)
