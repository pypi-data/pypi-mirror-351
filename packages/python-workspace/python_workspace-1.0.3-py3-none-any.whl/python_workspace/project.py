from pathlib import Path
from dataclasses import dataclass
from functools import cached_property
from typing import Any
import tomllib

from .project_command_sources import KNOWN_COMMAND_SOURCES


@dataclass
class Project:
    pyproject_path: Path

    @cached_property
    def toml(self) -> dict:
        return tomllib.loads(self.pyproject_path.read_text())

    @property
    def root_path(self) -> Path:
        return self.pyproject_path.parent

    @property
    def name(self) -> str:
        return self.poetry_config.get('name', 'NoName')

    @property
    def poetry_config(self) -> dict:
        return self.toml.get('tool', {}).get('poetry', {})

    @property
    def is_poetry_project(self) -> bool:
        return bool(self.poetry_config)

    def get_toml_value_from_dot_path(self, dot_path: str) -> None | Any:
        """
        Get a nested value from the toml dictionary using a dot path.
        """
        parts = dot_path.split('.')
        current = self.toml
        for part in parts:
            current = current.get(part)
            if current is None:
                return None

        return current

    def build_command_from_task_name(self, task_name: str) -> str | None:
        """
        Build a command string from a task name based on known command sources.
        """
        for source in KNOWN_COMMAND_SOURCES:
            command_dot_path = f"{source.toml_path}.{task_name}"
            command_value = self.get_toml_value_from_dot_path(command_dot_path)

            if command_value is None:
                continue

            return f"{source.runner_command} {command_value}" if source.runner_command else command_value

        return None