# 02 – Datenmodell

Die Datenbank ist das Gedächtnis des Systems. Die Anforderung "keine Doppelbewerbungen" ist eine Datenbankfrage, keine KI-Frage. Das vollständige Schema liegt in [`db/schema.sql`](../db/schema.sql); dieses Dokument erklärt die Absicht hinter den Tabellen.

## Tabellen

### `companies` – Firmenidentität

Eine Zeile pro **realer Firma**, unabhängig davon, aus wie vielen Quellen sie auftaucht.

| Spalte | Bedeutung |
|---|---|
| `id` | PK |
| `canonical_name` | Bereinigter Anzeigename ("Müller AG") |
| `normalized_name` | Für Matching: lowercase, ohne Rechtsform (AG/GmbH/SA/Sàrl/KG/e.U.), ohne Sonderzeichen, Umlaute normalisiert |
| `domain` | Primäre Web-Domain (`mueller.ch`). **Das stärkste Identitätsmerkmal.** NULL, wenn unbekannt |
| `country`, `region`, `city` | Für Filter |
| `industry_code`, `industry_label` | NOGA (CH) / ÖNACE (AT) / WZ (DE), falls aus Register bekannt |
| `size_hint` | `micro/small/medium/large/unknown` |
| `website`, `careers_url`, `application_email`, `application_url` | Aus Recherche (T6) |
| `research_summary` | Freitext aus T6: Was macht die Firma, Ton, Anknüpfungspunkte |
| `research_at` | Wann recherchiert; nach 180 Tagen gilt Recherche als veraltet |
| `status` | `discovered / prioritized / researched / no_contact / suggested / applied / blocked` |
| `blocked`, `blocked_reason`, `blocked_at` | Sperre durch Paula (`/block`) oder Regel |
| `reject_count` | Wie oft Paula Vorschläge zu dieser Firma verworfen hat |
| `last_contact_at` | Letzter Versand an diese Firma (aus applications abgeleitet, denormalisiert für schnelle Sperrfrist-Prüfung) |
| `source`, `source_ref` | Woher der Eintrag stammt (zefix, adzuna, inbox, manual, …) |
| `created_at`, `updated_at` | |

**`company_aliases`** (`company_id`, `alias`, `normalized_alias`, `source`) – alle Schreibweisen, unter denen die Firma je aufgetaucht ist. Wird beim Matching abgefragt.

**`company_domains`** (`company_id`, `domain`) – Absender-Domains aus Mails, die dieser Firma zugeordnet wurden (z. B. `recruiting.mueller.ch`, `mueller-group.com`). Für die Zuordnung eingehender Mails.

### `jobs` – Inserate

| Spalte | Bedeutung |
|---|---|
| `id` | PK |
| `fingerprint` | UNIQUE. sha256 über `normalized(company) + "|" + normalized(title) + "|" + normalized(location)`. Verhindert dasselbe Inserat aus zwei Quellen |
| `source`, `source_id`, `source_url` | Quelle + deren ID + Link. UNIQUE(source, source_id) |
| `company_id` | FK, NULL bis Firma zugeordnet |
| `company_name_raw` | Wie die Quelle die Firma nennt |
| `title`, `location`, `workload` (Pensum %), `employment_type`, `salary_min/max/currency` | Normalisierte Felder |
| `description` | Volltext (kann lang sein) |
| `posted_at`, `fetched_at`, `expires_at` | |
| `prefilter_result` | `pass / fail:<grund>` – Regelvorfilter |
| `score`, `score_reasoning`, `score_concerns`, `scored_at`, `score_model` | Aus T5 |
| `status` | `new / prefiltered_out / scored / below_threshold / proposed / applied / expired / duplicate` |

### `applications` – Bewerbungen (Portal **und** spontan)

| Spalte | Bedeutung |
|---|---|
| `id` | PK |
| `company_id` | FK, NOT NULL |
| `job_id` | FK, NULL bei Spontanbewerbung |
| `kind` | `portal / spontaneous / historical` (historical = aus der Mailbox rekonstruiert) |
| `status` | siehe Status-Maschine unten |
| `subject`, `body_text` | Der tatsächlich gesendete (oder zu sendende) Text |
| `attachments` | JSON-Liste von Dateinamen aus `data/documents/` |
| `to_email`, `to_name` | Empfänger |
| `gmail_thread_id`, `gmail_message_id` | Für Antwort-Zuordnung |
| `sent_at`, `first_reply_at`, `closed_at` | |
| `outcome` | `none / rejected / interview / offer / withdrawn / no_reply` |
| `draft_version` | Zähler für Revisionen (T11) |
| `confidence` | Bei `historical`: wie sicher die Rekonstruktion ist (0–1) |
| `created_at`, `updated_at` | |

**`application_drafts`** (`application_id`, `version`, `subject`, `body_text`, `generated_by`, `feedback_text`, `factcheck_result` JSON, `created_at`) – jede Entwurfsversion wird behalten. Wichtig für Lernen: Was ändert Paula regelmäßig?

### `messages` – relevante Mails

| Spalte | Bedeutung |
|---|---|
| `id` | PK |
| `gmail_message_id` | UNIQUE |
| `gmail_thread_id` | |
| `direction` | `in / out` |
| `from_email`, `from_name`, `to_email`, `subject`, `date` | |
| `body_text` | Bereinigter Text (ohne Zitate/Signatur, siehe `mail/parse.py`). **Kein HTML, keine Anhänge speichern** |
| `application_id` | FK, NULL wenn nicht zuordenbar |
| `company_id` | FK, NULL |
| `kind` | `application_sent / ack / rejection / interview / question / offer / followup / other / unrelated` |
| `classification_confidence`, `classified_by` (model), `classified_at` | |
| `needs_human` | 1, wenn Klassifikation unsicher (< 0.7) oder `kind=other` mit Bezug |
| `raw_snippet` | Erste 300 Zeichen für Anzeige |

Datenschutz-Regel: Es werden nur Mails gespeichert, die als bewerbungsbezogen klassifiziert wurden (kind ≠ unrelated). Für `unrelated` wird nur `gmail_message_id` + `kind` in `messages_seen` abgelegt, damit sie nicht nochmal geprüft werden.

**`messages_seen`** (`gmail_message_id` PK, `seen_at`, `verdict`) – alle je geprüften Mail-IDs.

### `approvals` – die Freigabe-Schleife

| Spalte | Bedeutung |
|---|---|
| `id` | PK |
| `kind` | `application_draft / reply_draft / block_company_question / info` |
| `application_id`, `message_id` | Bezug |
| `status` | `pending / approved / revise / rejected / expired / superseded` |
| `telegram_chat_id`, `telegram_message_id` | Um die Nachricht später zu editieren ("✅ gesendet um 09:14") |
| `sent_to_user_at`, `decided_at` | |
| `decision_by` | Telegram-User-ID |
| `feedback_text` | Freitext bei `revise` |
| `expires_at` | Standard +7 Tage; danach `expired`, Paula bekommt Erinnerung nach 3 Tagen |

Regel: Pro `application_id` darf es nur **ein** `pending` Approval geben (partieller UNIQUE-Index). Eine Revision setzt das alte auf `superseded` und legt ein neues an.

### `events` – Protokoll

`id, ts, kind, actor (system/user/admin), entity_type, entity_id, payload JSON`. Jede Statusänderung, jeder Versand, jeder LLM-Call (mit Token-Zahlen und Kosten), jeder Fehler. Wird nie gelöscht, nur archiviert.

### `llm_calls` – Kosten und Nachvollziehbarkeit

`id, ts, task (T1…T11), model, input_tokens, output_tokens, cache_read_tokens, cost_usd, duration_ms, entity_type, entity_id, ok, error`. Grundlage für `paula report --costs` und für das Budget-Limit.

### `sync_state` – Fortschritt der Batch-Jobs

`key TEXT PK, value TEXT, updated_at`. Beispiele: `gmail.history_id`, `gmail.initial_scan_done`, `adzuna.last_run_at`, `zefix.last_import_at`.

### `settings_runtime` – umschaltbare Zustände

`key, value`. Beispiele: `paused` (Paula `/pause`), `stopped` (Paula `/stop`, nur Admin hebt auf), `kill_switch` (Admin), `daily_proposals_sent:<date>`.

## Status-Maschine für `applications`

```
                         ┌──────────────┐
                         │  discovered  │  (nur portal: Job gefunden, Firma zugeordnet)
                         └──────┬───────┘
                                ▼
                         ┌──────────────┐
                         │   drafting   │  T6/T7/T8 laufen
                         └──────┬───────┘
                 ┌──────────────┼──────────────────┐
                 ▼              ▼                  ▼
        ┌────────────────┐ ┌──────────┐    ┌───────────────┐
        │pending_approval│ │factcheck_│    │ draft_failed  │  (LLM-Fehler, kein Kontakt)
        └───┬────┬───┬───┘ │ failed   │    └───────────────┘
            │    │   │     └──────────┘
   approved │    │   │ rejected_by_user
            │    │   └───────────────────────────┐
            │    │ revise → (T11) → pending_approval (neue Version)
            ▼    │                               ▼
        ┌────────┴──────┐                 ┌──────────────────┐
        │   approved    │                 │ rejected_by_user │
        └──────┬────────┘                 └──────────────────┘
               │ send_application() [nur im Sendefenster, unter Limit]
               ▼
        ┌──────────────┐
        │     sent     │──────────────┐ (nach settings.no_reply_days, Start 42)
        └──────┬───────┘              ▼
               │              ┌───────────────┐
      Antwort  │              │   no_reply    │ → optional followup_suggested
               ▼              └───────────────┘
        ┌──────────────┐
        │ acknowledged │  (Eingangsbestätigung; kein Telegram)
        └──────┬───────┘
               ▼
   ┌───────────┼─────────────┬──────────────┐
   ▼           ▼             ▼              ▼
┌────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│rejected│ │interview │ │ question │ │  offer   │
└───┬────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘
    │           │            │            │
    └───────────┴────────────┴────────────┴──▶ closed (Paula oder Betreiber schließt; oder automatisch 90 Tage nach letzter Aktivität)
```

Erlaubte Übergänge sind in `state.py` als Tabelle hinterlegt. `state.transition(app, new_status, actor, reason)` prüft, schreibt Event, aktualisiert `updated_at`. Direkte UPDATEs auf `status` außerhalb dieser Funktion sind verboten (Code-Review-Kriterium).

Historische Bewerbungen (`kind=historical`) werden direkt in `sent`, `acknowledged`, `rejected`, `interview` oder `closed` angelegt, mit `confidence`.

## Dedup- und Sperrfrist-Regeln

Bevor eine Bewerbung in `drafting` geht, prüft `dedup.py`:

1. **Firma gesperrt?** `companies.blocked = 1` → stop.
2. **Sperrfrist Firma:** `companies.last_contact_at > now - settings.dedup.company_cooldown_days` (Start 180) → stop, Grund `cooldown`.
3. **Gleiche Stelle:** existiert `applications` mit `job_id` = dieser Job, oder mit gleichem `jobs.fingerprint` → stop, Grund `same_job`.
4. **Offene Bewerbung:** existiert `applications` bei dieser Firma mit status ∈ {pending_approval, approved, sent, acknowledged, interview, question, offer} → stop, Grund `open_application`.
5. **Historisch unsicher:** existiert `historical` mit `confidence < 0.6` bei dieser Firma → **nicht** stoppen, aber im Telegram-Vorschlag warnen: "Du hattest dich vermutlich im März 2025 hier beworben – bin nicht sicher."

## Firmen-Matching (wann ist es dieselbe Firma?)

Reihenfolge, erster Treffer gewinnt:

1. `domain` identisch (nach Normalisierung: ohne `www.`, lowercase) oder in `company_domains`.
2. `normalized_name` identisch oder in `company_aliases.normalized_alias`.
3. `rapidfuzz.fuzz.token_set_ratio(normalized_name, kandidat) ≥ 92` **und** gleiche Stadt → match, Alias anlegen.
4. Ratio 80–91 → **LLM T2** entscheidet (mit Kontext: Ort, Branche, Website). Ergebnis wird als Alias gespeichert, damit dieselbe Frage nie zweimal gestellt wird.
5. Sonst: neue Firma.

Normalisierung von Firmennamen (`dedup.normalize_company`): lowercase → Umlaute/Akzente transliterieren (ä→ae, é→e) → Rechtsform-Suffixe entfernen (Liste in `config/legal_forms.txt`: ag, gmbh, sa, sàrl, sarl, sagl, kg, ohg, e.u., ltd, inc, se, & co, u. a.) → Interpunktion raus → Mehrfach-Leerzeichen → trim.

## Migrationen

`db/schema.sql` ist der Zielzustand. `db/migrations/NNN_*.sql` sind Deltas. `db.py:migrate()` führt alle Migrationen aus, die höher sind als `PRAGMA user_version`, in einer Transaktion je Datei, und setzt `user_version`. Erste Migration = gesamtes Schema. Kein ORM, keine Auto-Migration.

## Backup

`paula backup` → `sqlite3 .backup` (Online-Backup-API über Python) nach `data/backups/paula-YYYYMMDD-HHMM.db`, 14 Tage aufbewahren. Täglich per Timer. Zusätzlich optional `rclone` an ein Ziel des Betreibers (offene Frage).
