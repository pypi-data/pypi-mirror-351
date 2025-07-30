import dataclasses
import asyncio
import os

from .project import Project


@dataclasses.dataclass
class ProjectCommand:
    project: Project
    command: str


async def run_project_commands_parallel(project_commands: list[ProjectCommand]):
    tasks = []
    for project_command in project_commands:
        env = os.environ.copy()
        env.pop("VIRTUAL_ENV", None)  # Ensure VIRTUAL_ENV is not set

        process = await asyncio.create_subprocess_shell(
            project_command.command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(project_command.project.root_path),
            env=env
        )
        tasks.append(tail_output_async(process.stdout, project_command.project.name))
        tasks.append(tail_output_async(process.stderr, project_command.project.name))
        tasks.append(process.wait())

    await asyncio.gather(*tasks)


async def tail_output_async(stream, label: str):
    async for line in stream:
        print(f"{label}: {line.decode().strip()}")
