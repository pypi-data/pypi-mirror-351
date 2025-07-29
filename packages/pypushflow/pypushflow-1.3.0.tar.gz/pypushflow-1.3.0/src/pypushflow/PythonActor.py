import os
import pprint
import datetime
import importlib

from .AbstractActor import AbstractActor
from .concurrent import exceptions


class PythonActor(AbstractActor):
    def __init__(
        self, parent=None, name="Python Actor", errorHandler=None, script=None, **kw
    ):
        super().__init__(parent=parent, name=name, **kw)
        self.parentErrorHandler = errorHandler
        self.listErrorHandler = []
        self.script = script
        self.inData = None

    def connectOnError(self, actor):
        self.logger.debug("connect to error handler '%s'", actor.name)
        self.listErrorHandler.append(actor)

    def trigger(self, inData: dict):
        self.logger.info("triggered with inData =\n %s", pprint.pformat(inData))
        self.setStarted()
        self.inData = dict(inData)
        self.uploadInDataToMongo(actorData={"inData": inData}, script=self.script)

        try:
            module = importlib.import_module(os.path.splitext(self.script)[0])
        except Exception as e:
            self.logger.error("Error when trying to import script '%s'", self.script)
            self.errorHandler(e)
            return

        with self._postpone_end_thread(self.resultHandler, self.errorHandler) as (
            resultHandler,
            errorHandler,
        ):
            target = module.run
            self.logger.debug(
                "%s execution of '%s.%s'",
                "synchronous" if self.pool is None else "asynchronous",
                target.__module__,
                target.__name__,
            )

            args = {k: v for k, v in self.inData.items() if not isinstance(k, str)}
            kwargs = {k: v for k, v in self.inData.items() if isinstance(k, str)}
            if args:
                args = tuple(args.get(i) for i in range(max(args) + 1))
            else:
                args = tuple()

            if self.parent is not None:
                stop_exception = self.parent.stop_exception
                if stop_exception:
                    self.logger.error(str(stop_exception))
                    errorHandler(stop_exception)
                    return

            if self.pool is None:
                try:
                    result = target(*args, **kwargs)
                except BaseException as e:
                    errorHandler(e)
                else:
                    resultHandler(result)
            else:
                try:
                    self.pool.apply_async(
                        target,
                        args=args,
                        kwargs=kwargs,
                        callback=resultHandler,
                        error_callback=errorHandler,
                    )
                except RuntimeError:
                    if self.parent is not None:
                        stop_exception = self.parent.stop_exception
                        if stop_exception:
                            self.logger.error(str(stop_exception))
                            errorHandler(stop_exception)
                            return
                    raise

    @property
    def pool(self):
        if self.parent is not None:
            return self.parent.pool

    @property
    def pool_resources(self):
        return 1

    def resultHandler(self, result: dict):
        """Async callback in case of success"""
        try:
            # Handle the result
            self._finishedSuccess(result)

            # Trigger actors
            downstreamData = self.compileDownstreamData(result)
            self._triggerDownStreamActors(downstreamData)
        except Exception as e:
            self.errorHandler(e)

    def compileDownstreamData(self, result: dict) -> dict:
        return {**self.inData, **result}

    def errorHandler(self, exception: Exception):
        """Async callback in case of exception"""
        try:
            # Handle the result
            workflow_exception = exceptions.serialize_exception(exception)
            self._logException(exception)
            self._finishedFailure(workflow_exception)

            # Trigger actors
            result = {
                "WorkflowException": workflow_exception,
                "WorkflowExceptionInstance": exception,
            }
            downstreamData = self.compileDownstreamErrorData(result)
            self._triggerErrorHandlers(downstreamData)
        except Exception:
            self.logger.exception("In errorHandler for '%s'", self.name)

    def compileDownstreamErrorData(self, result: dict) -> dict:
        return {**self.inData, **result}

    def _triggerDownStreamActors(self, downstreamData: dict):
        for downStreamActor in self.listDownStreamActor:
            downStreamActor.trigger(downstreamData)

    def _triggerErrorHandlers(self, downstreamData: dict):
        for errorHandler in self.listErrorHandler:
            errorHandler.trigger(downstreamData)
        if self.parentErrorHandler is not None:
            self.parentErrorHandler.triggerOnError(inData=downstreamData)

    def _finishedSuccess(self, result: dict):
        self.setFinished()
        self.uploadOutDataToMongo(
            actorData={
                "stopTime": datetime.datetime.now(),
                "status": "finished",
                "outData": result,
            }
        )
        if "workflowLogFile" in result:
            self.setMongoAttribute("logFile", result["workflowLogFile"])
        if "workflowDebugLogFile" in result:
            self.setMongoAttribute("debugLogFile", result["workflowDebugLogFile"])

    def _finishedFailure(self, result: dict):
        self.setFinished()
        self.uploadOutDataToMongo(
            actorData={
                "stopTime": datetime.datetime.now(),
                "status": "error",
                "outData": result,
            }
        )

    def _logException(self, exception: Exception) -> None:
        if exception.__traceback__ is None:
            logfunc = self.logger.error
        else:
            logfunc = self.logger.exception
        logfunc(
            "Error in python actor '%s'!\n Not running down stream actors %s\n Exception:%s",
            self.name,
            [actor.name for actor in self.listDownStreamActor],
            exception,
        )
