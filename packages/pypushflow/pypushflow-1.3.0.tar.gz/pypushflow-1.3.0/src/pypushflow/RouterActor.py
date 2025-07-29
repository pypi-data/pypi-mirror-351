import pprint
from pypushflow.AbstractActor import AbstractActor


class RouterActor(AbstractActor):
    def __init__(
        self,
        parent=None,
        errorHandler=None,
        name="Router",
        itemName=None,
        listPort=None,
        **kw,
    ):
        super().__init__(parent=parent, name=name, **kw)
        self.errorHandler = errorHandler
        self.name = name
        self.itemName = itemName
        if listPort is None:
            self.listPort = []
        else:
            self.listPort = listPort
        self.dictValues = {}

    def connect(self, actor, expectedValue="other"):
        self.logger.debug(
            "connect to actor '%s' (output port %s)", actor.name, expectedValue
        )
        if expectedValue != "other" and expectedValue not in self.listPort:
            raise RuntimeError(
                f"Port {expectedValue} not defined for router actor {self.name}!"
            )
        if expectedValue in self.dictValues:
            self.dictValues[expectedValue].append(actor)
        else:
            self.dictValues[expectedValue] = [actor]

    def trigger(self, inData):
        self.logger.info("triggered with inData =\n %s", pprint.pformat(inData))
        self.setStarted()
        self.setFinished()
        listActor = None
        if self.itemName in inData:
            self.logger.debug("router item = '%s'", self.itemName)
            value = inData[self.itemName]
            self.logger.debug("router item = '%s' value = %s", self.itemName, value)
            if value in [None, "None", "null"]:
                value = "null"
            elif isinstance(value, bool):
                if value:
                    value = "true"
                else:
                    value = "false"
            if not isinstance(value, dict) and value in self.dictValues:
                listActor = self.dictValues[value]
        if listActor is None:
            self.logger.debug("no router destinations for inData")
            if "other" in self.dictValues:
                listActor = self.dictValues["other"]
            else:
                raise RuntimeError(f"No 'other' port for router actor '{self.name}'")
        for actor in listActor:
            actor.trigger(inData)
