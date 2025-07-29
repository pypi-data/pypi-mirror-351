from abc import ABC
from .abstract_annotator import AbstractAnnotator
from pprint import pprint
from fhir_cda.utils import ordered_load


class WorkflowAnnotator(AbstractAnnotator, ABC):
    def __init__(self, dataset_path):
        super().__init__(dataset_path, "workflow")
        self.cwl_content = {}
        self._analysis_workflow()

    def _analysis_workflow(self):
        primary_folder = self.root / "primary"

        workflow_paths = list(primary_folder.glob("*.cwl"))
        if not workflow_paths:
            self.descriptions = {}
            raise Exception("No workflow cwl found")

        self.descriptions["workflow"] = {
            "uuid": "",
            "name": self.root.name,
            "title": "",
            "version": "",
            "description": "",
            "purpose": "",
            "usage": "",
            "author": "",
            "goal": [],
            "action": []
        }

        workflow_path = workflow_paths[0]
        with open(workflow_path, 'r') as file:
            self.cwl_content = ordered_load(file)

        self._generate_action(self.cwl_content["steps"])

    def _generate_action(self, steps):
        for idx, step in enumerate(steps.keys()):
            action = {
                "title": step,
                "description": f'step {idx + 1}',
                "related_tool_uuid": "",
                "input": [],
                "output": []
            }
            self.descriptions["workflow"]["action"].append(action)

