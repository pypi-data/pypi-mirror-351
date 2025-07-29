from pypushflow.Workflow import Workflow
from pypushflow.StopActor import StopActor
from pypushflow.StartActor import StartActor
from pypushflow.PythonActor import PythonActor
from pypushflow.ThreadCounter import ThreadCounter
from pypushflow.tests.workflowTestCase import WorkflowTestCase


class Workflow1(Workflow):
    """
    Workflow containing one start actor,
    one python actor and one stop actor.
    """

    def __init__(self, name):
        super().__init__(name)
        ctr = ThreadCounter(parent=self)
        self.startActor = StartActor(parent=self, thread_counter=ctr)
        self.pythonActor = PythonActor(
            parent=self,
            script="pypushflow.tests.tasks.pythonActorTest.py",
            name="Python Actor Test",
            thread_counter=ctr,
        )
        self.stopActor = StopActor(parent=self, thread_counter=ctr)
        self.startActor.connect(self.pythonActor)
        self.pythonActor.connect(self.stopActor)


class TestWorkflow1(WorkflowTestCase):
    def test_Workflow1(self):
        testWorkflow1 = Workflow1("Test workflow 1")
        inData = {"name": "Jerry"}
        outData = testWorkflow1.run(
            inData, timeout=15, scaling_workers=False, max_workers=-1
        )
        self.assertIsNotNone(outData)
        self.assertEqual(outData["reply"], "Hello Jerry!")
