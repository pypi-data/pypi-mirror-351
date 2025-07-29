# Persona CLI

**Persona CLI** is a command-line tool for creating and managing projects that use the `persona-toolkit` — a modular
function-calling framework designed for agent-based systems.

This CLI helps you scaffold projects, generate tools, test them locally, and run the FastAPI server that exposes your
tools via REST API.

---

## 🚀 Installation

To use the CLI, first install the `persona-toolkit` library (assuming it's published or available locally):

```bash
pip install persona-toolkit
```

> Or if you're developing locally:

```bash
cd persona-toolkit/
poetry install
```

The CLI is exposed as:

```bash
persona-toolkit
```

---

## 📆 Features

### `init`

Create a new project scaffold with Poetry and the required structure:

```bash
persona-toolkit init my-project
```

This will:

- Initialize a Poetry project
- Install `persona-toolkit` as a dependency
- Create a `tools/` folder where your tools will live

---

### `add-tool`

Add a new tool interactively:

```bash
persona-toolkit add-tool
```

You'll be prompted for a tool name. A new Python file will be created in the `tools/` directory with a ready-to-edit
template including:

- `Input` and `Output` models (using Pydantic)
- A `run()` function

---

### `test-tool`

Test a tool locally by manually entering its input values:

```bash
persona-toolkit test-tool echo
```

This will:

- Import the specified tool from the `tools/` directory
- Prompt for input fields
- Run the `run()` function and show the output

You can use the cli to pass input values:

```bash
persona-toolkit test-tool echo --input '{"message": "Hello, World!"}'
```

---

### `run`

Start the FastAPI server and expose your tools via HTTP:

```bash
persona-toolkit run --port 8000
```

You can now access:

- `GET /tools` — list available tools
- `GET /tools/{tool}/schema` — get tool schema
- `POST /invocations` — run a tool

---

## 🗂 Project Structure

```bash
my-project/
├── pyproject.toml        # Poetry project config
├── tools/                # Directory for your tools
│   └── echo_test.py      # Example tool
|── secret.py             # Example secret validation
```

Each tool must define:

- `NAME` (a str with tool name)
- `Input` (a Pydantic model)
- `Output` (a Pydantic model)
- `run(context: AgentContext, input: Input) -> Output`

---

## 💡 Example Tool

```python
from pydantic import BaseModel, Field
from persona_toolkit.model import AgentContext

NAME = "echo"


class Input(BaseModel):
    message: str = Field(description="Message to echo")


class Output(BaseModel):
    message: str


def run(context: AgentContext, args: Input) -> Output:
    """
    Echo the message back.

    The `context` can be used to store and retrieve state across invocations.
    For example, if a previous message exists in the context, it will be appended to the current message.
    """
    previous_message = context.get("message")
    if previous_message:
        input.message = f"{previous_message} {input.message}"

    context.set("message", args.message)

    return Output(message=f"Echo: {args.message}")
```

### Understanding kwargs and context

The `context` parameter is an instance of `AgentContext`, which is a dictionary-like object that provides access to the
current execution context of the tool, it includes the following keys:

- `project_id`: The ID of the project where the tool is being executed.
- `session_id`: The ID of the current session, which can be used to track the state of the conversation or interaction.
- `user_id`: The ID of the user invoking the tool, which can be useful for personalizing responses or tracking
  user-specific data.

And expose a set of methods to manage the context:

- `get(key: str, default: Any = None)`: Retrieve a value from the context by key. If the key does not exist, return the
  default value.
- `set(key: str, value: Any)`: Set a value in the context by key.
- `delete(key: str)`: Delete a value from the context by key.

For example, if a tool needs to keep track of the last message sent by the user, it can store that message in the
`context` and retrieve it in subsequent invocations, it can be used to:

- Store intermediate results.
- Append or modify input values based on previous invocations.
- Share data across different tools in the same session.

### Example of using kwargs

```python
# tools/echo_test.py

from pydantic import BaseModel, Field
from persona_toolkit.model import AgentContext

NAME = "echo"


class Input(BaseModel):
    message: str = Field(description="Message to echo")


class Output(BaseModel):
    message: str


def run(context: AgentContext, args: Input) -> Output:
    """
    Echo the message back.
    """
    # Access primary infos from kwargs
    project_id = context.project_id
    session_id = context.session_id
    user_id = context.user_id

    # TODO: Do something with project_id, session_id, user_id

    return Output(message=f"Echo: {args.message}")
```

---

### ExternalToolException

The `ExternalToolException` is a special exception provided by the `persona-toolkit` to signal that a tool does not perform any internal operations but instead delegates its behavior to an external system. When this exception is raised, it generates a transaction inside the `persona-core` framework, which can then be handled by any external service or component responsible for managing the tool's behavior. This mechanism is particularly useful for tools that act as placeholders or triggers for external workflows, ensuring seamless integration between the `persona-toolkit` and external systems.

---

## 🔒 Secrets and Authentication

The `persona-toolkit` provides a mechanism to validate secrets using the `SecretProvider`. This can be used to add a basic authentication layer to your tools.

### How to Configure Secrets

1. **Define a Secret Validation Function**

   Create a function to validate the secret. It **must be named** `secret.py` and placed in the root of your project.

   ```python
   from persona_toolkit.model import AgentContext

   def validate(secret: str, context: AgentContext, args: dict) -> bool:
       """Validate static secrets."""
       return secret == "your-secret-key"
   ```

### How Secrets Are Used

Once configured, the secret is checked by reading the `x-persona-secret` header from each tool request. The validation process works as follows:

1. If the `x-persona-secret` header is present in the request, its value is validated using the `validate` function.
2. If the secret is valid, the request proceeds as expected.
3. If the secret is invalid, the request is rejected with an appropriate error.

This mechanism ensures that tools can optionally enforce authentication while allowing unauthenticated access if no secret is provided.

---

## 💻 Local Development

To run the CLI locally, you can use the following command:

```bash
python persona_toolkit/cli.py --port 8001
```

You can use local `tools` folder to test your tools. Just make sure to set the `PYTHONPATH` to the root of the project:

## ✅ Requirements

- Python 3.10+
- Poetry
- Uvicorn (installed automatically)

---

## 📃 License

MIT License

---

Built for the [Persona Agent System](https://github.com/your-org/persona) 🤖
