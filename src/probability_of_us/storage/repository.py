"""Small transactional SQLite repository for saved scenarios and preferences."""

from __future__ import annotations

import json
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def default_database_path() -> Path:
    import os
    base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    directory = base / "ProbabilityOfUs"
    directory.mkdir(parents=True, exist_ok=True)
    return directory / "probability_of_us.sqlite3"


class ScenarioRepository:
    SCHEMA_VERSION = 1

    def __init__(self, database: str | Path):
        self.path = Path(database)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path, timeout=10)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys=ON")
        return connection

    @contextmanager
    def _connection(self):
        connection = self._connect()
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    def _initialize(self) -> None:
        with self._connection() as connection:
            version = connection.execute("PRAGMA user_version").fetchone()[0]
            if version not in (0, self.SCHEMA_VERSION):
                raise RuntimeError(f"Unsupported local database schema version {version}.")
            connection.execute("""
                CREATE TABLE IF NOT EXISTS scenarios (
                    scenario_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL CHECK(length(name) BETWEEN 1 AND 120),
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    input_json TEXT NOT NULL CHECK(length(input_json) <= 200000),
                    result_json TEXT NOT NULL CHECK(length(result_json) <= 500000),
                    tags_json TEXT NOT NULL DEFAULT '[]'
                )
            """)
            connection.execute("""
                CREATE TABLE IF NOT EXISTS preferences (
                    key TEXT PRIMARY KEY,
                    value_json TEXT NOT NULL CHECK(length(value_json) <= 20000)
                )
            """)
            connection.execute("PRAGMA user_version=1")

    def save_scenario(self, name: str, inputs: dict[str, Any], result: dict[str, Any], tags: list[str] | None = None, scenario_id: str | None = None) -> str:
        safe_name = name.strip()
        if not 1 <= len(safe_name) <= 120:
            raise ValueError("Scenario name must contain 1 to 120 characters.")
        input_json, result_json = json.dumps(inputs, ensure_ascii=False, allow_nan=False), json.dumps(result, ensure_ascii=False, allow_nan=False)
        tags_json = json.dumps([str(tag)[:40] for tag in (tags or [])[:30]], ensure_ascii=False)
        now = datetime.now(timezone.utc).isoformat()
        identifier = scenario_id or str(uuid.uuid4())
        with self._connection() as connection:
            existing = connection.execute("SELECT created_at FROM scenarios WHERE scenario_id=?", (identifier,)).fetchone()
            created = existing["created_at"] if existing else now
            connection.execute("""
                INSERT INTO scenarios(scenario_id,name,created_at,updated_at,input_json,result_json,tags_json)
                VALUES(?,?,?,?,?,?,?)
                ON CONFLICT(scenario_id) DO UPDATE SET name=excluded.name, updated_at=excluded.updated_at,
                    input_json=excluded.input_json, result_json=excluded.result_json, tags_json=excluded.tags_json
            """, (identifier, safe_name, created, now, input_json, result_json, tags_json))
        return identifier

    def list_scenarios(self) -> list[dict[str, Any]]:
        with self._connection() as connection:
            rows = connection.execute("SELECT scenario_id,name,created_at,updated_at,input_json,result_json,tags_json FROM scenarios ORDER BY updated_at DESC").fetchall()
        return [{"scenario_id": row["scenario_id"], "name": row["name"], "created_at": row["created_at"],
                 "updated_at": row["updated_at"], "inputs": json.loads(row["input_json"]),
                 "result": json.loads(row["result_json"]), "tags": json.loads(row["tags_json"])} for row in rows]

    def delete_scenario(self, scenario_id: str) -> bool:
        with self._connection() as connection:
            cursor = connection.execute("DELETE FROM scenarios WHERE scenario_id=?", (scenario_id,))
            return cursor.rowcount == 1

    def set_preference(self, key: str, value: Any) -> None:
        if len(key) > 80:
            raise ValueError("Preference key is too long.")
        data = json.dumps(value, ensure_ascii=False, allow_nan=False)
        with self._connection() as connection:
            connection.execute("INSERT INTO preferences(key,value_json) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value_json=excluded.value_json", (key, data))

    def get_preference(self, key: str, default: Any = None) -> Any:
        with self._connection() as connection:
            row = connection.execute("SELECT value_json FROM preferences WHERE key=?", (key,)).fetchone()
        return json.loads(row[0]) if row else default

    def integrity_check(self) -> str:
        with self._connection() as connection:
            return str(connection.execute("PRAGMA integrity_check").fetchone()[0])

