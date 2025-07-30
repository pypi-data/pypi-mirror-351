import dataclasses


@dataclasses.dataclass
class ProjectCommandSource:
    toml_path: str
    runner_command: str


KNOWN_COMMAND_SOURCES = [
    ProjectCommandSource(toml_path="tool.tasks", runner_command=""),
    ProjectCommandSource(toml_path="tool.pdm.scripts", runner_command="pdm run"),
    ProjectCommandSource(toml_path="tool.poe.tasks", runner_command="poe"),
]

