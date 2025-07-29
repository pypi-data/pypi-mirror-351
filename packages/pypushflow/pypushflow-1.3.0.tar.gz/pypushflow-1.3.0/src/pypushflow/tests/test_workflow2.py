from pypushflow.Workflow import Workflow
from pypushflow.StopActor import StopActor
from pypushflow.StartActor import StartActor
from pypushflow.PythonActor import PythonActor
from pypushflow.ThreadCounter import ThreadCounter
from pypushflow.tests.workflowTestCase import WorkflowTestCase


class Workflow2(Workflow):
    """
    Workflow with error handling, containing one start actor,
    one python actor and one stop actor.

    The python actor throws an exception.
    """

    def __init__(self, name):
        super().__init__(name)
        ctr = ThreadCounter(parent=self)
        self.startActor = StartActor(parent=self, thread_counter=ctr)
        self.pythonActor = PythonActor(
            parent=self,
            script="pypushflow.tests.tasks.pythonErrorHandlerTest.py",
            name="Python Error Handler Test",
            errorHandler=self,
            thread_counter=ctr,
        )
        self.stopActor = StopActor(parent=self, thread_counter=ctr)
        self.startActor.connect(self.pythonActor)
        self.pythonActor.connect(self.stopActor)
        self.connectOnError(self.stopActor)


class TestWorkflow2(WorkflowTestCase):
    def test_Workflow2(self):
        testWorkflow2 = Workflow2("Test workflow 2")
        inData = {"name": "Tom"}
        outData = testWorkflow2.run(inData, timeout=5, scaling_workers=False)
        self.assertIsNotNone(outData)
        self.assertTrue("WorkflowException" in outData)
