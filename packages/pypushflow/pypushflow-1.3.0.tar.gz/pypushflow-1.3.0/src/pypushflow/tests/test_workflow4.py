from pypushflow.Workflow import Workflow
from pypushflow.Submodel import Submodel
from pypushflow.StopActor import StopActor
from pypushflow.StartActor import StartActor
from pypushflow.PythonActor import PythonActor
from pypushflow.ThreadCounter import ThreadCounter
from pypushflow.tests.workflowTestCase import WorkflowTestCase


class Submodel4(Submodel):
    """
    Submodel containing one python actor which throws an exception.
    """

    def __init__(self, parent, name, thread_counter):
        super().__init__(parent=parent, name=name, thread_counter=thread_counter)
        self.pythonActor = PythonActor(
            parent=self,
            script="pypushflow.tests.tasks.pythonErrorHandlerTest.py",
            name="Python Error Handler Test",
            errorHandler=self,
            thread_counter=thread_counter,
        )
        self.getPort("In").connect(self.pythonActor)
        self.pythonActor.connect(self.getPort("Out"))


class Workflow4(Workflow):
    """
    Workflow containing one start actor,
    one submodel which throws an exception and one stop actor.
    """

    def __init__(self, name):
        super().__init__(name)
        ctr = ThreadCounter(parent=self)
        self.startActor = StartActor(thread_counter=ctr)
        self.submodel4 = Submodel4(parent=self, name="Submodel 4", thread_counter=ctr)
        self.stopActor = StopActor(thread_counter=ctr)
        self.startActor.connect(self.submodel4.getPort("In"))
        self.submodel4.getPort("Out").connect(self.stopActor)
        self.connectOnError(self.stopActor)


class TestWorkflow4(WorkflowTestCase):
    def test_workflow4(self):
        workflow4 = Workflow4("Test workflow 4")
        inData = {"name": "Dog"}
        outData = workflow4.run(
            inData, timeout=5, scaling_workers=False, max_workers=-1
        )
        self.assertIsNotNone(outData)
        self.assertTrue("WorkflowException" in outData)
