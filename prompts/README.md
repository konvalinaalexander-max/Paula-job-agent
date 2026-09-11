# Prompts

Ein Prompt pro KI-Aufgabe (T1–T11, siehe `docs/03-llm-tasks.md`). Diese Dateien sind **Entwürfe** mit den fachlichen Anforderungen; die ausführende KI verfeinert sie anhand der Golden-Tests und dokumentiert Änderungen im Git-Log.

Konventionen:
- `{{platzhalter}}` werden von `src/paula/llm/prompts.py` gefüllt.
- Abschnitt `## System` = Systemprompt (statisch, wird gecacht). Abschnitt `## User` = User-Turn (variabel).
- Fremdinhalte (Inserat, Mail, Website) stehen **nur** im User-Turn in `<inserat>`, `<mail>`, `<website>`-Blöcken.
- Output kommt immer über `messages.parse` mit dem Pydantic-Schema aus `llm/schemas.py` – der Prompt beschreibt Felder nur, wo Erklärung nötig ist.
- Sprache der Prompts: Deutsch. Ausgabesprache wird pro Aufgabe gesteuert.
