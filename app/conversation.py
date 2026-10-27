import sqlite3
from datetime import datetime, timezone

from app.config import DATABASE_PATH, MAX_HISTORY_MESSAGES


def get_connection():
    connection = sqlite3.connect(
        str(DATABASE_PATH),
        timeout=10,
    )
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL,
                role TEXT NOT NULL CHECK (
                    role IN ('user', 'assistant')
                ),
                content TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_messages_conversation
            ON messages(conversation_id, id)
        """)


def get_history(conversation_id: str):
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT role, content
            FROM messages
            WHERE conversation_id = ?
            ORDER BY id ASC
            """,
            (conversation_id,),
        ).fetchall()

    return [
        {"role": row["role"], "content": row["content"]}
        for row in rows
    ]


def get_recent_history(history):
    recent = history[-MAX_HISTORY_MESSAGES:]

    # Avoid starting the context with an assistant response.
    if recent and recent[0]["role"] == "assistant":
        recent = recent[1:]

    return recent


def save_turn(
    conversation_id: str,
    user_message: str,
    assistant_message: str,
):
    timestamp = datetime.now(timezone.utc).isoformat()

    with get_connection() as connection:
        connection.executemany(
            """
            INSERT INTO messages (
                conversation_id, role, content, created_at
            )
            VALUES (?, ?, ?, ?)
            """,
            [
                (
                    conversation_id,
                    "user",
                    user_message,
                    timestamp,
                ),
                (
                    conversation_id,
                    "assistant",
                    assistant_message,
                    timestamp,
                ),
            ],
        )


def clear_conversation(conversation_id: str):
    with get_connection() as connection:
        connection.execute(
            "DELETE FROM messages WHERE conversation_id = ?",
            (conversation_id,),
        )