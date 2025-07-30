from typing import Optional, Literal

ResourceType = ["Observation", "ImagingStudy"]


class WorkflowGoal:

    def __init__(self, description):
        self.description = description if isinstance(description, str) else str(description)

    def get(self):
        goal = {
            "description": self.description
        }
        return {k: v for k, v in goal.items() if v not in ("", None)}


class WorkflowActionInput:

    def __init__(self, resource_type: Literal["Observation", "ImagingStudy", "none"]):
        self.resource_type = resource_type if resource_type in ResourceType else "none"

    def get(self):
        action_input = {
            "resource_type": self.resource_type
        }
        return {k: v for k, v in action_input.items() if v not in ("", None)}


class WorkflowActionOutput:
    def __init__(self, resource_type: Literal["Observation", "ImagingStudy", "none"], code, system, display):
        self.resource_type = resource_type if resource_type in ResourceType else "none"
        self.code = code
        self.system = system
        self.display = display

    def get(self):
        action_input = {
            "resource_type": self.resource_type,
        }
        if self.resource_type == "Observation":
            action_input["code"] = self.code
            action_input["system"] = self.system
            action_input["display"] = self.display
        return {k: v for k, v in action_input.items() if v not in ("", None)}
