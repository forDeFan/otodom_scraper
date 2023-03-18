from os import path
from typing import Any, Dict

import yaml


class ParametersHandler:
    """
    Helper function to extract params from yaml and return predefined params.
    """
    def __init__(self) -> None:
        self.handler: Dict[Any, Any]
        current_directory: str = path.dirname(path.realpath(__file__))
        file_path: str = path.normpath(
            path.join(current_directory, "parameters.yaml")
        )
        with open(file_path, "r", encoding="utf-8") as f:
            self.handler = yaml.safe_load(f)

        if not self.handler:
            raise ValueError("Parameters file is empty or not exists.")

    def get_params(self) -> Dict[str, Any]:
        """
        Return all handler params from "parameters.yaml" in a Dict.
        """
        return self.handler if self.handler else {}


class PresetsHandler:
    """
    Helper function to extract params from yaml and return predefined params.
    """
    def __init__(self) -> None:
        self.handler = None
        current_directory: str = path.dirname(path.realpath(__file__))
        file_path: str = path.normpath(
            path.join(current_directory, "presets.yaml")
        )
        with open(file_path, "r", encoding="utf-8") as f:
            self.handler = yaml.safe_load(f)

        if not self.handler:
            raise ValueError("Presets file is empty or not exists.")

    def get_presets(self) -> Dict[str, Any]:
        """
        Return all handler presets from "presets.yaml" in a Dict.
        """
        return self.handler if self.handler else {}
