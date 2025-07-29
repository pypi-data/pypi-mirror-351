import logging

from persona_toolkit.model import AgentContext

logger = logging.getLogger(__name__)


def validate(secret: str, context: AgentContext, args: dict) -> bool:
    """Validate static secrets."""
    logger.debug(f"Agent context: {context}")
    logger.debug(f"Arguments: {args}")
    logger.debug(f"Validating secret {secret}")

    return secret == "persona"
