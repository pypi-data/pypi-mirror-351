import argparse
import asyncio
from pathlib import Path

from .workspace import Workspace

POETRY_BASE_COMMAND = "poetry --ansi"

def main():
    argparser = argparse.ArgumentParser(description='TODO Description')
    argparser.add_argument('operation', choices=[
        'install',
        'sync',
        'test',
        'package',
        'lock',
        'recreate',
        'remove',
        'list',
        'exec',
    ])
    argparser.add_argument('--path')
    argparser.add_argument('passthrough', nargs=argparse.REMAINDER)
    args = argparser.parse_args()

    workspace_root = Path(args.path) if args.path else Path.cwd()
    workspace = Workspace(workspace_root)

    asyncio.run(run_operation(args.operation, args.passthrough, workspace))


async def run_operation(operation: str, passthrough_args: list[str], workspace: Workspace):
    if operation == 'install':
        await run_package_manager_operation(workspace, operation)
    if operation == 'sync':
        await run_package_manager_operation(workspace, operation)
    elif operation == 'test':
        await workspace.run_project_task_parallel("test")
    elif operation == 'package':
        await workspace.run_project_task_parallel("package")
    elif operation == 'lock':
        await run_package_manager_operation(workspace, operation)
    elif operation == 'remove':
        await remove_all_venvs(workspace)
    elif operation == 'recreate':
        await recreate_all_venvs(workspace)
    elif operation == 'list':
        list_all_projects(workspace)
    elif operation == 'exec':
        await workspace.run_project_command_parallel(" ".join(passthrough_args))


async def run_package_manager_operation(workspace: Workspace, operation: str):
    await workspace.run_project_command_parallel(f"{POETRY_BASE_COMMAND} {operation}")


async def recreate_all_venvs(workspace: Workspace):
    await remove_all_venvs(workspace)
    await run_package_manager_operation(workspace, "install")


async def remove_all_venvs(workspace: Workspace):
    await workspace.run_project_command_parallel(f"{POETRY_BASE_COMMAND} env remove --all")


def list_all_projects(workspace: Workspace):
    for project in workspace.poetry_projects:
        print(f"{project.name}: {project.pyproject_path}")