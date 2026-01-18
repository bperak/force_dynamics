import sqlite3
from pathlib import Path


def connect(db_path: str) -> sqlite3.Connection:
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            provider TEXT NOT NULL,
            model TEXT NOT NULL,
            seed INTEGER NOT NULL,
            config_hash TEXT NOT NULL
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS sentences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            language TEXT NOT NULL,
            original_text TEXT NOT NULL,
            translation_human TEXT NOT NULL,
            translation_google TEXT NOT NULL,
            UNIQUE(language, original_text)
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS translations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id INTEGER NOT NULL,
            sentence_id INTEGER NOT NULL,
            translation_gpt TEXT NOT NULL,
            FOREIGN KEY(run_id) REFERENCES runs(id),
            FOREIGN KEY(sentence_id) REFERENCES sentences(id)
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS evaluations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id INTEGER NOT NULL,
            sentence_id INTEGER NOT NULL,
            evaluation_json TEXT NOT NULL,
            mapping_json TEXT NOT NULL,
            FOREIGN KEY(run_id) REFERENCES runs(id),
            FOREIGN KEY(sentence_id) REFERENCES sentences(id)
        )
        """
    )

    conn.commit()


def insert_sentence(conn: sqlite3.Connection, language: str, original: str, human: str, google: str) -> int:
    cur = conn.cursor()
    cur.execute(
        """
        INSERT OR IGNORE INTO sentences (language, original_text, translation_human, translation_google)
        VALUES (?, ?, ?, ?)
        """,
        (language, original, human, google),
    )
    conn.commit()

    cur.execute(
        """
        SELECT id FROM sentences WHERE language = ? AND original_text = ?
        """,
        (language, original),
    )
    row = cur.fetchone()
    return int(row["id"])


def insert_run(conn: sqlite3.Connection, provider: str, model: str, seed: int, config_hash: str, created_at: str) -> int:
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO runs (created_at, provider, model, seed, config_hash)
        VALUES (?, ?, ?, ?, ?)
        """,
        (created_at, provider, model, seed, config_hash),
    )
    conn.commit()
    return int(cur.lastrowid)


def insert_translation(conn: sqlite3.Connection, run_id: int, sentence_id: int, translation_gpt: str) -> None:
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO translations (run_id, sentence_id, translation_gpt)
        VALUES (?, ?, ?)
        """,
        (run_id, sentence_id, translation_gpt),
    )
    conn.commit()


def insert_evaluation(conn: sqlite3.Connection, run_id: int, sentence_id: int, evaluation_json: str, mapping_json: str) -> None:
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO evaluations (run_id, sentence_id, evaluation_json, mapping_json)
        VALUES (?, ?, ?, ?)
        """,
        (run_id, sentence_id, evaluation_json, mapping_json),
    )
    conn.commit()
