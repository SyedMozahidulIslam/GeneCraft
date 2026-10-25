"""
src/database/db_manager.py
===========================
DBManager — optional SQLite persistence layer for long-term analytics,
species encyclopedia, and evolution history that survives across sessions.
"""
from __future__ import annotations
import logging
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

_SCHEMA_FILE = Path(__file__).parent / "schema.sql"


class DBManager:
    """
    SQLite wrapper for GeneCraft persistent analytics.

    The database is OPTIONAL — the game works fully without it.
    It provides cross-session analytics that JSON saves cannot easily support.

    Tables
    ------
    species_log    — every species ever created (name, genome hash, birth/death tick)
    evolution_log  — timestamped evolution events
    population_log — sampled population snapshots for long-term graphs
    achievement_log— when and how each achievement was earned
    """

    def __init__(self, db_path: str = "saves/genecraft.db") -> None:
        self._path = Path(db_path)
        self._con:  Optional[sqlite3.Connection] = None
        logger.info("DBManager: using %s", self._path)

    # ── Lifecycle ──────────────────────────────────────────────────────────

    def connect(self) -> bool:
        """Open the database and apply schema. Returns True on success."""
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            self._con = sqlite3.connect(str(self._path), check_same_thread=False)
            self._con.row_factory = sqlite3.Row
            self._apply_schema()
            logger.info("DBManager: connected.")
            return True
        except sqlite3.Error as exc:
            logger.error("DBManager: connect failed: %s", exc)
            return False

    def close(self) -> None:
        if self._con:
            self._con.close()
            self._con = None

    def _apply_schema(self) -> None:
        if _SCHEMA_FILE.exists():
            with open(_SCHEMA_FILE, "r") as fh:
                self._con.executescript(fh.read())
        else:
            self._con.executescript(_INLINE_SCHEMA)
        self._con.commit()

    # ── Species Log ────────────────────────────────────────────────────────

    def log_species_created(self, species_id: str, name: str,
                             trophic_level: int, biomes: List[str],
                             created_tick: int) -> None:
        if not self._con:
            return
        try:
            self._con.execute(
                "INSERT OR IGNORE INTO species_log "
                "(species_id, name, trophic_level, biomes, created_tick, status) "
                "VALUES (?,?,?,?,?,'alive')",
                (species_id, name, trophic_level, ",".join(biomes), created_tick),
            )
            self._con.commit()
        except sqlite3.Error as exc:
            logger.error("DBManager.log_species_created: %s", exc)

    def log_species_extinct(self, species_id: str, extinction_tick: int,
                             cause: str, final_generation: int) -> None:
        if not self._con:
            return
        try:
            self._con.execute(
                "UPDATE species_log SET status='extinct', extinction_tick=?, "
                "extinction_cause=?, final_generation=? WHERE species_id=?",
                (extinction_tick, cause, final_generation, species_id),
            )
            self._con.commit()
        except sqlite3.Error as exc:
            logger.error("DBManager.log_species_extinct: %s", exc)

    # ── Evolution Log ──────────────────────────────────────────────────────

    def log_evolution_event(self, event_type: str, species_id: str,
                            description: str, tick: int,
                            gene: Optional[str] = None) -> None:
        if not self._con:
            return
        try:
            self._con.execute(
                "INSERT INTO evolution_log (event_type, species_id, description, tick, gene) "
                "VALUES (?,?,?,?,?)",
                (event_type, species_id, description, tick, gene),
            )
            self._con.commit()
        except sqlite3.Error as exc:
            logger.error("DBManager.log_evolution_event: %s", exc)

    # ── Population Snapshots ───────────────────────────────────────────────

    def log_population_snapshot(self, tick: int,
                                 populations: Dict[str, int]) -> None:
        """Store a population snapshot. Call every N ticks for long-term graphs."""
        if not self._con:
            return
        try:
            rows = [(tick, sid, pop) for sid, pop in populations.items()]
            self._con.executemany(
                "INSERT INTO population_log (tick, species_id, population) VALUES (?,?,?)",
                rows,
            )
            self._con.commit()
        except sqlite3.Error as exc:
            logger.error("DBManager.log_population_snapshot: %s", exc)

    # ── Achievement Log ───────────────────────────────────────────────────

    def log_achievement(self, ach_id: str, name: str, tick: int) -> None:
        if not self._con:
            return
        try:
            self._con.execute(
                "INSERT OR IGNORE INTO achievement_log (ach_id, name, earned_tick) VALUES (?,?,?)",
                (ach_id, name, tick),
            )
            self._con.commit()
        except sqlite3.Error as exc:
            logger.error("DBManager.log_achievement: %s", exc)

    # ── Queries ───────────────────────────────────────────────────────────

    def get_species_history(self) -> List[Dict[str, Any]]:
        if not self._con:
            return []
        try:
            cursor = self._con.execute(
                "SELECT * FROM species_log ORDER BY created_tick ASC")
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error:
            return []

    def get_evolution_events(self, limit: int = 100) -> List[Dict[str, Any]]:
        if not self._con:
            return []
        try:
            cursor = self._con.execute(
                "SELECT * FROM evolution_log ORDER BY tick DESC LIMIT ?", (limit,))
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error:
            return []

    def get_long_term_population(self, species_id: str) -> List[Tuple[int, int]]:
        if not self._con:
            return []
        try:
            cursor = self._con.execute(
                "SELECT tick, population FROM population_log "
                "WHERE species_id=? ORDER BY tick ASC", (species_id,))
            return [(row[0], row[1]) for row in cursor.fetchall()]
        except sqlite3.Error:
            return []


# Inline schema used if schema.sql is missing
_INLINE_SCHEMA = """
CREATE TABLE IF NOT EXISTS species_log (
    species_id       TEXT PRIMARY KEY,
    name             TEXT NOT NULL,
    trophic_level    INTEGER,
    biomes           TEXT,
    created_tick     INTEGER,
    status           TEXT DEFAULT 'alive',
    extinction_tick  INTEGER,
    extinction_cause TEXT,
    final_generation INTEGER
);

CREATE TABLE IF NOT EXISTS evolution_log (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type  TEXT NOT NULL,
    species_id  TEXT,
    description TEXT,
    tick        INTEGER,
    gene        TEXT
);

CREATE TABLE IF NOT EXISTS population_log (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    tick        INTEGER,
    species_id  TEXT,
    population  INTEGER
);

CREATE TABLE IF NOT EXISTS achievement_log (
    ach_id      TEXT PRIMARY KEY,
    name        TEXT,
    earned_tick INTEGER
);

CREATE INDEX IF NOT EXISTS idx_pop_log_tick      ON population_log(tick);
CREATE INDEX IF NOT EXISTS idx_pop_log_species   ON population_log(species_id);
CREATE INDEX IF NOT EXISTS idx_evo_log_tick      ON evolution_log(tick);
"""
