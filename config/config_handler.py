from os import path
from typing import Any, Dict

import yaml


class ParametersHandler:
    def __init__(self) -> None:
        self.handler: dict[Any, Any]
        current_directory: str = path.dirname(path.realpath(__file__))
        file_path: str = path.normpath(
            path.join(current_directory, "parameters.yaml")
        )
        with open(file_path, "r", encoding="utf-8") as f:
            self.handler = yaml.safe_load(f)

        if not self.handler:
            raise ValueError("Parameters file is empty")

    def get_params(self) -> Dict[str, Any]:
        return self.handler if self.handler else {}


class PresetsHandler:
    def __init__(self) -> None:
        self.handler = None
        current_directory = path.dirname(path.realpath(__file__))
        file_path = path.normpath(
            path.join(current_directory, "presets.yaml")
        )
        with open(file_path, "r", encoding="utf-8") as f:
            self.handler = yaml.safe_load(f)

        if not self.handler:
            raise ValueError("Presets file is empty")

    def get_presets(self):
        return self.handler if self.handler else {}
