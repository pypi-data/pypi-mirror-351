import os
import sys
import time
import signal
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import ProcessPoolExecutor

import pytest
from pypushflow.Workflow import Workflow
from pypushflow.StopActor import StopActor
from pypushflow.StartActor import StartActor
from pypushflow.PythonActor import PythonActor
from pypushflow.ThreadCounter import ThreadCounter
from pypushflow.ErrorHandler import ErrorHandler
from pypushflow.stop_workflows import DEFAULT_STOP_SIGNALS


@pytest.mark.parametrize("forced_interruption", [True, False])
def test_stop_workflow(forced_interruption, workflow_cleanup):
    if os.name == "nt" and forced_interruption:
        pytest.skip("not supported on windows")
    testWorkflow1 = WorkflowSleep("Test workflow Sleep")

    def run_normal(executor):
        # Workflow with 3 nodes that sleep 0 seconds each.
        inData = {"sleep_time": 0, "counter": 0}
        future = executor.submit(
            testWorkflow1.run,
            inData,
            timeout=15,
            scaling_workers=False,
            max_workers=-1,
        )
        result = future.result()
        assert "WorkflowException" not in result
        assert result["counter"] == 3

    def run_stopped(executor):
        # Workflow with 3 nodes that sleep 2 seconds each.
        inData = {"sleep_time": 2, "counter": 0}
        future = executor.submit(
            testWorkflow1.run,
            inData,
            timeout=15,
            scaling_workers=False,
            max_workers=-1,
        )

        # Stop half-way the execution of the second node.
        time.sleep(3)
        print("STOP ...")
        testWorkflow1.stop(
            reason="workflow stopped by user", forced_interruption=forced_interruption
        )

        result = future.result()
        assert result["counter"] < 3
        assert "WorkflowException" in result

    with ThreadPoolExecutor(max_workers=1) as executor:
        run_normal(executor)
        run_stopped(executor)
        run_stopped(executor)
        run_normal(executor)


@pytest.mark.parametrize("forced_interruption", [True, False])
def test_stop_signal_workflow(forced_interruption, skip_when_gevent, skip_on_windows):
    def run_normal(executor):
        # Workflow with 3 nodes that sleep 0 seconds each.
        inData = {"sleep_time": 0, "counter": 0}
        future = executor.submit(
            _run_workflow,
            inData,
            timeout=15,
            scaling_workers=False,
            max_workers=-1,
            forced_interruption=forced_interruption,
        )
        result = future.result()
        assert "WorkflowException" not in result
        assert result["counter"] == 3

    def run_stopped(executor, started_event):
        # Workflow with 3 nodes that sleep 2 seconds each.
        inData = {"sleep_time": 2, "counter": 0}
        started_event.clear()
        future = executor.submit(
            _run_workflow,
            inData,
            timeout=15,
            scaling_workers=False,
            max_workers=-1,
            started_event=started_event,
            forced_interruption=forced_interruption,
        )

        # Stop signal half-way the execution of the second node.
        assert started_event.wait(timeout=10)
        time.sleep(3)
        for pid in list(executor._processes):
            # TODO: doesn't work on windows (it kills the subprocess)
            print(f"KILL pid={pid} ...")
            os.kill(pid, DEFAULT_STOP_SIGNALS[0])

        result = future.result()
        assert result["counter"] < 3
        assert "WorkflowException" in result

    with mp.Manager() as manager:
        started_event = manager.Event()

        if sys.version_info < (3, 7):
            pool = ProcessPoolExecutor(max_workers=1)
            pool.submit(_process_initializer).result()
        else:
            pool = ProcessPoolExecutor(max_workers=1, initializer=_process_initializer)

        with pool as executor:
            print("\n--run_normal--")
            run_normal(executor)
            print("\n--run_stopped--")
            run_stopped(executor, started_event)
            print("\n--run_stopped--")
            run_stopped(executor, started_event)
            print("\n--run_normal--")
            run_normal(executor)


def _process_initializer():
    try:
        signal.signal(DEFAULT_STOP_SIGNALS[0], signal.SIG_IGN)
    except (OSError, AttributeError, ValueError, RuntimeError):
        pass


def _run_workflow(
    *args,
    started_event=None,
    forced_interruption: bool = False,
    **kwargs,
):
    print(f"START WORKFLOW pid={os.getpid()}")
    testWorkflow1 = WorkflowSleep(
        "Test workflow Sleep",
        stop_on_signals=True,
        forced_interruption=forced_interruption,
    )
    if started_event is not None:
        started_event.set()
    return testWorkflow1.run(*args, **kwargs)


class WorkflowSleep(Workflow):
    def __init__(self, name, **kw):
        super().__init__(name, **kw)
        ctr = ThreadCounter(parent=self)
        self.startActor = StartActor(parent=self, thread_counter=ctr)
        self.errorActor = ErrorHandler(parent=self, thread_counter=ctr)
        self.pythonActor1 = PythonActor(
            parent=self,
            script="pypushflow.tests.tasks.pythonActorInterrupt.py",
            name="Python Actor Sleep",
            thread_counter=ctr,
        )
        self.pythonActor2 = PythonActor(
            parent=self,
            script="pypushflow.tests.tasks.pythonActorInterrupt.py",
            name="Python Actor Sleep",
            thread_counter=ctr,
        )
        self.pythonActor3 = PythonActor(
            parent=self,
            script="pypushflow.tests.tasks.pythonActorInterrupt.py",
            name="Python Actor Sleep",
            thread_counter=ctr,
        )
        self.stopActor = StopActor(parent=self, thread_counter=ctr)
        self.startActor.connect(self.pythonActor1)
        self.pythonActor1.connect(self.pythonActor2)
        self.pythonActor2.connect(self.pythonActor3)
        self.pythonActor3.connect(self.stopActor)
        self.errorActor.connect(self.stopActor)
        self.pythonActor1.connectOnError(self.errorActor)
        self.pythonActor2.connectOnError(self.errorActor)
        self.pythonActor3.connectOnError(self.errorActor)
