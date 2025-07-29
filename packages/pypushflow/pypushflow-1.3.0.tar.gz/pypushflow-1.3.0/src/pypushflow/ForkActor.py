from pypushflow.AbstractActor import AbstractActor


class ForkActor(AbstractActor):
    def __init__(self, parent=None, name="Fork actor", **kw):
        super().__init__(parent=parent, name=name, **kw)
