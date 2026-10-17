
from backend.database import get_db_connection


def save_conversation_message(
    session_id: str,
    role: str,
    message: str,
) -> None:
    if not session_id.strip():
        raise ValueError("Session ID is required")

    if role not in ("customer", "assistant"):
        raise ValueError("Invalid conversation role")

    if not message.strip():
        raise ValueError("Message cannot be empty")

    connection = get_db_connection()

    try:
        with connection:
            connection.execute(
                """
                INSERT OR IGNORE INTO conversations (session_id)
                VALUES (?)
                """,
                (session_id,),
            )

            connection.execute(
                """
                INSERT INTO conversation_messages
                    (conversation_id, role, message)
                SELECT id, ?, ?
                FROM conversations
                WHERE session_id = ?
                """,
                (role, message, session_id),
            )
    finally:
        connection.close()
