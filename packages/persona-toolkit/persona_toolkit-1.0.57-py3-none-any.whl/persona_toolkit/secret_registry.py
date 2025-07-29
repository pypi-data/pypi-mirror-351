import asyncio
import importlib
import logging
from typing import Optional

from persona_toolkit.model import SecretProvider

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def discover_secret_provider() -> Optional[SecretProvider]:
    module = importlib.import_module(f"secret")
    if hasattr(module, "validate") and callable(module.validate):
        return SecretProvider(
            handler=module.validate,
            is_async=asyncio.iscoroutinefunction(module.validate),
        )
    else:
        return None


SECRET = discover_secret_provider()
