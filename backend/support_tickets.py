
from backend.database import get_db_connection


def create_support_ticket(
    session_id: str,
    issue_summary: str,
) -> int:
    """Create a support ticket for an existing conversation."""

    if not session_id.strip():
        raise ValueError("Session ID is required")

    if not issue_summary.strip():
        raise ValueError("Issue summary is required")

    connection = get_db_connection()

    try:
        with connection:
            conversation = connection.execute(
                """
                SELECT id
                FROM conversations
                WHERE session_id = ?
                """,
                (session_id,),
            ).fetchone()

            if conversation is None:
                raise ValueError("Conversation not found")

            cursor = connection.execute(
                """
                INSERT INTO support_tickets
                    (conversation_id, issue_summary, status)
                VALUES (?, ?, 'open')
                """,
                (
                    conversation["id"],
                    issue_summary.strip(),
                ),
            )

            return cursor.lastrowid

    finally:
        connection.close()


def get_support_ticket(ticket_id: int):
    connection = get_db_connection()

    try:
        row = connection.execute(
            """
            SELECT
                t.id,
                t.issue_summary,
                t.status,
                t.created_at,
                c.session_id
            FROM support_tickets AS t
            JOIN conversations AS c
                ON t.conversation_id = c.id
            WHERE t.id = ?
            """,
            (ticket_id,),
        ).fetchone()

        return dict(row) if row else None
    finally:
        connection.close()