# pypushflow

A task scheduler for cyclic and acyclic graphs

## Install

```bash
pip install pypushflow[mx]
```

Use the `mx` option for installation at MX beamlines.

## Run tests

```bash
pip install pypushflow[test]
pytest
```

## Getting started

```python
import logging
from pypushflow.Workflow import Workflow
from pypushflow.StopActor import StopActor
from pypushflow.StartActor import StartActor
from pypushflow.PythonActor import PythonActor
from pypushflow.ThreadCounter import ThreadCounter


class MyWorkflow(Workflow):
    def __init__(self, name):
        super().__init__(name, level=logging.DEBUG)
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


testMyWorkflow = MyWorkflow("Test workflow")
inData = {"name": "World"}
outData = testMyWorkflow.run(inData, timeout=15, pool_type="process")
assert outData["reply"] == "Hello World!"
```

## Documentation

https://pypushflow.readthedocs.io/
