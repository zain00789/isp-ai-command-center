import sqlite3
from pathlib import Path

DATABASE_PATH = Path(__file__).resolve().parent.parent / "isp_ai.db"


def get_db_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection

def initialize_database():
    connection = get_db_connection()

    try:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id TEXT NOT NULL UNIQUE,
                isp_provider TEXT NOT NULL,
                registered_phone TEXT NOT NULL,
                plan TEXT NOT NULL,
                connection_status TEXT NOT NULL,
                package_expiry TEXT NOT NULL
            )
        """)

        connection.commit()
    finally:
        connection.close()


def seed_test_customers():
    customers = [
        ("FAL001", "Falcon", "03000000001", "Fiber 20 Mbps", "online", "2026-12-31"),
        ("JAZ001", "Jazz", "03000000002", "Fiber 30 Mbps", "online", "2026-12-31"),
        ("CON001", "CONNECT", "03000000003", "Fiber 50 Mbps", "offline", "2026-12-31"),
    ]

    connection = get_db_connection()

    try:
        connection.executemany(
            """
            INSERT OR IGNORE INTO customers
            (customer_id, isp_provider, registered_phone,
             plan, connection_status, package_expiry)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            customers,
        )
        connection.commit()
    finally:
        connection.close()

def initialize_support_tables():
    connection = get_db_connection()

    try:
        connection.executescript("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL UNIQUE,
                customer_id TEXT,
                started_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS conversation_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('customer', 'assistant')),
                message TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id)
                    REFERENCES conversations(id)
            );

            CREATE TABLE IF NOT EXISTS support_tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER NOT NULL,
                issue_summary TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'open',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id)
                    REFERENCES conversations(id)
            );
        """)

        connection.commit()
    finally:
        connection.close()