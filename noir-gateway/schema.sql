-- NOIR AGENT v6 — D1 Database Schema
-- Jalankan: wrangler d1 execute noir-db --file=schema.sql

-- Tabel: Antrian Perintah
CREATE TABLE IF NOT EXISTS commands (
    id          TEXT PRIMARY KEY,
    action      TEXT NOT NULL,
    description TEXT DEFAULT 'Manual',
    status      TEXT DEFAULT 'pending',  -- pending | sent | done | failed
    result      TEXT,
    created_at  TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at  TEXT
);

-- Tabel: Registrasi Agen
CREATE TABLE IF NOT EXISTS agents (
    device_id       TEXT PRIMARY KEY,
    name            TEXT,
    last_seen       TEXT DEFAULT CURRENT_TIMESTAMP,
    last_screenshot TEXT
);

-- Tabel: Memori Agen (Key-Value)
CREATE TABLE IF NOT EXISTS memory (
    key         TEXT PRIMARY KEY,
    value       TEXT,
    updated_at  TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Index untuk performa query
CREATE INDEX IF NOT EXISTS idx_commands_status ON commands(status, created_at);
