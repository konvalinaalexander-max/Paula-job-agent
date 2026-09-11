# 07 – Etappenplan

Zehn Etappen, strikt nacheinander. Jede ist für sich nützlich; nach jeder kann man aufhören und hat etwas gewonnen. Bis einschließlich M4 verlässt **nichts** das System. Erst M5 schaltet den Versand frei – und auch dann nur nach Abnahme.

Format je Etappe: Ziel → Voraussetzungen → Aufgaben (nummeriert, in Reihenfolge) → Deliverables → Tests → Definition of Done (DoD) → Abnahme durch Menschen → Risiken/Hinweise. Zeitangaben sind grobe Erwartungen für eine ausführende KI mit Rückfragen an einen nicht-technischen Auftraggeber.

---

## M0 – Fundament (Repo, Konfiguration, Einwilligung, Zugänge)

**Ziel:** Alles, was danach kommt, hat einen Ort, eine Konfiguration und die nötigen Schlüssel. Noch keine Fachlogik.

**Voraussetzungen:** Antworten auf die blockierenden Fragen Q1–Q4 in `08-open-questions.md`.

**Aufgaben:**
1. `pyproject.toml` (uv, ruff, pytest-Konfig, Entry-Point `paula = paula.cli:app`), `uv sync`, `uv run paula --help` funktioniert.
2. `src/paula/config.py`: lädt `.env` (pydantic-settings), `config/settings.yaml`, `config/profile.yaml`; validiert mit Pydantic; klare Fehlermeldung, wenn etwas fehlt. Alle Defaults aus `config/*.example.yaml`.
3. `src/paula/db.py`: Verbindung mit WAL + `busy_timeout` + `foreign_keys`, `migrate()` über `db/migrations/*.sql` und `PRAGMA user_version`. `paula db migrate`.
4. `src/paula/events.py`, `src/paula/llm/client.py` (Anthropic-Client-Wrapper: Fallbacks, Retry, `llm_calls`-Logging, Budgetprüfung, Cache-Header-Helfer), `src/paula/state.py` (Übergangstabelle aus `02-data-model.md`).
5. `paula doctor`: prüft Python-Version, `.env`-Vollständigkeit, Dateirechte, Anthropic-Testcall, Telegram `getMe`, Adzuna-Testsuche, DB-Migration-Stand.
6. `docs/einwilligung.md` nach Gliederung in `05-safety-legal.md`; `paula consent`-Befehl.
7. `deploy/SETUP.md` (Runbook für den Betreiber, Schritt für Schritt, mit Screenshot-Beschreibungen für Google Cloud Console, BotFather, Adzuna-Registrierung, Hetzner), `deploy/*.service`, `deploy/*.timer`, `deploy/install-systemd.sh`, `deploy/deploy.sh`.
8. `tests/conftest.py` mit In-Memory-DB-Fixture, Settings-Fixture, `tests/test_config.py`, `tests/test_db.py`, `tests/test_state.py`.
9. Logging-Setup (`structlog`, JSON, Maskierung von Mailadressen und Body-Feldern).

**Deliverables:** lauffähiges Package ohne Fachlogik; `doctor` grün auf dem Laptop des Betreibers (oder dem VPS).

**DoD:** `uv run pytest` grün; `paula doctor` zeigt alle Checks; Einwilligungsdokument existiert; Betreiber hat alle Zugänge (Anthropic-Key, Telegram-Token, Adzuna-Keys, Google-Cloud-Projekt mit `credentials.json`).

**Abnahme:** Betreiber führt `paula doctor` aus, versteht die Ausgabe, hat die Einwilligung mit Paula durchgesprochen.

**Risiken:** Google-Cloud-Console ist für Nicht-Techniker verwirrend → Runbook muss wirklich Schritt für Schritt sein. Hetzner-Bestellung kann 1 Tag Identitätsprüfung dauern.

---

## M1 – Mailbox lesen, Historie rekonstruieren (nur lesen)

**Ziel:** Das System kennt Paulas Bewerbungsvergangenheit: welche Firmen, wann, welche Stelle, was kam zurück. Ausgabe: eine Tabelle, die der Betreiber mit Paula durchgeht.

**Voraussetzungen:** M0; Einwilligung bestätigt (`sync_state.consent_confirmed_at`); OAuth-Login mit **Sandbox-Konto** (erst nach M5 mit Paulas Konto).

**Aufgaben:**
1. `mail/gmail.py`: OAuth-Flow (Desktop, headless-fähig), Token-Refresh, `list_messages(query, pages)`, `get_message(id)`, `list_history(start_id)`, `get_profile()`, Labels anlegen/setzen. Retry/Backoff.
2. `mail/parse.py`: MIME → Text (plain bevorzugt, HTML-Fallback), Zitate/Signaturen entfernen, Anhänge nur als Metadaten, Absender-Domain extrahieren. 15+ Unit-Tests mit Fixture-`.eml`.
3. `llm/tasks.py: classify_mail_triage()` (T1a, Haiku, Batch-API für `--initial`) und `classify_mail()` (T1b, Opus). Schemas in `llm/schemas.py`. Prompts in `prompts/t1_*.md` verfeinern.
4. `dedup.py`: `normalize_company()`, Rechtsformen-Liste, Fingerprint, `find_or_create_company()` mit den 5 Matching-Stufen (T2 für Stufe 4).
5. `pipeline/inbox.py`: `--initial`-Modus (Query über `history_months`, beide Richtungen, Batch-Triage, Extraktion, `messages` + `companies` + `applications(kind=historical)` anlegen, Labels setzen, `history_id` speichern) und inkrementeller Modus (History-API, 404-Fallback). Idempotent über `messages_seen`.
6. Rekonstruktionslogik: Gesendete Mail mit `kind=application_sent` → `application(historical, sent, confidence)`; spätere Mails im gleichen Thread oder von gleicher Domain → Status-Fortschreibung (ack/rejection/interview). Konfidenz sinkt, wenn Zuordnung nur über Domain und Zeitfenster.
7. `paula report --history`: Tabelle (Firma, Stelle, Datum, Ergebnis, Konfidenz) als Markdown + CSV in `data/reports/`.
8. Fixtures: 40+ synthetische Mails mit `expected.yaml`; `seed_mailbox.py`; Golden-Test T1.

**Deliverables:** `paula scan-inbox --initial` gegen Sandbox-Konto füllt DB korrekt; Report lesbar.

**Tests:** parse (Unit), dedup (Unit, alle Fälle aus `11-testing.md`), inbox-Pipeline gegen Fake-Gmail (Integration), T1-Golden ≥ 90 %.

**DoD:** Sandbox-Lauf ohne Fehler; zweiter Lauf erzeugt 0 neue Zeilen (Idempotenz); Report zeigt alle 12 gesäten historischen Bewerbungen mit korrektem Ergebnis; `unrelated`-Mails haben keinen Body in der DB.

**Abnahme:** Betreiber vergleicht Report mit den gesäten Mails. Danach – und erst danach – Entscheidung, ob mit Paulas echtem Konto der `--initial`-Lauf gemacht wird (Paula loggt sich selbst ein). Nach dem echten Lauf geht der Betreiber den Report **mit Paula** durch; falsche Zuordnungen werden per `paula debug application <id> --set-status …` korrigiert.

**Risiken:** Paulas Mailbox kann groß sein (Batch-API dauert bis zu Stunden – okay, asynchron). Mehrsprachigkeit (FR/IT) im Query nicht vergessen. Google-Testing-Modus-Falle (7-Tage-Token) → in SETUP.md fett.

---

## M2 – Stilprofil und Faktenblock

**Ziel:** Das System kann wie Paula klingen und weiß, was über sie wahr ist.

**Voraussetzungen:** M1 mit echtem Konto abgenommen (für Stil); Paulas CV als PDF in `data/documents/`.

**Aufgaben:**
1. `paula style build`: sammelt `messages(direction=out, kind=application_sent)` (min. 8, ideal 15–40), T3, rendert `data/style_profile.draft.md`. Bei < 8: Hinweis, welche Beispiele Paula liefern sollte; `--extra-samples <ordner>` für Texte, die Paula per Telegram/Datei nachliefert.
2. `paula facts build --cv …`: T4 mit PDF als Document-Block, rendert `data/facts.draft.md`. Mehrere Dokumente (Zeugnisse) möglich, `unclear_items` prominent oben.
3. `profile.yaml` vollständig mit Paula ausfüllen: Zielrollen, Orte + Radius, Pensum, Branchen, No-Gos, Sprachen, Anhänge, `locale`.
4. `llm/prompts.py`: Rendering mit Stil + Fakten als **gecachter** Systemprompt-Block; `paula doctor --cache` bestätigt Cache-Hits.
5. Optional: Paula kann per Telegram (M3 vorgezogen) oder per Datei eine Liste "Dinge, die ich nicht mehr will / die mir wichtig sind" liefern → `facts.md` Abschnitt "Präferenzen".

**Deliverables:** `data/style_profile.md`, `data/facts.md` – beide **von Paula gelesen und freigegeben** (Betreiber dokumentiert das im Etappenbericht).

**DoD:** Beide Dateien existieren, sind nicht `.draft`; Golden-Test "T7-Probelauf ohne Versand" (`paula replay --fixture`) erzeugt für 3 Fixture-Inserate Entwürfe, die der Betreiber Paula zeigt: sie sagt "klingt nach mir" oder nennt Korrekturen → Stilprofil nachbessern, wiederholen (max. 3 Runden in dieser Etappe).

**Abnahme:** Paulas Urteil über die 3 Probe-Entwürfe. Das ist die wichtigste Abnahme des Projekts – wenn die Texte nicht nach ihr klingen, wird sie das System nicht benutzen.

---

## M3 – Telegram-Bot und Freigabe-Mechanik (ohne Versand)

**Ziel:** Paula kann mit dem System reden; Freigabe-Karten funktionieren technisch; noch nichts wird verschickt.

**Aufgaben:**
1. `channels/telegram_send.py`: `send_message`, `edit_message`, `send_card(approval)` mit Inline-Keyboards, Splitting bei 4096, HTML-Escaping.
2. `channels/render.py`: alle Karten aus `10-telegram-flows.md` als Funktionen mit Fixture-Tests (Snapshot-Tests des erzeugten Textes).
3. `channels/telegram_bot.py`: Daemon mit Handlern für alle Befehle und Callbacks; Chat-ID-Whitelist; Conversation-State in `settings_runtime`; Idempotenz; `awaiting_feedback`-Timeout.
4. `approvals`-Logik: anlegen, entscheiden, superseded bei Revision, `expires_at`, Reminder-Job (`paula reminders`, Teil von `run-cycle`).
5. `/status`, `/list`, `/pause`, `/resume`, `/stop`, `/block` (mit Fuzzy-Suche über companies), `/add`, `/settings`, `/help`; Admin-Befehle.
6. `paula demo-card`: erzeugt eine Fixture-Freigabekarte und schickt sie an `TELEGRAM_USER_CHAT_ID` – zum Ausprobieren aller Buttons ohne echte Bewerbung. Entscheidungen landen in `approvals`, `send.py` existiert noch nicht → nichts passiert außer Karten-Update.
7. systemd-Unit `paula-bot.service` live auf dem VPS.

**Deliverables:** Bot läuft dauerhaft; alle Flows mit Demo-Karten durchspielbar.

**Tests:** Handler gegen Fixture-Updates (jeder Befehl, jeder Callback, unbekannter Nutzer, Doppelklick, State-Timeout); Renderer-Snapshots.

**DoD:** Bot überlebt Neustart mit offenem `awaiting_feedback`-State; unbekannte Chat-ID bekommt nur "privat"; Demo-Karte: ✅ → Karte editiert, `approvals.status=approved`; ✏️ → Feedback-Text landet in `approvals.feedback_text`; ❌ → rejected; Reminder nach konfigurierter Zeit erscheint (Zeit für Test auf 2 Minuten stellbar).

**Abnahme:** Betreiber **und Paula** klicken sich durch Demo-Karten. Paulas Feedback zur Tonalität der Nachrichten wird eingearbeitet.

---

## M4 – Erste Jobquelle, Scoring, Entwurf, Faktencheck (Dry-Run, Karten echt)

**Ziel:** Der Hauptpfad funktioniert Ende-zu-Ende bis zur Freigabe-Karte. Freigabe führt zu einer `.eml` in `data/outbox/`, nicht zu einer Mail.

**Aufgaben:**
1. `sources/base.py`, `sources/adzuna.py` (mit `enrich()` via JSON-LD/Haupttext, respx-Tests gegen aufgezeichnete Antworten), Personalvermittler-Liste.
2. `sources/mailalert.py` für die Portale aus Q7 (Parser je Portal mit Fixture-Mail), Integration in `scan-inbox`.
3. `sources/manual.py` (/add-Verarbeitung).
4. Regel-Vorfilter (`pipeline/portals.py:prefilter()`): Ort/Radius (Geocoding über einfache Ortsliste in `config/places.csv` + Haversine, kein externer Dienst), Pensum, Ausschlusswörter aus `profile.exclude_keywords`, Sprache, gesperrte Firmen, Sperrfrist. Jeder Ausschluss mit Grund in `prefilter_result`.
5. T5 Scoring inkl. Kalibrierungs-Logik; T6 Firmenrecherche (Server-Tools) für Firmen ohne Recherche; T7 Entwurf; T8 Faktencheck + Regeln; T11 Revision.
6. `pipeline/drafts.py`: Entwurf → Faktencheck → ggf. Regenerierung → `applications(pending_approval)` + `approvals` + Karte. Tageslimit `proposals_per_day`; Rest bleibt `scored` in Reihenfolge Score.
7. `mail/send.py` **mit allen 10 Prüfungen**, aber `dry_run` fest `true` in dieser Etappe (Setting wird ignoriert; Freischaltung erst M5).
8. `paula sweep-portals`, `paula run-cycle` (ohne send-approved), Timer aktiv.
9. Fixtures: 25 Inserate, 10 Recherchen; Golden-Tests T5/T7/T8; Injection-Tests.

**Deliverables:** Echte Adzuna-Suche → echte Karten an Paula → Freigabe → `.eml` in outbox.

**DoD:** 3 Tage Betrieb im Dry-Run; ≥ 10 Karten erzeugt; Betreiber liest alle `.eml` in outbox: korrekte Empfänger, Anhänge, Betreff, Thread-Header; Faktencheck-Log zeigt keine `major`-Durchläufe; Kalibrierung: Paulas Approve-Quote ≥ 50 % (sonst Threshold anpassen, weitere 3 Tage).

**Abnahme:** Betreiber + Paula. Paula bewertet, ob die Vorschläge sinnvoll sind (nicht ob sie perfekt sind).

**Risiken:** Adzuna-Beschreibungen gekürzt → `enrich` wichtig. T6 mit Server-Tools + strukturiertem Output: ausführende KI prüft, ob `output_config.format` mit Server-Tools kombinierbar ist, sonst zweiter `parse`-Call. Geocoding ohne externen Dienst ist grob – reicht für "im Radius".

---

## M5 – Echter Versand

**Ziel:** Freigegebene Bewerbungen gehen raus. Der Kreis schließt sich.

**Voraussetzungen:** M4 abgenommen; Umstellung auf Paulas echtes Gmail-Konto (falls nicht schon in M1 geschehen); SPF/DKIM sind bei Gmail automatisch.

**Aufgaben:**
1. `send.py`: `dry_run` aus Settings respektieren; Gmail-Send mit Multipart + Anhängen; `messages(direction=out)`; Karte editieren; `companies.last_contact_at`.
2. `send-approved` in `run-cycle`; Sendefenster-Logik mit Zeitzone; `min_minutes_between_sends` über `events`.
3. Fehlerpfad: Gmail-Fehler → Retry-Zähler in `approvals`, Paula-Info nach 1., Admin nach 3. Versuch.
4. **Sicherheitstests vollständig** (`test_send_guard.py`, alle Fälle aus `11-testing.md`).
5. Erster echter Versand: **eine** Bewerbung, die Paula ohnehin schicken wollte, vom Betreiber live beobachtet (Journal), Empfang in "Gesendet" geprüft, Thread-ID gespeichert.
6. `settings.dry_run: false` setzen – bewusst, dokumentiert im Etappenbericht.

**DoD:** Sicherheitstests grün; erste echte Mail korrekt angekommen (Testempfänger = Betreiber-Adresse als "Firma" für den allerersten Versand, dann eine echte); Tageslimit greift nachweislich (Test mit `sends_per_day=1`).

**Abnahme:** Betreiber. Paula wird informiert: "Ab jetzt geht's echt raus, wenn du ✅ drückst."

---

## M6 – Antworten lesen, einordnen, reagieren

**Ziel:** Der Rückkanal. Absagen, Einladungen, Rückfragen werden erkannt und Reaktionen vorgeschlagen.

**Aufgaben:**
1. `pipeline/replies.py`: inkrementeller Gmail-Scan → Zuordnung (Thread-ID → Absender-Domain → Betreff-Fuzzy → T9 mit Kandidatenliste) → `messages` → Status-Übergang.
2. T9, T10 mit allen Regeln aus `03-llm-tasks.md` (Termin nie zusagen, Rückfragen nur aus Fakten, Angebot nur melden).
3. Karten Flow 4 komplett (Absage/Einladung/Rückfrage/Angebot/Unklar), Termin-Auswahl-Buttons, `{{TERMIN}}`-Ersetzung.
4. Antwort-Versand über `send.py` mit Thread-Headern (`In-Reply-To`, `References`, `threadId`).
5. `no_reply`-Logik nach `no_reply_days`, Nachfass-Vorschlag in `/list` und Wochenreport; Nachfass-Entwurf (T10-Variante `followup`).
6. `/close <n>`; automatisches `closed` nach 90 Tagen Inaktivität.
7. Fixtures: alle Antworttypen, Threads mit Zitatketten; Golden-Test T9 ≥ 90 %.

**DoD:** Sandbox-Test: gesäte Antworten auf gesendete Bewerbungen werden korrekt zugeordnet und klassifiziert; Absage-Antwort geht nach ✅ im richtigen Thread raus (Betreiber prüft in Gmail, dass es als Antwort erscheint); Einladung erzeugt Termin-Buttons; Rückfrage mit unbekanntem Fakt zeigt ❓ und kein ✅.

**Abnahme:** Betreiber + Paula (Paula prüft Ton der Absage-Antworten – hier ist Ton alles).

---

## M7 – Spontanbewerbungen

**Ziel:** Firmen-Discovery, Priorisierung, Recherche, gezielte Initiativbewerbungen.

**Aufgaben:**
1. `companies/discovery.py`: Importer für die Quellen aus Q1-Land (CH: Zefix-Client mit Basic Auth + Rate-Limit, opendata-CSV-Importer; plus `companies_seed.csv`, plus Ableitung aus Mailbox/Inseraten). `paula import-companies`.
2. `prioritize()` regelbasiert nach `04-integrations.md` 4.5; `priority_score`; Wochenreport-Zahlen.
3. `pipeline/companies.py`: Top-N pro Nacht → T6 → T5b → Entwurf (Variante spontan) → Karte B. Limits `spontaneous_per_week`, `companies_research_per_night`.
4. Domain-Check für `application_email` (4.6 Punkt 7 + T6-Guardrail); `no_contact`-Pfad; `accepts_spontaneous=no`-Regel.
5. Text-Ähnlichkeitsprüfung gegen letzte 20 Sendungen (Jaccard < 0.7).
6. `sources/careerpage.py` für recherchierte Firmen mit `careers_url` (+ Adapter Greenhouse/Lever/Personio/SmartRecruiters, wenn erkannt).
7. `/settings` Schalter "Spontanbewerbungen an/aus".

**DoD:** Discovery-Import für Paulas Region läuft (Zahlen im Report); 5 Nächte Betrieb; ≥ 5 Karten B; Betreiber prüft Recherche-Zusammenfassungen stichprobenartig gegen die echten Websites (keine Halluzinationen bei Adresse/Kontakt); Paulas Approve-Quote bei Spontan-Karten ≥ 40 %.

**Abnahme:** Betreiber + Paula.

**Risiken:** Zefix-Zugang/Format (verifizieren); Kontaktadressen oft nicht auf Website → viele `no_contact` (dann Karriereportal-Link + "Bewirb dich über ihr Formular, hier dein Text" als Karten-Variante).

---

## M8 – Betriebsreife

**Ziel:** Läuft wochenlang ohne Eingriff.

**Aufgaben:**
1. Alle Admin-Benachrichtigungen aus `06-operations.md` 6.4; Watchdog-Timer; Healthchecks.io optional.
2. Backups + Off-Site + **Restore-Test** (dokumentiert in `deploy/RESTORE.md`).
3. `paula export --for-user`, `paula purge`.
4. Wochenreport (Flow 11) automatisch; `/report`; `--costs`.
5. Kalibrierungs-Loop: Threshold-Anpassung aus Approve-Quote; Vorschlag im Wochenreport ("Radius kleiner?").
6. Log-Retention, Journal-Limits, `unattended-upgrades` geprüft.
7. `deploy/SETUP.md`, `deploy/RUNBOOK.md` (was tun bei: Gmail 401, Telegram down, Budget überschritten, Quelle deaktiviert, Paula /stop, VPS neu aufsetzen).
8. Prompt-Review: alle Golden-Tests erneut, Ergebnisse in `tests/llm_results/`.

**DoD:** 14 Tage Betrieb ohne manuellen Eingriff; alle Admin-Alarme einmal ausgelöst und geprüft (simuliert); Restore-Test bestanden; Wochenreport kam 2× automatisch.

**Abnahme:** Betreiber.

---

## M9 – Optional / Später (nicht ohne neue Entscheidung des Auftraggebers)

- Weitere Quellen (Arbeitsagentur DE, AMS AT, JobSpy nach Q8, job-room-Endpunkt).
- PDF-Anschreiben zusätzlich zur Mail (A12 aufheben) – nur wenn Portale/Firmen es verlangen.
- Formular-Hilfe: Für Stellen, die nur ein Web-Formular haben, liefert die Karte Text-Bausteine zum Kopieren (kein Auto-Fill).
- Mehrsprachigkeit der Bot-Oberfläche (FR).
- Web-Dashboard für den Betreiber (read-only).
- Lern-Loop: Aus `application_drafts` mit Feedback automatische Vorschläge zur Stilprofil-Anpassung (nur Vorschläge, Mensch entscheidet).
- Kalender-Integration für Einladungen (Google Calendar, `calendar.events` – neuer Scope, neue Einwilligung).
- Docker-Variante der Deployment-Doku.

---

## Reihenfolge-Begründung in einem Absatz

M1 vor allem anderen, weil die Historie die Dedup-Grundlage ist und weil es der einzige Schritt ist, der nur liest – ideal zum Lernen der Infrastruktur. M2 vor M3, weil ohne Stil und Fakten kein Entwurf sinnvoll ist, und weil Paulas "klingt nach mir" die kritischste Abnahme ist – lieber früh scheitern. M3 vor M4, weil die Karten das Interface sind, das M4 braucht. M4 im Dry-Run, damit Scoring und Entwürfe über Tage kalibriert werden können, ohne dass ein einziger Fehler rausgeht. M5 ist bewusst klein: nur der Schalter und die Sicherheitstests. M6 nach M5, weil Antworten erst kommen, wenn gesendet wurde. M7 zuletzt, weil Spontanbewerbungen die riskanteste, teuerste und am schwersten zu bewertende Variante sind – bis dahin ist das System an Portal-Bewerbungen erprobt.
