from pypushflow.Workflow import Workflow
from pypushflow.Submodel import Submodel
from pypushflow.StopActor import StopActor
from pypushflow.StartActor import StartActor
from pypushflow.PythonActor import PythonActor
from pypushflow.ThreadCounter import ThreadCounter
from pypushflow.tests.workflowTestCase import WorkflowTestCase


class Submodel1(Submodel):
    """
    Submodel containing one python actor.
    """

    def __init__(self, parent, name, thread_counter):
        super().__init__(parent=parent, name=name, thread_counter=thread_counter)
        self.pythonActor = PythonActor(
            parent=self,
            script="pypushflow.tests.tasks.pythonActorTest.py",
            name="Python Actor Test",
            thread_counter=thread_counter,
        )
        self.getPort("In").connect(self.pythonActor)
        self.pythonActor.connect(self.getPort("Out"))


class Workflow3(Workflow):
    """
    Workflow containing one start actor,
    one submodel and one stop actor.
    """

    def __init__(self, name):
        super().__init__(name)
        ctr = ThreadCounter(parent=self)
        self.startActor = StartActor(parent=self, thread_counter=ctr)
        self.submodel1 = Submodel1(parent=self, name="Submodel 1", thread_counter=ctr)
        self.stopActor = StopActor(parent=self, thread_counter=ctr)
        self.startActor.connect(self.submodel1.getPort("In"))
        self.submodel1.getPort("Out").connect(self.stopActor)


class TestWorkflow3(WorkflowTestCase):
    def test_workflow3(self):
        testWorkflow3 = Workflow3("Test workflow 3")
        inData = {"name": "Cat"}
        outData = testWorkflow3.run(
            inData, timeout=15, scaling_workers=False, max_workers=-1
        )
        self.assertIsNotNone(outData)
        self.assertEqual(outData["reply"], "Hello Cat!")
