import logging

from pydantic import BaseModel, Field

from persona_toolkit.model import AgentContext

NAME = "echo"

logger = logging.getLogger(NAME)


class Input(BaseModel):
    message: str = Field(description="The message to echo")


class Output(BaseModel):
    message: str


def run(context: AgentContext, args: Input) -> Output:
    """
    Echo the message back
    """
    logger.debug(f"echo message: {context.message}")
    
    return Output(message=f"Echo: {args.message}")
