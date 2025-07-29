import pprint
from typing import Optional, Sequence
from contextlib import contextmanager
from .persistence import init_db_client
from .logutils import PyPushflowLoggedObject
from .concurrent import get_pool
from . import stop_workflows


class Workflow(PyPushflowLoggedObject):
    def __init__(
        self,
        name,
        stop_on_signals: bool = False,
        forced_interruption: bool = False,
        stop_signals: Optional[Sequence] = None,
        db_options: Optional[dict] = None,
    ):
        """
        :param name:
        :param level:
        :param stop_on_signals:
        :param forced_interruption:
        :param stop_signals:
        """
        super().__init__(log_metadata={"workflow": name})
        self.logger.info("\n\nInstantiate new workflow '%s'\n", name)
        self.name = name
        self.listOnErrorActor = []
        if db_options is None:
            db_options = dict()
        self.db_client = init_db_client(**db_options)
        self.listActorRef = []
        self._execution_pool = None
        self._stop_exception = None
        self._stop_on_signals = stop_on_signals
        self._forced_interruption = forced_interruption
        self._stop_signals = stop_signals

    def connectOnError(self, actor):
        self.logger.debug("connect to error handler '%s'", actor.name)
        self.listOnErrorActor.append(actor)

    def triggerOnError(self, inData):
        self.logger.info(
            "triggered due to error with inData =\n %s", pprint.pformat(inData)
        )
        for onErrorActor in self.listOnErrorActor:
            onErrorActor.trigger(inData)

    def getActorPath(self):
        return "/" + self.name

    def addActorRef(self, actorRef):
        self.logger.debug("add reference to actor '%s'", actorRef.name)
        self.listActorRef.append(actorRef)

    def getListActorRef(self):
        return self.listActorRef

    def setStatus(self, status):
        self.db_client.setWorkflowStatus(status)

    def endWorkflow(self, status):
        self.db_client.endWorkflow(status)

    @contextmanager
    def _run_context(
        self,
        max_workers: Optional[int] = None,
        scaling_workers: bool = True,
        pool_type: Optional[str] = None,
        **pool_options,
    ):
        with self._pool_context(
            max_workers=max_workers,
            scaling_workers=scaling_workers,
            pool_type=pool_type,
            **pool_options,
        ):
            with self._db_client_context():
                yield

    @contextmanager
    def _pool_context(
        self,
        max_workers: Optional[int] = None,
        scaling_workers: bool = True,
        pool_type: Optional[str] = None,
        **pool_options,
    ):
        if self._execution_pool is not None:
            # A pool already exists
            yield
            return
        if max_workers is not None and max_workers <= 0:
            max_workers = sum(actor.pool_resources for actor in self.listActorRef)
        pool_options["max_workers"] = max_workers
        pool_options["pool_type"] = pool_type
        if scaling_workers:
            pool_type = "scaling"
        try:
            with self._stop_on_signals_context():
                with get_pool(pool_type)(**pool_options) as pool:
                    self.logger.info(
                        "Execution pool %s (%s)", type(pool).__name__, pool_options
                    )
                    self._execution_pool = pool
                    yield
        except BaseException as e:
            # Make sure PythonActor callbacks do not trigger other tasks
            self.logger.warning("Interrupt workflow execution: %s", str(e))
            self._stop_exception = e
            raise
        finally:
            if self._execution_pool is not None:
                self._execution_pool.join()
                self._execution_pool = None
            self._stop_exception = None

    @contextmanager
    def _db_client_context(self):
        self.db_client.connect()
        try:
            self.db_client.startWorkflow(self.name)
            try:
                yield
            finally:
                self.db_client.ensureEndWorkflow()
        finally:
            self.db_client.disconnect()

    @contextmanager
    def _stop_on_signals_context(self):
        if self._stop_on_signals:
            with stop_workflows.stop_on_signals_context(
                self, stop_signals=self._stop_signals
            ):
                yield
        else:
            yield

    def run(
        self,
        inData,
        timeout: Optional[float] = None,
        max_workers: Optional[int] = None,
        scaling_workers: bool = True,
        pool_type: Optional[str] = None,
        **pool_options,
    ) -> dict:
        self.logger.info("\n\nRun workflow '%s'\n", self.name)
        self.stopActor.reset()
        with self._run_context(
            max_workers=max_workers,
            scaling_workers=scaling_workers,
            pool_type=pool_type,
            **pool_options,
        ):
            self.startActor.trigger(inData)
            self.stopActor.join(timeout=timeout)
            return self.stopActor.outData

    @property
    def pool(self):
        return self._execution_pool

    @property
    def stop_exception(self) -> Optional[BaseException]:
        if self._stop_exception:
            return self._stop_exception

    def stop(
        self,
        reason: str = "interrupt workflow",
        forced_interruption: Optional[bool] = None,
    ):
        self.logger.debug("stop workflow: %s", reason)
        if forced_interruption is None:
            forced_interruption = self._forced_interruption
        self._stop_exception = stop_workflows.StopPypushflowWorkflow(reason)
        if forced_interruption and self.pool is not None:
            self.pool.close()
            self.pool.interrupt()
