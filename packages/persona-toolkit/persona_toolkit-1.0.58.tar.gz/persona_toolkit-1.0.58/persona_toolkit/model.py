import asyncio
import base64
import logging
from typing import Type, Callable, Optional, List, Any

from pydantic import BaseModel
from pydantic.alias_generators import to_camel

from persona_toolkit.schema_utils import flatten_schema

logger = logging.getLogger(__name__)


class ExternalToolException(Exception):
    """
    This exception is raised when a tool execution must be managed externally.
    """

    pass


def map_model_props(schema: dict):
    """Define a standard format for model properties to be used in API documentation."""
    properties = schema.get("properties", {})
    required = schema.get("required", [])
    title = schema.get("title", "")
    _type = schema.get("type", "object")
    fields = {}
    for field_name, field_info in properties.items():
        param = {
            "type": field_info.get("type", "string"),
            "description": field_info.get("description", ""),
        }
        if "items" in field_info:
            param["items"] = field_info["items"]
        fields[field_name] = param

    return {
        "title": title,
        "type": _type,
        "properties": fields,
        "required": required,
    }


class Tool:
    def __init__(
            self,
            name: str,
            input_model: Type[BaseModel],
            output_model: Type[BaseModel],
            handler: Callable[..., BaseModel],
            is_async: bool = False,
    ):
        self.name = name
        self.input_model = input_model
        self.output_model = output_model
        self.handler = handler
        self.is_async = is_async

    def schema(self):
        return {
            "name": self.name,
            "description": self.handler.__doc__ or f"Function for {self.name}",
            "parameters": map_model_props(flatten_schema(self.input_model)),
            "output": map_model_props(flatten_schema(self.output_model)),
        }

    async def run(self, request: "InvocationRequest") -> "InvocationResponse":
        parsed = self.input_model.model_validate(request.input)
        context = request.context
        try:
            if self.is_async:
                result = await self.handler(context, parsed)
            else:
                def call_handler(ctx: AgentContext, args: BaseModel):
                    return self.handler(ctx, args)

                result = await asyncio.get_event_loop().run_in_executor(None, call_handler, context, parsed)

            output = result.model_dump()
            logger.info(f"Tool {self.name} invoked. Input: {parsed}, Output {output}")
            return InvocationResponse(success=True, output=output, context=context.get_data())
        except ExternalToolException:
            return InvocationResponse(success=True, needs_external_management=True, context=context.get_data(),
                                      output={})
        except Exception as e:
            logger.info(f"Tool {self.name}, input {parsed}, failed with error: {e}")
            return InvocationResponse(success=False, error_message=str(e), output={}, context=context.get_data())


class File(BaseModel):
    name: str
    content_base64: str
    content_type: str

    def get_content(self) -> bytes:
        """
        Get the content of the file as bytes.
        """
        return base64.b64decode(self.content_base64)

    class Config:
        populate_by_name = True
        alias_generator = to_camel


class AgentContext(BaseModel):
    """
    Context for the agent, containing information about the current session and is passed to the tools.
    """
    data: dict[str, Any] = {}
    events: dict[str, Any] = {}
    session_id: str
    project_id: str
    user_id: Optional[str | None] = None
    files: Optional[List[File]] = None

    def dispatch_event(self, event_name: str, event_data: dict) -> None:
        """
        Dispatch an event to the context.
        """
        if event_name not in self.events:
            self.events[event_name] = []
        self.events[event_name].append(event_data)

    def get_data(self):
        """
        Get the context data.
        """
        return {"data": self.data, "files": self.files}

    def merge_data(self, data: dict[str, Any]) -> None:
        """
        Merge new data into the context.
        """
        self.data.update(data)

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a value from the context.
        """
        return self.data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """
        Set a value in the context.
        """
        self.data[key] = value

    def __getitem__(self, key: str) -> Any:
        """
        Get a value from the context using the [] operator.
        """
        return self.get(key)

    def __setitem__(self, key: str, value: Any) -> None:
        """
        Set a value in the context using the [] operator.
        """
        self.set(key, value)

    def __contains__(self, key: str) -> bool:
        """
        Check if a key exists in the context.
        """
        return key in self.data

    def __iter__(self):
        """
        Iterate over the keys in the context.
        """
        return iter(self.data)

    def clear(self) -> None:
        """
        Clear all values from the context.
        """
        self.data.clear()

    def all_keys(self) -> List[str]:
        """
        Get all keys from the context.
        """
        return list(self.data.keys())

    def add_file(self, name: str, content_type: str, content: bytes):
        """
        Add a file to the context.
        """
        if self.files is None:
            self.files = []
        content_base64 = base64.b64encode(content).decode("utf-8")
        file = File(name=name, content_base64=content_base64, content_type=content_type)
        self.files.append(file)

    class Config:
        populate_by_name = True
        alias_generator = to_camel


class InvocationRequest(BaseModel):
    tool: str
    input: dict
    context: AgentContext

    class Config:
        populate_by_name = True
        alias_generator = to_camel


class InvocationResponse(BaseModel):
    success: bool
    error_message: Optional[str] = None
    output: dict
    context: dict
    needs_external_management: bool = False

    class Config:
        populate_by_name = True
        alias_generator = to_camel


class SecretProvider(BaseModel):
    handler: Callable
    is_async: bool

    async def validate_secret(self, secret: str, context: AgentContext, args: dict) -> bool:
        if self.is_async:
            return await self.handler(secret, context, args)
        else:
            return self.handler(secret, context, args)
