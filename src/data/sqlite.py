"""SQLite implementation of the repository interfaces.

Each entity is stored as one JSON document next to the few columns used for
lookups. This keeps the schema small and avoids an ORM: the domain models stay
the single definition of the data shape.
"""

from __future__ import annotations

import logging
import sqlite3
import threading
from pathlib import Path
from typing import Callable, Generic, Optional, TypeVar

from pydantic import ValidationError as PydanticValidationError

from src.common.constants import IN_MEMORY_DATABASE
from src.common.exceptions import DataAccessError
from src.data.repositories import (
    ApplicantRepository,
    DocumentRepository,
    LoanApplicationRepository,
)
from src.domain import Applicant, Document, LoanApplication
from src.domain.base import DomainModel

logger = logging.getLogger("loan_processing_ai_poc.data")

M = TypeVar("M", bound=DomainModel)

_SCHEMA = """
CREATE TABLE IF NOT EXISTS applicants (
    applicant_id TEXT PRIMARY KEY,
    data TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS loan_applications (
    application_id TEXT PRIMARY KEY,
    applicant_id TEXT NOT NULL,
    data TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_loan_applications_applicant
    ON loan_applications (applicant_id);
CREATE TABLE IF NOT EXISTS documents (
    document_id TEXT PRIMARY KEY,
    application_id TEXT NOT NULL,
    data TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_documents_application
    ON documents (application_id);
"""


class SqliteDatabase:
    """Owns one SQLite connection and creates the schema.

    One shared connection guarded by a lock is enough for the single-user POC.
    """

    def __init__(self, path: str) -> None:
        self.path = path
        try:
            if path != IN_MEMORY_DATABASE:
                Path(path).parent.mkdir(parents=True, exist_ok=True)
            self._connection = sqlite3.connect(path, check_same_thread=False)
            self._connection.executescript(_SCHEMA)
            self._connection.commit()
        except (sqlite3.Error, OSError) as exc:
            logger.error("Could not open the database: %s", exc.__class__.__name__)
            raise DataAccessError("Could not open the database.") from exc
        self._lock = threading.Lock()

    def execute(self, sql: str, params: tuple = ()) -> list[tuple]:
        with self._lock:
            try:
                rows = self._connection.execute(sql, params).fetchall()
                self._connection.commit()
                return rows
            except sqlite3.Error as exc:
                try:
                    self._connection.rollback()
                except sqlite3.Error:
                    pass  # connection already unusable (for example closed)
                logger.error("Database operation failed: %s", exc.__class__.__name__)
                raise DataAccessError("Database operation failed.") from exc

    def close(self) -> None:
        with self._lock:
            self._connection.close()


class _JsonStore(Generic[M]):
    """Shared save/get/list behaviour for one table."""

    def __init__(
        self,
        database: SqliteDatabase,
        table: str,
        key_column: str,
        model: type[M],
        key_of: Callable[[M], str],
        group_column: Optional[str] = None,
        group_of: Optional[Callable[[M], str]] = None,
    ) -> None:
        self._db = database
        self._table = table
        self._key = key_column
        self._model = model
        self._key_of = key_of
        self._group = group_column
        self._group_of = group_of

    def save(self, entity: M) -> None:
        payload = entity.model_dump_json()
        if self._group and self._group_of:
            sql = (
                f"INSERT OR REPLACE INTO {self._table} ({self._key}, {self._group}, data) "
                "VALUES (?, ?, ?)"
            )
            self._db.execute(sql, (self._key_of(entity), self._group_of(entity), payload))
        else:
            sql = f"INSERT OR REPLACE INTO {self._table} ({self._key}, data) VALUES (?, ?)"
            self._db.execute(sql, (self._key_of(entity), payload))
        logger.debug("Saved %s %s", self._model.__name__, self._key_of(entity))

    def get(self, key: str) -> Optional[M]:
        rows = self._db.execute(f"SELECT data FROM {self._table} WHERE {self._key} = ?", (key,))
        return self._load(rows[0][0]) if rows else None

    def list_by_group(self, group_value: str) -> list[M]:
        if not self._group:
            raise DataAccessError("This store has no grouping column.")
        rows = self._db.execute(
            f"SELECT data FROM {self._table} WHERE {self._group} = ? ORDER BY {self._key}",
            (group_value,),
        )
        return [self._load(row[0]) for row in rows]

    def _load(self, payload: str) -> M:
        try:
            return self._model.model_validate_json(payload)
        except PydanticValidationError as exc:
            logger.error("Stored %s record failed validation.", self._model.__name__)
            raise DataAccessError("Stored data is invalid.") from exc


class SqliteApplicantRepository(ApplicantRepository):
    def __init__(self, database: SqliteDatabase) -> None:
        self._store = _JsonStore(
            database, "applicants", "applicant_id", Applicant, lambda a: a.applicant_id
        )

    def save(self, applicant: Applicant) -> None:
        self._store.save(applicant)

    def get(self, applicant_id: str) -> Optional[Applicant]:
        return self._store.get(applicant_id)


class SqliteLoanApplicationRepository(LoanApplicationRepository):
    def __init__(self, database: SqliteDatabase) -> None:
        self._store = _JsonStore(
            database,
            "loan_applications",
            "application_id",
            LoanApplication,
            lambda a: a.application_id,
            "applicant_id",
            lambda a: a.applicant_id,
        )

    def save(self, application: LoanApplication) -> None:
        self._store.save(application)

    def get(self, application_id: str) -> Optional[LoanApplication]:
        return self._store.get(application_id)

    def list_by_applicant(self, applicant_id: str) -> list[LoanApplication]:
        return self._store.list_by_group(applicant_id)


class SqliteDocumentRepository(DocumentRepository):
    def __init__(self, database: SqliteDatabase) -> None:
        self._store = _JsonStore(
            database,
            "documents",
            "document_id",
            Document,
            lambda d: d.document_id,
            "application_id",
            lambda d: d.application_id,
        )

    def save(self, document: Document) -> None:
        self._store.save(document)

    def get(self, document_id: str) -> Optional[Document]:
        return self._store.get(document_id)

    def list_by_application(self, application_id: str) -> list[Document]:
        return self._store.list_by_group(application_id)
