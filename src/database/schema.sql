-- GeneCraft SQLite Schema v1.0.0
-- Optional persistent analytics database

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
CREATE INDEX IF NOT EXISTS idx_evo_log_species   ON evolution_log(species_id);
