import subprocess
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path

from .project import Project
from .parallel_exec import run_project_commands_parallel, ProjectCommand

@dataclass
class Workspace:
    root_path: Path

    @cached_property
    def projects(self) -> list[Project]:
        ls_files_result = subprocess.run(
            f"git ls-files {self.root_path}",
            shell=True,
            capture_output=True,
            text=True,
            cwd=str(self.root_path)
        )
        all_files = ls_files_result.stdout.split('\n')
        all_file_paths = (self.root_path / file for file in all_files)

        return [
            Project(path.resolve()) for path in all_file_paths if path.name == 'pyproject.toml'
        ]

    @cached_property
    def poetry_projects(self) -> list[Project]:
        return [
            project for project in self.projects if project.is_poetry_project
        ]

    async def run_project_command_parallel(self, command: str):
        await run_project_commands_parallel(
            [ProjectCommand(project=project, command=command) for project in self.poetry_projects]
        )

    async def run_project_task_parallel(self, task_name: str):
        project_commands: list[ProjectCommand] = []

        for project in self.poetry_projects:
            command = project.build_command_from_task_name(task_name)
            if command is None:
                print(f"Task '{task_name}' not found in project '{project.name}'. Skipping.")
            else:
                project_commands.append(ProjectCommand(project=project, command=command))

        if not project_commands:
            print(f"No projects have commands defined for task '{task_name}'.")
            return

        await run_project_commands_parallel(project_commands)
