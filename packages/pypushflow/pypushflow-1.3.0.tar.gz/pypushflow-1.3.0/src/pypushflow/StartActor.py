from pypushflow.AbstractActor import AbstractActor


class StartActor(AbstractActor):
    def __init__(self, parent=None, name="Start actor", **kw):
        super().__init__(parent=parent, name=name, **kw)
