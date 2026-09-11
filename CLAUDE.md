# Anweisungen für die ausführende KI

Du setzt das Projekt "Paula Job Agent" um. Der Plan liegt vollständig in `docs/`. Dieses Dokument sagt dir, **wie** du arbeitest. Der Plan sagt, **was** du baust.

## Wer hier wer ist

- **Auftraggeber (Alexander):** dein Ansprechpartner. Er kann nicht programmieren und hat noch nie KI-Agenten gebaut. Erkläre Entscheidungen kurz und ohne Jargon. Frage ihn, wenn `docs/08-open-questions.md` eine Frage als *blockierend* markiert und sie noch offen ist.
- **Nutzerin (Paula):** die Person, die den Job sucht. Sie hat keinen Zugang zu dir, zum Repo oder zu einer Konsole. Sie interagiert **ausschließlich** über Telegram. Alles, was sie sehen soll, muss durch `docs/10-telegram-flows.md` abgedeckt sein.

## Reihenfolge

Arbeite die Etappen in `docs/07-milestones.md` **strikt der Reihe nach** ab: M0 → M1 → … → M9. Jede Etappe hat eine *Definition of Done* mit Tests und einer menschlichen Abnahme. Beginne keine Etappe, bevor die vorherige abgenommen ist – frag den Auftraggeber explizit um die Abnahme.

Innerhalb einer Etappe: erst Datenmodell, dann Integration, dann LLM-Aufgabe, dann Tests, dann Doku. Nicht umgekehrt.

## Harte Regeln (gelten immer, überstimmen alles andere)

1. **Kein Versand ohne Freigabe.** Keine Mail, kein Formular, keine Nachricht an Dritte verlässt das System ohne eine explizite Freigabe-Aktion von Paula über Telegram, die in der Tabelle `approvals` protokolliert ist. Es gibt keinen "Auto-Send"-Modus. Baue ihn nicht, auch nicht als Feature-Flag.
2. **Keine erfundenen Fakten.** Generierte Texte dürfen nur Aussagen über Paula enthalten, die in `data/facts.md` stehen. Die Faktentreue-Prüfung (`docs/03-llm-tasks.md`, T8) ist Pflicht vor jeder Freigabe-Anfrage.
3. **Tageslimits sind hart.** Die Limits in `config/settings.yaml` (`limits.*`) werden im Code erzwungen, nicht nur im Prompt. Der Versand-Layer verweigert alles darüber hinaus.
4. **Secrets nie in Git.** `.env`, OAuth-Tokens, Datenbank, Mails, Lebenslauf, Profile: alles unter `data/` oder in `.env`, beides in `.gitignore`. Prüfe vor jedem Commit mit `git status`, dass nichts davon staged ist.
5. **Keine Portale scrapen, deren AGB das verbieten, ohne dass der Auftraggeber das ausdrücklich entschieden hat.** Siehe `docs/04-integrations.md`, Abschnitt Jobquellen, und `docs/08-open-questions.md`. Offizielle APIs und öffentliche Feeds sind immer okay.
6. **Idempotenz.** Jeder Batch-Lauf (`scan-inbox`, `sweep-portals`, …) muss beliebig oft wiederholbar sein, ohne Duplikate zu erzeugen. Das ist durch Fingerprints und UNIQUE-Constraints im Schema abgesichert – umgehe sie nicht.
7. **Dry-Run ist der Standard.** `settings.dry_run: true` ist der Auslieferungszustand. Im Dry-Run wird nichts versendet, sondern in `data/outbox/` geschrieben. Der Auftraggeber schaltet das um, nicht du.

## Tech-Stack (festgelegt, nicht neu diskutieren)

- Python 3.12, Paketmanager `uv`, Linter/Formatter `ruff`, Tests `pytest`
- SQLite (WAL-Modus) über `sqlite3` aus der Standardbibliothek, Schema in `db/schema.sql`, Migrationen als nummerierte SQL-Dateien in `db/migrations/`
- Pydantic v2 für alle Datenmodelle und LLM-Output-Schemas
- Anthropic Python SDK (`anthropic`) – **direkt**, kein LangChain, kein CrewAI, kein Agent-Framework. Strukturierte Ausgaben über `client.messages.parse(..., output_format=PydanticModel)`.
- Gmail API (`google-api-python-client`, `google-auth-oauthlib`); IMAP/SMTP nur als Fallback, wenn Paulas Anbieter nicht Google ist (siehe offene Fragen)
- `python-telegram-bot` (v21+, async)
- `httpx` für alle anderen HTTP-Aufrufe
- `typer` für die CLI, `structlog` für Logging
- systemd (Services + Timer) auf einem Linux-VPS; kein Docker in der ersten Version

Wenn du eine Bibliothek ergänzen willst: kurz begründen im Commit, in `docs/01-architecture.md` unter "Abhängigkeiten" eintragen.

## Modelle

Standard: `claude-opus-5` mit adaptivem Thinking. Für Massen-Vorsortierung (historischer Mailbox-Scan, tausende Mails) `claude-haiku-4-5`. Details je Aufgabe in `docs/03-llm-tasks.md`. Verwende exakt diese Modell-IDs, ohne Datumssuffix. Aktiviere Server-side-Fallbacks (`fallbacks`) wie im SDK dokumentiert.

## Arbeitsweise

- **Lies vor jeder Etappe** die betroffenen Docs vollständig. Sie sind detailliert; die Details sind absichtlich.
- **Wo der Plan eine Entscheidung offen lässt**, triff sie, dokumentiere sie in `docs/01-architecture.md` unter "Entscheidungen während der Umsetzung" und mach weiter. Frag nur bei den als blockierend markierten Fragen.
- **Wo der Plan sich als falsch herausstellt** (API existiert nicht mehr, Bibliothek inkompatibel), schreib das in `docs/09-research-notes.md` unter "Abweichungen", wähl die nächstbeste Lösung aus dem Plan (es gibt fast überall eine Alternative) und melde es dem Auftraggeber im Etappenbericht.
- **Commits:** klein, ein Thema pro Commit, deutsche oder englische Commit-Messages – konsistent bleiben. Kein Modellname in Commits oder Code.
- **Tests laufen vor jedem Push** (`uv run pytest`, `uv run ruff check .`).
- **Kein Feature-Creep.** Wenn dir etwas Sinnvolles auffällt, das nicht im Plan steht, schreib es in `docs/08-open-questions.md` unter "Vorschläge" statt es zu bauen.

## Etappenbericht (nach jeder Etappe an den Auftraggeber)

Kurz, in dieser Form:

1. Was gebaut wurde (3–6 Sätze, verständlich für Nicht-Programmierer)
2. Wie er es selbst ausprobieren kann (konkrete Befehle / Telegram-Nachrichten)
3. Was von ihm gebraucht wird, um weiterzumachen (Zugänge, Entscheidungen)
4. Abweichungen vom Plan und warum
5. Frage nach Abnahme

## Was du **nicht** tust

- Kein Auto-Apply über Web-Formulare (LinkedIn Easy Apply, Workday etc.). Nicht in Scope, siehe `docs/00-vision.md`.
- Keine Bewerbungen an Firmen, die in `companies.blocked = 1` stehen.
- Keine Änderung an `data/facts.md` oder `data/style_profile.md` ohne Freigabe – diese Dateien werden vom Menschen kuratiert, du schlägst nur Änderungen vor.
- Keine Erweiterung der OAuth-Scopes über das in `docs/04-integrations.md` Festgelegte hinaus.
