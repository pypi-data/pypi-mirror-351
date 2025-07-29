from pypushflow.AbstractActor import AbstractActor


class ErrorHandler(AbstractActor):
    def __init__(self, parent=None, name="Error handler", **kw):
        super().__init__(parent=parent, name=name, **kw)

    def trigger(self, inData):
        if self.parent is not None:
            self.parent.setStatus("error")
        super().trigger(inData=inData)
