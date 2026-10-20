"""SQLite store replaced with PostgreSQL for persistent hosting.

Every note has an owner. In v1/v2 the owner is always "local".
In v3 (after auth is added) the owner will be the user id from the token.
"""

import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()


def _conn() -> psycopg2.extensions.connection:
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    conn.autocommit = False
    # Create table if it doesn't exist yet
    with conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS notes (
                id SERIAL PRIMARY KEY,
                owner TEXT NOT NULL,
                text TEXT,
                created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
    conn.commit()
    return conn


def list_notes(owner: str) -> list[dict]:
    conn = _conn()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                "SELECT id, text, created_at FROM notes WHERE owner = %s ORDER BY id",
                (owner,)
            )
            rows = cur.fetchall()
            # cast created_at to string so it's JSON-serialisable
            return [{"id": r["id"], "text": r["text"], "created_at": str(r["created_at"])} for r in rows]
    finally:
        conn.close()


def add_note(owner: str, text: str) -> dict:
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO notes (owner, text) VALUES (%s, %s) RETURNING id",
                (owner, text)
            )
            note_id = cur.fetchone()[0]
        conn.commit()
        return {"id": note_id, "text": text}
    finally:
        conn.close()


def delete_note(owner: str, note_id: int) -> bool:
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM notes WHERE owner = %s AND id = %s",
                (owner, note_id)
            )
            deleted = cur.rowcount > 0
        conn.commit()
        return deleted
    finally:
        conn.close()
