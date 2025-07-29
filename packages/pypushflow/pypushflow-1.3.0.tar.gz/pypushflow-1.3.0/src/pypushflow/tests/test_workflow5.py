from pypushflow.Workflow import Workflow
from pypushflow.Submodel import Submodel
from pypushflow.StopActor import StopActor
from pypushflow.StartActor import StartActor
from pypushflow.PythonActor import PythonActor
from pypushflow.ThreadCounter import ThreadCounter
from pypushflow.tests.workflowTestCase import WorkflowTestCase


class Submodel5(Submodel):
    """
    Submodel containing one python actor which has a long execution time
    """

    def __init__(self, parent, name, thread_counter):
        super().__init__(parent=parent, name=name, thread_counter=thread_counter)
        self.pythonActor = PythonActor(
            parent=self,
            script="pypushflow.tests.tasks.pythonLongExecutionTest.py",
            name="Python Long Execution Test",
            errorHandler=self,
            thread_counter=thread_counter,
        )
        self.getPort("In").connect(self.pythonActor)
        self.pythonActor.connect(self.getPort("Out"))


class Workflow5(Workflow):
    """
    Workflow containing one start actor,
    one submodel which has a long execution and one stop actor with short timeout.
    """

    def __init__(self, name):
        super().__init__(name)
        ctr = ThreadCounter(parent=self)
        self.startActor = StartActor(self, thread_counter=ctr)
        self.submodel5 = Submodel5(self, name="Submodel 5", thread_counter=ctr)
        self.stopActor = StopActor(self, thread_counter=ctr)
        self.startActor.connect(self.submodel5.getPort("In"))
        self.submodel5.getPort("Out").connect(self.stopActor)


class TestWorkflow5(WorkflowTestCase):
    def test_Workflow5(self):
        testWorkflow5 = Workflow5("Test workflow 5")
        inData = {"name": "Dog", "sleep": 5}
        outData = testWorkflow5.run(
            inData, timeout=1, scaling_workers=False, max_workers=-1
        )
        self.assertIsNone(outData)
        outData = testWorkflow5.run(
            inData, timeout=10, scaling_workers=False, max_workers=-1
        )
        self.assertIsNotNone(outData)
