-- Paula Job Agent – Zielschema (SQLite, WAL)
-- Erklärung der Absicht: docs/02-data-model.md
-- Erste Migration (db/migrations/001_initial.sql) ist eine Kopie dieser Datei.

PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS companies (
  id                INTEGER PRIMARY KEY,
  canonical_name    TEXT NOT NULL,
  normalized_name   TEXT NOT NULL,
  domain            TEXT,                          -- primäre Domain, NULL wenn unbekannt
  country           TEXT,                          -- ISO-2: CH, AT, DE
  region            TEXT,                          -- Kanton / Bundesland
  city              TEXT,
  industry_code     TEXT,                          -- NOGA / ÖNACE / WZ
  industry_label    TEXT,
  size_hint         TEXT CHECK (size_hint IN ('micro','small','medium','large','unknown')) DEFAULT 'unknown',
  website           TEXT,
  careers_url       TEXT,
  application_email TEXT,
  application_url   TEXT,
  research_summary  TEXT,
  research_at       TEXT,
  status            TEXT NOT NULL DEFAULT 'discovered'
                    CHECK (status IN ('discovered','prioritized','researched','no_contact','suggested','applied','blocked')),
  blocked           INTEGER NOT NULL DEFAULT 0,
  blocked_reason    TEXT,
  blocked_at        TEXT,
  reject_count      INTEGER NOT NULL DEFAULT 0,
  priority_score    REAL,                          -- regelbasiert, für sweep-companies
  last_contact_at   TEXT,
  source            TEXT NOT NULL,                 -- zefix, opendata, adzuna, inbox, manual, careerpage, ...
  source_ref        TEXT,
  created_at        TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
  updated_at        TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);
CREATE UNIQUE INDEX IF NOT EXISTS ux_companies_domain ON companies(domain) WHERE domain IS NOT NULL;
CREATE INDEX IF NOT EXISTS ix_companies_normalized ON companies(normalized_name);
CREATE INDEX IF NOT EXISTS ix_companies_status ON companies(status, priority_score);

CREATE TABLE IF NOT EXISTS company_aliases (
  id                INTEGER PRIMARY KEY,
  company_id        INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  alias             TEXT NOT NULL,
  normalized_alias  TEXT NOT NULL,
  source            TEXT,
  UNIQUE (normalized_alias)
);

CREATE TABLE IF NOT EXISTS company_domains (
  company_id        INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  domain            TEXT NOT NULL,
  PRIMARY KEY (domain)
);

CREATE TABLE IF NOT EXISTS jobs (
  id                INTEGER PRIMARY KEY,
  fingerprint       TEXT NOT NULL UNIQUE,
  source            TEXT NOT NULL,
  source_id         TEXT,
  source_url        TEXT,
  company_id        INTEGER REFERENCES companies(id),
  company_name_raw  TEXT,
  title             TEXT NOT NULL,
  location          TEXT,
  workload_min      INTEGER,                       -- Pensum in %
  workload_max      INTEGER,
  employment_type   TEXT,                          -- permanent, temporary, internship, ...
  salary_min        REAL,
  salary_max        REAL,
  salary_currency   TEXT,
  description       TEXT,
  posted_at         TEXT,
  fetched_at        TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
  expires_at        TEXT,
  prefilter_result  TEXT,                          -- 'pass' oder 'fail:<grund>'
  score             INTEGER,                       -- 0..100
  score_reasoning   TEXT,
  score_concerns    TEXT,
  scored_at         TEXT,
  score_model       TEXT,
  status            TEXT NOT NULL DEFAULT 'new'
                    CHECK (status IN ('new','prefiltered_out','scored','below_threshold','proposed','applied','expired','duplicate')),
  UNIQUE (source, source_id)
);
CREATE INDEX IF NOT EXISTS ix_jobs_status_score ON jobs(status, score DESC);
CREATE INDEX IF NOT EXISTS ix_jobs_company ON jobs(company_id);

CREATE TABLE IF NOT EXISTS applications (
  id                INTEGER PRIMARY KEY,
  company_id        INTEGER NOT NULL REFERENCES companies(id),
  job_id            INTEGER REFERENCES jobs(id),
  kind              TEXT NOT NULL CHECK (kind IN ('portal','spontaneous','historical')),
  status            TEXT NOT NULL CHECK (status IN (
                      'discovered','drafting','pending_approval','factcheck_failed','draft_failed',
                      'approved','rejected_by_user','sent','acknowledged','no_reply',
                      'rejected','interview','question','offer','closed')),
  subject           TEXT,
  body_text         TEXT,
  attachments       TEXT,                          -- JSON-Liste
  to_email          TEXT,
  to_name           TEXT,
  gmail_thread_id   TEXT,
  gmail_message_id  TEXT,
  sent_at           TEXT,
  first_reply_at    TEXT,
  closed_at         TEXT,
  outcome           TEXT CHECK (outcome IN ('none','rejected','interview','offer','withdrawn','no_reply')) DEFAULT 'none',
  draft_version     INTEGER NOT NULL DEFAULT 0,
  confidence        REAL,                          -- nur historical
  created_at        TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
  updated_at        TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);
CREATE INDEX IF NOT EXISTS ix_applications_company ON applications(company_id, status);
CREATE INDEX IF NOT EXISTS ix_applications_thread ON applications(gmail_thread_id);
CREATE INDEX IF NOT EXISTS ix_applications_status ON applications(status);

CREATE TABLE IF NOT EXISTS application_drafts (
  id                INTEGER PRIMARY KEY,
  application_id    INTEGER NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
  version           INTEGER NOT NULL,
  subject           TEXT NOT NULL,
  body_text         TEXT NOT NULL,
  generated_by      TEXT NOT NULL,                 -- model id oder 'user'
  feedback_text     TEXT,                          -- Paulas Änderungswunsch, der zu dieser Version führte
  factcheck_result  TEXT,                          -- JSON
  created_at        TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
  UNIQUE (application_id, version)
);

CREATE TABLE IF NOT EXISTS messages (
  id                        INTEGER PRIMARY KEY,
  gmail_message_id          TEXT NOT NULL UNIQUE,
  gmail_thread_id           TEXT,
  direction                 TEXT NOT NULL CHECK (direction IN ('in','out')),
  from_email                TEXT,
  from_name                 TEXT,
  to_email                  TEXT,
  subject                   TEXT,
  date                      TEXT,
  body_text                 TEXT,
  raw_snippet               TEXT,
  application_id            INTEGER REFERENCES applications(id),
  company_id                INTEGER REFERENCES companies(id),
  kind                      TEXT NOT NULL CHECK (kind IN (
                              'application_sent','ack','rejection','interview','question','offer','followup','other','unrelated')),
  classification_confidence REAL,
  classified_by             TEXT,
  classified_at             TEXT,
  needs_human               INTEGER NOT NULL DEFAULT 0,
  created_at                TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);
CREATE INDEX IF NOT EXISTS ix_messages_thread ON messages(gmail_thread_id);
CREATE INDEX IF NOT EXISTS ix_messages_application ON messages(application_id);

CREATE TABLE IF NOT EXISTS messages_seen (
  gmail_message_id  TEXT PRIMARY KEY,
  seen_at           TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
  verdict           TEXT NOT NULL                  -- 'unrelated' | 'stored' | 'error'
);

CREATE TABLE IF NOT EXISTS approvals (
  id                  INTEGER PRIMARY KEY,
  kind                TEXT NOT NULL CHECK (kind IN ('application_draft','reply_draft','block_company_question','info')),
  application_id      INTEGER REFERENCES applications(id),
  message_id          INTEGER REFERENCES messages(id),
  draft_id            INTEGER REFERENCES application_drafts(id),
  status              TEXT NOT NULL DEFAULT 'pending'
                      CHECK (status IN ('pending','approved','revise','rejected','expired','superseded')),
  telegram_chat_id    INTEGER,
  telegram_message_id INTEGER,
  sent_to_user_at     TEXT,
  decided_at          TEXT,
  decision_by         INTEGER,
  feedback_text       TEXT,
  reminder_sent_at    TEXT,
  expires_at          TEXT,
  created_at          TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);
-- Pro Bewerbung höchstens eine offene Freigabe-Anfrage
CREATE UNIQUE INDEX IF NOT EXISTS ux_approvals_pending_app
  ON approvals(application_id) WHERE status = 'pending' AND application_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS ix_approvals_status ON approvals(status, expires_at);

CREATE TABLE IF NOT EXISTS events (
  id            INTEGER PRIMARY KEY,
  ts            TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
  kind          TEXT NOT NULL,                     -- status_change, sent, llm_call, error, user_action, admin_action, ...
  actor         TEXT NOT NULL CHECK (actor IN ('system','user','admin')),
  entity_type   TEXT,
  entity_id     INTEGER,
  payload       TEXT                               -- JSON
);
CREATE INDEX IF NOT EXISTS ix_events_entity ON events(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS ix_events_ts ON events(ts);

CREATE TABLE IF NOT EXISTS llm_calls (
  id                 INTEGER PRIMARY KEY,
  ts                 TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
  task               TEXT NOT NULL,                -- T1..T11
  model              TEXT NOT NULL,
  input_tokens       INTEGER,
  output_tokens      INTEGER,
  cache_read_tokens  INTEGER,
  cache_write_tokens INTEGER,
  cost_usd           REAL,
  duration_ms        INTEGER,
  entity_type        TEXT,
  entity_id          INTEGER,
  ok                 INTEGER NOT NULL DEFAULT 1,
  error              TEXT
);
CREATE INDEX IF NOT EXISTS ix_llm_calls_ts ON llm_calls(ts);

CREATE TABLE IF NOT EXISTS sync_state (
  key         TEXT PRIMARY KEY,
  value       TEXT,
  updated_at  TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);

CREATE TABLE IF NOT EXISTS settings_runtime (
  key         TEXT PRIMARY KEY,
  value       TEXT,
  updated_at  TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);

-- Von Paula per /add eingereichte Links, bevor sie zu jobs werden
CREATE TABLE IF NOT EXISTS manual_submissions (
  id          INTEGER PRIMARY KEY,
  url         TEXT NOT NULL,
  note        TEXT,
  submitted_by INTEGER,
  status      TEXT NOT NULL DEFAULT 'new' CHECK (status IN ('new','processed','failed')),
  job_id      INTEGER REFERENCES jobs(id),
  created_at  TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);
