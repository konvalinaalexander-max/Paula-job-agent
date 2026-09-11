# 11 – Teststrategie

Ziel: Der Betreiber kann jede Etappe abnehmen, ohne Paulas echte Daten zu riskieren, und die ausführende KI kann Prompts verbessern, ohne Bewerbungen zu verschicken.

## Ebenen

| Ebene | Werkzeug | Was |
|---|---|---|
| Unit | `pytest` | Normalisierung, Fingerprints, Status-Maschine, Limits, Sendefenster, MIME-Parsing, Callback-Parsing, Renderer |
| Integration (gemockt) | `pytest` + `respx` (httpx) + Gmail-Service-Fake | Adapter (Adzuna etc.) gegen aufgezeichnete Antworten; Telegram-Handler gegen Fake-Updates; Versand-Layer gegen Fake-Mailclient |
| LLM-Golden-Tests | `pytest -m llm` (nur auf Anfrage, kostet Geld) | Prompts gegen Fixture-Fälle mit erwarteten Bändern |
| End-to-End im Dry-Run | manuell, Runbook | Ganzer Zyklus mit Sandbox-Mailbox und Test-Telegram-Chat |
| Abnahme | Betreiber + Paula | Pro Etappe (siehe `07-milestones.md`) |

## Fixtures (`tests/fixtures/`)

Alle **synthetisch**, keine echten Daten. Die ausführende KI erzeugt sie in M1–M6, jeweils mit Erwartungswerten in einer `expected.yaml` daneben.

- `mails/` – 60+ `.eml`: Bewerbungen gesendet (DE/FR/EN, CH-Stil), Eingangsbestätigungen (automatisch, persönlich), Absagen (kurz, lang, freundlich, formal), Einladungen (mit 1/2/0 Terminvorschlägen), Rückfragen, Angebote, Jobportal-Newsletter, Job-Alert-Mails (jobs.ch, job-room, Indeed-Format), Spam, private Mails, Mails mit Zitatketten, HTML-only-Mails, Mails mit Injection-Text.
- `jobs/` – 25 Inserate als JSON (`RawJob`): gute Treffer, Grenzfälle, klare Fehltreffer, Personalvermittler, mit Hard-Blockern, Injection-Inserate, FR/IT-Inserate, gekürzte Beschreibung.
- `companies/` – 10 Recherche-Ergebnisse (`CompanyResearch`) für T5b/T7-Tests, inkl. `no_contact`, `accepts_spontaneous=no`.
- `profile/` – `facts.test.md`, `style_profile.test.md`, `profile.test.yaml` für eine fiktive Person "Paula Muster".
- `adzuna/` – 3 aufgezeichnete API-Antworten (anonymisiert).
- `telegram/` – Update-JSONs für jeden Flow (Command, Callback, Freitext, unbekannter Nutzer).

## Pflicht-Tests (müssen existieren, bevor eine Etappe als "done" gilt)

**Sicherheit (M5, `tests/test_send_guard.py`):**
- Jede der 10 Prüfungen in `mail/send.py` einzeln durchfallen lassen → kein Versand, Event mit Grund.
- Approval von falscher `chat_id` → kein Versand.
- Doppelter Callback → genau ein Versand.
- `dry_run=true` → Datei in outbox, Status `sent`, kein Mailclient-Aufruf.
- Kill-Switch gesetzt → alle Batch-Entrypoints beenden sich sofort.

**Dedup (M1/M4, `tests/test_dedup.py`):**
- "Müller AG" / "Mueller AG" / "MÜLLER AG, Zürich" / "Müller Aktiengesellschaft" → eine Firma.
- "Müller AG Zürich" vs "Müller GmbH Berlin" → zwei Firmen.
- Gleiches Inserat aus Adzuna und Mailalert → ein `jobs`-Eintrag.
- Sperrfrist: Bewerbung vor 100 Tagen → blockiert; vor 200 Tagen → erlaubt; Personalvermittler → nicht blockiert.
- Historische Bewerbung mit `confidence 0.5` → Warnung, nicht Block.

**Status-Maschine (`tests/test_state.py`):** Jeder erlaubte Übergang ok; jeder verbotene (`discovered → sent`, `rejected_by_user → approved`) wirft.

**Injection (`tests/test_injection.py`, `-m llm`):** 3 Inserate + 2 Mails mit Anweisungstext → Score im erwarteten Band, `concerns` erwähnt Auffälligkeit, Entwurf enthält keine der injizierten Inhalte, kein Empfänger außerhalb der Firmen-Domain.

**Faktentreue (`tests/test_factcheck.py`):** Entwurf mit erfundener Zahl → regelbasiert erkannt; Entwurf mit erfundenem Skill → T8 erkennt (`-m llm`); sauberer Entwurf → `passed`.

**Golden-Tests Prompts (`tests/test_llm_golden.py`, `-m llm`):** T1 Accuracy ≥ 90 % `kind`; T5 alle Fixture-Inserate im Erwartungsband; T7 Länge im Band, Grußformeln aus Stilprofil, keine verbotenen Phrasen, alle `claims` im Faktenblock. Ergebnis wird als `tests/llm_results/<datum>.json` gespeichert (in Git, damit Prompt-Änderungen vergleichbar sind).

## Dry-Run-Modus

`settings.dry_run: true`:
- `send.py` schreibt `.eml` nach `data/outbox/` statt zu senden.
- Telegram geht **echt** (das ist ja das, was getestet wird) – aber an `TELEGRAM_USER_CHAT_ID`, und der kann in der Testphase Alexanders eigener Chat sein.
- LLM-Calls gehen echt (kosten Geld; `--no-llm` in Batch-Befehlen schaltet auf Fixture-Antworten um, für Verdrahtungstests).

## Sandbox-Mailbox

Für M1–M5: ein **eigenes Gmail-Testkonto** des Betreibers, in das er 20–30 der synthetischen Fixture-Mails schickt (Skript `tests/tools/seed_mailbox.py` sendet sie über SMTP an das Testkonto). Erst nach Abnahme von M5 wird auf Paulas Konto umgestellt. So wird der gesamte Pfad inkl. OAuth, History-API, Labels an einer echten Mailbox geprüft, ohne Paulas Daten.

## Was bei jeder Etappe grün sein muss

`uv run ruff check . && uv run ruff format --check . && uv run pytest` (ohne `-m llm`). LLM-Tests einmal pro Etappe manuell mit Kostenausweis im Etappenbericht.
