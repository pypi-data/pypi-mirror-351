from pypushflow.AbstractActor import AbstractActor


class RequestStatus(AbstractActor):
    def __init__(self, parent=None, name="Request status", status=None, **kw):
        super().__init__(parent=parent, name=name, **kw)
        self.status = status

    def trigger(self, inData):
        if self.status is not None and self.parent is not None:
            self.parent.setStatus(self.status)
        super().trigger(inData=inData)
