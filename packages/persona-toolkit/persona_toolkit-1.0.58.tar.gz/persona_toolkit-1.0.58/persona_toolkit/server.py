import logging
import os
import sys
from typing import Annotated

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.params import Header
from starlette.middleware.cors import CORSMiddleware

from persona_toolkit.model import InvocationRequest
from persona_toolkit.secret_registry import SECRET
from persona_toolkit.tools_registry import TOOLS

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.DEBUG)

stderr_handler = logging.StreamHandler(sys.stderr)
stderr_handler.setLevel(logging.ERROR)

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(name)s - %(message)s",
    handlers=[stdout_handler, stderr_handler],
)

logging.getLogger("pymongo").setLevel(logging.WARNING)
logging.getLogger("aiortc").setLevel(logging.WARNING)
logging.getLogger("aioice").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("grpc").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

app = FastAPI(title="Persona Toolkit Service")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/tools")
def list_tools():
    return {"tools": list(TOOLS.keys())}


@app.get("/tools/{tool_name}/schema")
def get_tool_schema(tool_name: str):
    tool = TOOLS.get(tool_name)
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    return tool.schema()


@app.post("/invocations")
async def invoke_tool(request: InvocationRequest,
                      secret: Annotated[str | None, Header(alias="x-persona-secret")] = None):
    tool = TOOLS.get(request.tool)
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")

    if SECRET is not None and not await SECRET.validate_secret(secret, request.context, request.input):
        logger.warning(f"Invalid secret provided: {secret}")
        raise HTTPException(status_code=403, detail="Invalid secret")
    elif SECRET is None:
        logger.warning("Secret provider not configured. Skipping secret validation.")

    try:
        return await tool.run(request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


def run(port: int = 8001):
    load_dotenv()

    port = int(os.getenv("SERVER_PORT", port))
    logger.info(f"Persona toolkit service running {port}")
    uvicorn.run(app, port=port, host="0.0.0.0", log_level="warning")


if __name__ == "__main__":
    run()
