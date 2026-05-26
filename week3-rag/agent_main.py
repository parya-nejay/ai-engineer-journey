"""Day 20 — Stateful agent exposed as a FastAPI endpoint.
Wraps run_agent() from agent_demo.py with HTTP, using session_id
to thread multi-turn conversations across stateless requests.
"""
from fastapi import FastAPI #From the library named fastapi, give me the tool FastAPI
from pydantic import BaseModel, Field  #the parent class that turns a normal Python class into a validated data shape, Field helps you to describe each field
from agent_demo import run_agent, TOOLS, TOOL_FUNCTIONS
import logging

from fastapi import FastAPI, HTTPException
from anthropic import (
    AuthenticationError,
    RateLimitError,
    APIConnectionError,
    BadRequestError,
)

logger = logging.getLogger(__name__)
app = FastAPI(title="Agent Chat API", version="0.1.0") # creat an actual web app and store it in a variable called app(I choose this name app)
#These two classes define the shape of data going in and out of your endpoint. 

class AgentRequest(BaseModel):
    message: str = Field(..., description="The user's message for this turn")
    session_id: str = Field(..., description="Identifier for the multi-turn conversation")


class AgentResponse(BaseModel):
    answer: str
    session_id: str

@app.post("/agent-chat", response_model=AgentResponse)
def agent_chat(request: AgentRequest) -> AgentResponse:
    try:
        answer = run_agent(
            user_message=request.message,
            session_id=request.session_id,
            tools=TOOLS,
            tool_functions=TOOL_FUNCTIONS,
        )
        return AgentResponse(answer=answer, session_id=request.session_id)
    except RateLimitError:
        logger.exception("Anthropic rate limit for session %s", request.session_id)
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Please try again shortly.")
    except APIConnectionError:
        logger.exception("Anthropic unreachable for session %s", request.session_id)
        raise HTTPException(status_code=503, detail="Upstream LLM provider unreachable.")
    except AuthenticationError:
        logger.exception("Anthropic auth error — check API key")
        raise HTTPException(status_code=500, detail="Server configuration error.")
    except BadRequestError:
        logger.exception("Anthropic rejected the request for session %s", request.session_id)
        raise HTTPException(status_code=500, detail="Internal request error.")
    except Exception:
        logger.exception("Unexpected error for session %s", request.session_id)
        raise HTTPException(status_code=500, detail="Internal server error.")