import pprint
from pypushflow import Submodel
from pypushflow.ThreadCountingActor import ThreadCountingActor


class StopActor(ThreadCountingActor):
    def __init__(self, parent=None, errorHandler=None, name="Stop actor", **kw):
        super().__init__(name=name, parent=parent, **kw)
        self.errorHandler = errorHandler
        self._outData = None

    def trigger(self, inData):
        self.logger.info("triggered with inData =\n %s", pprint.pformat(inData))
        if self.parent is not None and not isinstance(self.parent, Submodel.Submodel):
            # Parent is a Workflow
            self.outData = inData
        elif self.errorHandler is not None:
            self.errorHandler.errorHandler.stopActor.trigger(inData)
        else:
            self.outData = inData

    def reset(self):
        self._outData = None

    @property
    def outData(self):
        return self._outData

    @outData.setter
    def outData(self, data):
        if data is None:
            self._outData = None
            return
        if self._outData is None:
            self._outData = data
            return
        inerror = data.get("WorkflowException")
        outerror = self._outData.get("WorkflowException")
        if inerror and outerror:
            pass  # keep the first error
        elif inerror:
            pass  # keep the non-error result
        elif outerror:
            # keep the non-error result
            self._outData = data
        else:
            # keep the last result
            self._outData = data

    def join(self, timeout=7200):
        if self.parent is not None:
            self.logger.debug("wait for scheduler threads to be finished")
        success = self._wait_threads_finished(timeout=timeout)
        if self.parent is not None:
            self.logger.debug("scheduler threads are finished")
        self._finalizeInMongo(success)
        return success

    def _finalizeInMongo(self, success):
        if self.parent is None:
            return
        if success:
            self.logger.debug("finished")
            self.parent.endWorkflow("finished")
        else:
            self.logger.error("timeout detected")
            self.parent.endWorkflow("timeout")
