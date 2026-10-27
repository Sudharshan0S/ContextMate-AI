import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from google.genai import errors as genai_errors

from app.config import MAX_MESSAGE_LENGTH
from app.models import (
    ChatRequest,
    ChatResponse,
    HistoryResponse,
)
from app.conversation import (
    clear_conversation,
    get_history,
    get_recent_history,
    init_db,
    save_turn,
)
from app.llm import generate_reply

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    logger.info("ContextMate database initialized.")
    yield


app = FastAPI(
    title="ContextMate AI",
    description=(
        "A conversational AI assistant with persistent memory "
        "and context-window management."
    ),
    version="2.0.0",
    lifespan=lifespan,
)

app.mount(
    "/static",
    StaticFiles(directory=str(STATIC_DIR)),
    name="static",
)


@app.get("/")
def home():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
def health():
    return {
        "status": "ok",
        "application": "ContextMate AI",
        "version": "2.0.0",
    }


@app.get(
    "/conversations/{conversation_id}",
    response_model=HistoryResponse,
)
def conversation_history(conversation_id: str):
    if not conversation_id.strip() or len(conversation_id) > 100:
        raise HTTPException(
            status_code=400,
            detail="Invalid conversation ID.",
        )

    return HistoryResponse(
        conversation_id=conversation_id,
        messages=get_history(conversation_id),
    )


@app.delete("/conversations/{conversation_id}")
def delete_conversation(conversation_id: str):
    if not conversation_id.strip() or len(conversation_id) > 100:
        raise HTTPException(
            status_code=400,
            detail="Invalid conversation ID.",
        )

    clear_conversation(conversation_id)

    return {
        "status": "deleted",
        "conversation_id": conversation_id,
    }


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    message = request.message

    if not message:
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty.",
        )

    if len(message) > MAX_MESSAGE_LENGTH:
        raise HTTPException(
            status_code=413,
            detail="Message exceeds the maximum allowed length.",
        )

    history = get_recent_history(
        get_history(request.conversation_id)
    )

    try:
        reply = generate_reply(history, message)

    except genai_errors.APIError as error:
        logger.warning(
            "Gemini API request failed: %s",
            type(error).__name__,
        )
        raise HTTPException(
            status_code=502,
            detail=(
                "The AI service is temporarily unavailable. "
                "Please try again shortly."
            ),
        ) from error

    except RuntimeError as error:
        logger.error("Chat configuration or generation error: %s", error)
        raise HTTPException(
            status_code=503,
            detail=(
                "The AI service is not configured correctly "
                "or could not complete the request."
            ),
        ) from error

    except Exception as error:
        logger.exception("Unexpected chatbot error.")
        raise HTTPException(
            status_code=500,
            detail="Something went wrong. Please try again.",
        ) from error

    # Save the turn only after Gemini successfully responds.
    save_turn(request.conversation_id, message, reply)

    return ChatResponse(
        conversation_id=request.conversation_id,
        response=reply,
    )