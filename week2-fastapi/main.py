import logging
import anthropic
import json
import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from anthropic import Anthropic
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
# === Logging configuration ===
logging.basicConfig(  # sets up Python's logging system
    level=logging.INFO,  # show INFO, WARNING, ERROR messages
    format="%(asctime)s [%(levelname)s] %(name)s:%(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    force=True,
)
logger = logging.getLogger(__name__)


load_dotenv()  # Load API key from .env file
# Initialize the Anthropic client (auto-reads ANTHROPIC_API_KEY)
anthropic_client = Anthropic()

app = FastAPI()
DB_FILE = "employees.json"
# === Pydantic model ===


class Employee(BaseModel):
    id: int
    name: str
    salary: int


class ChatRequest(BaseModel):
    message: str
# === Load/save helpers ===


def load_db():
    if not os.path.exists(DB_FILE):
        return {
            1: {"id": 1, "name": "Alice", "salary": 50000},
            2: {"id": 2, "name": "Bob", "salary": 60000},
            3: {"id": 3, "name": "Charlie", "salary": 70000},
        }
    try:
        with open(DB_FILE, "r") as f:
            data = json.load(f)
            return {int(k): v for k, v in data.items()}
    except (json.JSONDecodeError, FileNotFoundError):
        return {}


def save_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=2)


# === Initialize on startup ===
employees_db = load_db()
# === Endpoints ===


@app.get("/")
def read_root():
    return {"message": "Hello, World!"}


@app.get("/employees")
def get_employees():
    return list(employees_db.values())


@app.get("/employees/{employee_id}")
def get_employee(employee_id: int):
    if employee_id not in employees_db:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employees_db[employee_id]


@app.post("/employees")
def create_employee(employee: Employee):
    if employee.id in employees_db:
        raise HTTPException(
            status_code=400, detail="Employee with this ID already exists")
    employees_db[employee.id] = employee.model_dump()
    save_db(employees_db)
    return employees_db[employee.id]


@app.put("/employees/{employee_id}")
def update_employee(employee_id: int, employee: Employee):
    if employee_id not in employees_db:
        raise HTTPException(status_code=404, detail="Employee not found")
    employees_db[employee_id] = employee.model_dump()
    save_db(employees_db)
    return employees_db[employee_id]


@app.delete("/employees/{employee_id}")
def delete_employee(employee_id: int):
    if employee_id not in employees_db:
        raise HTTPException(status_code=404, detail="Employee not found")
    deleted = employees_db.pop(employee_id)
    save_db(employees_db)
    return {"deleted": deleted}
# === Helper: Claude API call with retry ===


@retry(
    stop=stop_after_attempt(3),  # max 3 tries total
    # wait 2s, 4s, 8s (capped at 10s)
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((
        anthropic.RateLimitError,
        anthropic.APIConnectionError,
        anthropic.APITimeoutError,
        anthropic.InternalServerError,
    )),
    reraise=True,
)
def call_claude(message: str):
    """Call Claude with automatic retry on transient errors."""
    return anthropic_client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        system="You are a helpful AI assistant for a Python developer learning AI engineering. Keep responses concise and practical.",
        messages=[
            {"role": "user", "content": message}
        ]
    )

# Add the AI endpoint


@app.post("/chat")
def chat_with_claude(request: ChatRequest):
    """Send a message to Claude and get a response."""
    logger.info(f"/chat received message ({len(request.message)} chars)")
    try:
       # response = anthropic_client.messages.create(

        #     model="claude-haiku-4-5-20251001",
        #     max_tokens=1024,
        #     system="You are a helpful AI assistant for a Python developer learning AI engineering. Keep responses concise and practical.",
        #     messages=[
        #         {"role": "user", "content": request.message}
        #     ]
        # )
        response = call_claude(request.message)   # ← uses retry helper now
        logger.info(f"/chat succeeded — input_tokens={response.usage.input_tokens}, output_tokens={response.usage.output_tokens}")   # ← NEW
        return {
            "user_message": request.message,
            "claude_response": response.content[0].text,
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens
        }

    except anthropic.AuthenticationError:
        # Bad API key — permanent error, retrying won't help
        raise HTTPException(
            status_code=500,
            detail="Server configuration error: invalid API key"
        )

    except anthropic.BadRequestError as e:
        # Malformed request — your fault, not Claude's
        raise HTTPException(
            status_code=400,
            detail=f"Invalid request: {str(e)}"
        )

    except anthropic.RateLimitError:
        # Hit Anthropic's rate limit — retry will help (we add it in Part 3)
        raise HTTPException(
            status_code=429,
            detail="Service is busy. Please try again in a moment."
        )

    except anthropic.APIConnectionError:
        # Network problem reaching Anthropic
        raise HTTPException(
            status_code=503,
            detail="Could not reach AI service. Please try again."
        )

    except anthropic.APIStatusError as e:
        # Catch-all for other API errors (5xx server errors, etc.)
        raise HTTPException(
            status_code=502,
            detail=f"AI service error: {e.message}"
        )

    except Exception as e:
        # Catch-all for unexpected errors — log it, give generic message to user
        logger.exception("Unexpected error in /chat")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred. Please try again."
        )


@app.post("/chat-stream")
def chat_stream(request: ChatRequest):
    """Send a message to Claude and stream the response back."""

    def generate():
        with anthropic_client.messages.stream(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            system="You are a helpful AI assistant for a Python developer learning AI engineering. Keep responses concise and practical.",
            messages=[
                {"role": "user", "content": request.message}
            ]
        )as stream:
            for text in stream.text_stream:
                yield text
    return StreamingResponse(generate(), media_type="text/plain")


# In-memory conversation storage
# Dict mapping session_id → list of messages
conversations: dict[str, list[dict]] = {}


class ConversationRequest(BaseModel):
    session_id: str
    message: str


@app.post("/conversation")
def conversation(request: ConversationRequest):
    """Multi-turn conversation with Claude that remembers history."""

    # Get or create the conversation history for this session
    if request.session_id not in conversations:
        conversations[request.session_id] = []

    history = conversations[request.session_id]

    # Add the new user message
    history.append({"role": "user", "content": request.message})

    # Call Claude with the FULL history
    response = anthropic_client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        system="You are a helpful AI assistant. Remember the conversation context.",
        messages=history
    )

    # Extract Claude's response
    assistant_message = response.content[0].text

    # Add Claude's response to the history
    history.append({"role": "assistant", "content": assistant_message})

    return {
        "session_id": request.session_id,
        "response": assistant_message,
        "message_count": len(history),
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens
    }


@app.get("/conversation/{session_id}")
def get_conversation_history(session_id: str):
    """Retrieve the full message history for a session."""
    if session_id not in conversations:
        raise HTTPException(status_code=404, detail="Session not found")
    return {
        "session_id": session_id,
        "messages": conversations[session_id],
        "message_count": len(conversations[session_id])
    }


@app.delete("/conversation/{session_id}")
def delete_conversation(session_id: str):
    """Clear a conversation's history."""
    if session_id in conversations:
        del conversations[session_id]
    return {"deleted": session_id}
