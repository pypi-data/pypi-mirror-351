from pypushflow.Workflow import Workflow
from pypushflow.StopActor import StopActor
from pypushflow.StartActor import StartActor
from pypushflow.PythonActor import PythonActor
from pypushflow.RouterActor import RouterActor
from pypushflow.ThreadCounter import ThreadCounter
from pypushflow.tests.workflowTestCase import WorkflowTestCase


class Workflow10(Workflow):
    def __init__(self, name):
        super().__init__(name)
        ctr = ThreadCounter(parent=self)
        self.startActor = StartActor(self, thread_counter=ctr)
        self.pythonActorAddWithoutSleep = PythonActor(
            parent=self,
            script="pypushflow.tests.tasks.pythonActorAddWithoutSleep.py",
            name="Add without sleep",
            thread_counter=ctr,
        )
        self.pythonActorCheck = PythonActor(
            parent=self,
            script="pypushflow.tests.tasks.pythonActorCheck.py",
            name="Check",
            thread_counter=ctr,
        )
        self.check = RouterActor(
            parent=self,
            name="Check",
            itemName="doContinue",
            listPort=["true", "false"],
            thread_counter=ctr,
        )
        self.stopActor = StopActor(self, thread_counter=ctr)
        self.startActor.connect(self.pythonActorAddWithoutSleep)
        self.pythonActorAddWithoutSleep.connect(self.pythonActorCheck)
        self.pythonActorCheck.connect(self.check)
        self.check.connect(self.pythonActorAddWithoutSleep, expectedValue="true")
        self.check.connect(self.stopActor, expectedValue="false")


class TestWorkflow10(WorkflowTestCase):
    def test_workflow10(self):
        limit = 10
        workflow10 = Workflow10(f"Test workflow {limit}")
        inData = {"value": 1, "limit": limit}
        outData = workflow10.run(
            inData, timeout=1200, scaling_workers=False, max_workers=-1
        )
        self.assertEqual(outData["value"], limit)
