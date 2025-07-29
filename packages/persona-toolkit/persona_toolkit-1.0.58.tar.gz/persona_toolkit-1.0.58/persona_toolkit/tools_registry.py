# tools_management.py
import asyncio
import importlib
import logging
import pkgutil
from typing import Dict, List

from persona_toolkit.model import Tool

logger = logging.getLogger(__name__)


def discover_tools(path: List[str]) -> Dict[str, Tool]:
    tool_map = {}

    for finder, name, ispkg in pkgutil.iter_modules(path):
        module = importlib.import_module(f"tools.{name}")
        if (
                hasattr(module, "NAME")
                and hasattr(module, "Input")
                and hasattr(module, "Output")
                and hasattr(module, "run")
        ):
            tool_map[module.NAME] = Tool(
                name=module.NAME,
                input_model=module.Input,
                output_model=module.Output,
                handler=module.run,
                is_async=asyncio.iscoroutinefunction(module.run),
            )

            logger.info(f"Discovered tool {module.NAME}.")
        else:
            logger.info(f"Skipping {name}: missing Input, Output or run or NAME")

    return tool_map


TOOLS = discover_tools(["tools"])
