import asyncio
import importlib
import json
import os
import subprocess
import sys
from importlib import resources
from importlib.metadata import version as pkg_version
from pathlib import Path

import typer
from rich import print
from rich.prompt import Prompt
from typing_extensions import Annotated

from persona_toolkit.model import AgentContext

app = typer.Typer(help="CLI for managing persona-toolkit projects")


@app.command()
def init(project_name: str):
    """
    Initialize a new persona-toolkit project.
    """
    print(f"🚀 Creating project: [bold cyan]{project_name}[/bold cyan]")
    project_path = Path(project_name)
    project_path.mkdir(exist_ok=True)

    copy_template_files(project_path)

    print("✅ Project initialized.")
    print("➡️ You can now add tools using: [green]persona-toolkit add-tool[/green]")


def copy_template_files(project_path: Path):
    """
    Copy template files from the `template_project` folder to the specified project directory.
    """
    template_project_path = Path(__file__).parent.parent / "template_project"

    if not template_project_path.exists():
        print(f"[red]❌ Template project folder not found: {template_project_path}")
        raise typer.Exit()

    for item in template_project_path.rglob("*"):
        # Skip __pycache__ directories and their contents
        if "__pycache__" in item.parts:
            continue

        relative_path = item.relative_to(template_project_path)
        destination = project_path / relative_path

        if item.is_dir():
            destination.mkdir(parents=True, exist_ok=True)
        elif item.is_file():
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(item.read_bytes())
            print(f"✅ Copied {destination}")


@app.command()
def add_tool(tool_name: str):
    """
    Create a new tool using an interactive wizard.
    """

    if not tool_name:
        print("[red]❌ Tool name is required.")
        raise typer.Exit()

    file_path = Path("tools") / f"{tool_name}.py"

    if file_path.exists():
        print(f"[red]⚠️ Tool '{tool_name}' already exists.")
        raise typer.Exit()

    template = f"""from pydantic import BaseModel, Field
from persona_toolkit.model import AgentContext

NAME = "{tool_name}"

class Input(BaseModel):
    value: str = Field(description="Value to process")

class Output(BaseModel):
    result: str

def run(context: AgentContext, args: Input) -> Output:
    \"\"\"Example tool: {tool_name}\"\"\"
    return Output(result=f"Processed: {{args.value}}")
"""

    file_path.write_text(template)

    print(f"✅ Tool '{tool_name}' created at [green]{file_path}[/green]")


@app.command()
def test_tool(tool_name: str, args: Annotated[str, typer.Argument()] = None):
    """
    Manually test a tool locally by invoking it with input values.
    """

    params = json.loads(args) if args else {}

    print(f"🧪 Testing tool: [cyan]{tool_name}[/cyan]")
    print(f"🔹 Input: {params}")

    try:
        project_root = Path.cwd()
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))

        if not os.path.exists(f"tools/{tool_name}.py"):
            print(f"[red]❌ Tool '{tool_name}' not found.")
            raise typer.Exit()

        module = importlib.import_module(f"tools.{tool_name}")
        _input = module.Input
        _run = module.run

        print(f"🧪 Enter input for tool: [cyan]{tool_name}[/cyan]")
        fields = {}
        for name, field in _input.model_fields.items():
            if name in params:
                fields[name] = params[name]
                continue
            value = Prompt.ask(f"🔹 {name} ({field.annotation.__name__})")
            try:
                fields[name] = json.loads(value)
            except json.JSONDecodeError:
                fields[name] = value

        input_obj = _input(**fields)
        agent_context = AgentContext(session_id="test", project_id="test", user_id="test")

        if asyncio.iscoroutinefunction(_run):
            result = asyncio.run(_run(agent_context, input_obj))
        else:
            result = _run(agent_context, input_obj)

        print(f"✅ Output: [green]{result.model_dump()}[/green]")

    except ModuleNotFoundError:
        print(f"[red]❌ Tool '{tool_name}' not found.")
    except Exception as e:
        print(f"[red]💥 Error: {e}[/red]")


@app.command()
def create_docker_image(image_name: str):
    """
    Create a Docker image for the project.
    """
    print("🔨 Creating Docker image...")
    dockerfile_path = Path("docker/Dockerfile")
    subprocess.run(
        [
            "docker",
            "build",
            "--tag",
            image_name,
            "--file",
            str(dockerfile_path),
            "."
        ],
        check=True
    )
    print("✅ Docker image created successfully.")


@app.command()
def run(port: int = typer.Option(8000, help="Port to run the server on")):
    """
    Start the FastAPI server on the specified port.
    """
    subprocess.run(
        [
            "uvicorn",
            "persona_toolkit.server:app",
            "--host", "0.0.0.0",
            "--port",
            str(port),
        ]
    )


@app.command()
def version():
    """
    Show the version of the persona-toolkit package.
    """
    try:
        print(f"Persona Toolkit Version: {pkg_version('persona-toolkit')}")
    except ImportError:
        print("Persona Toolkit is not installed.")


if __name__ == "__main__":
    app()
