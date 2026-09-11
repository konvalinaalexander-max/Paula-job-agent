# 01 – Architektur

## Überblick

```
                 ┌──────────────────────────────────────────────────────────┐
                 │                        VPS (Linux)                        │
                 │                                                          │
  systemd timer ─┼─▶ paula scan-inbox      ──┐                              │
  (3x täglich)   │   paula sweep-portals   ──┤                              │
                 │   paula process-replies ──┤    ┌────────────────┐        │
  systemd timer ─┼─▶ paula sweep-companies ──┼───▶│  SQLite (WAL)  │◀──┐    │
  (1x nachts)    │                           │    │  data/paula.db │   │    │
                 │   paula backup          ──┘    └────────────────┘   │    │
                 │                                        ▲            │    │
  systemd service┼─▶ paula bot  (Telegram, dauerhaft) ────┘            │    │
                 │                                                     │    │
                 │   paula <cli>  (Betreiber, manuell) ────────────────┘    │
                 └──────────────────────────────────────────────────────────┘
                          │            │             │              │
                          ▼            ▼             ▼              ▼
                     Gmail API    Telegram API   Anthropic API   Jobquellen
                                                                 (Adzuna, …)
```

Drei Arten von Prozessen teilen sich eine SQLite-Datenbank:

1. **Batch-Jobs** (`scan-inbox`, `sweep-portals`, `sweep-companies`, `process-replies`, `backup`) – kurz laufend, von systemd-Timern gestartet, idempotent.
2. **Bot-Daemon** (`paula bot`) – läuft dauerhaft, empfängt Telegram-Eingaben (Button-Klicks, Befehle, Freitext), schreibt Entscheidungen in die DB, löst Versand aus.
3. **CLI** – für den Betreiber: Einrichtung, Diagnose, Reports, manuelle Eingriffe.

Die DB ist die einzige Kopplung zwischen den Prozessen. Batch-Jobs erzeugen Freigabe-Anfragen (`approvals`) und schicken die Telegram-Nachricht direkt über die Bot-API (ein HTTP-POST); der Daemon verarbeitet nur die *Antworten* darauf. So gibt es keine Queue, keinen Message-Broker, keine zweite Datenbank.

## Datenfluss – Hauptpfad (Portal-Bewerbung)

```
sweep-portals
  1. für jede aktive Quelle: Adapter.fetch(profile.search) → List[RawJob]
  2. RawJob → normalisieren → Fingerprint → INSERT OR IGNORE jobs
  3. neue jobs → Regel-Vorfilter (Ort, Pensum, Ausschlusswörter, Firma gesperrt?, Firma in Sperrfrist?)
  4. Überlebende → LLM T5 Scoring (Score 0–100 + Begründung + Bedenken)
  5. Score ≥ threshold → LLM T6 Firmenrecherche (falls Firma unbekannt) → LLM T7 Entwurf → LLM T8 Faktencheck
  6. Faktencheck bestanden → applications(status=pending_approval) + approvals(kind=application_draft)
  7. Telegram: Nachricht mit Entwurf + Buttons an Paula
  8. Tageslimit für Vorschläge erreicht → Rest bleibt status=scored, kommt beim nächsten Lauf dran (nach Score sortiert)

bot (Callback)
  9a. ✅ Senden   → approvals.decision=approved → send_application() → status=sent, messages-Eintrag, Gmail-Thread-ID gespeichert
  9b. ✏️ Ändern   → Bot fragt nach Freitext → LLM T11 Revision → T8 Faktencheck → neue Nachricht mit neuem Entwurf (max. 3 Runden, dann Hinweis "bitte selbst anpassen und als Text schicken")
  9c. ❌ Verwerfen → status=rejected_by_user, Firma bekommt reject_count+1; ab 2 → Nachfrage "Firma dauerhaft sperren?"

process-replies (3x täglich)
  10. Gmail: neue Mails seit last_history_id, gefiltert auf Threads bekannter Bewerbungen ODER Absender-Domains bekannter Firmen ODER Bewerbungs-Keywords
  11. LLM T9 Klassifikation → messages.kind ∈ {ack, rejection, interview, question, offer, other}
  12. Status-Update applications; bei rejection/interview/question/offer → LLM T10 Antwortentwurf → approvals(kind=reply_draft) → Telegram
  13. Einladungen: sofort Telegram, unabhängig vom Tageslimit
```

## Datenfluss – Spontanbewerbung

```
sweep-companies (nachts, 1x)
  1. Discovery-Quellen (Zefix/Handelsregister-Export, Branchenverzeichnis, manuelle Liste, Firmen aus alten Bewerbungen) → companies (status=discovered)
  2. Regel-Vorfilter: Region, Rechtsform, Branche (NOGA/ÖNACE-Code), Größe falls bekannt, gesperrt?
  3. Priorisierung ohne LLM: Score aus Branche-Match, Nähe, Größe → Top-N pro Nacht (settings.companies_research_per_night, Start 10)
  4. Top-N → LLM T6 Firmenrecherche (Agent mit web_search/web_fetch): Was macht die Firma, Karriereseite, Kontaktadresse für Initiativbewerbungen, offene Stellen, Ton der Website
  5. Recherche-Ergebnis → LLM T5b Spontan-Scoring (passt Paula zu dieser Firma? gibt es einen konkreten Anknüpfungspunkt?)
  6. Score ≥ threshold_spontaneous → T7 Entwurf (Variante "spontan") → T8 → approvals → Telegram
  7. Keine Kontaktadresse gefunden → companies.status=no_contact, Paula sieht es nicht, Betreiber im Wochenreport
```

Wichtig: Der Firmen-Sweep ist **gedrosselt**, nicht "non-stop bis das Land durch ist". Die Firmenliste darf tausende Einträge haben; recherchiert und vorgeschlagen wird pro Nacht eine Handvoll. Das ist Absicht (siehe `docs/00-vision.md`, Nicht-Ziele).

## Modulstruktur

```
src/paula/
├── __init__.py
├── cli.py                  Typer-App: alle Befehle (scan-inbox, sweep-portals, bot, doctor, report, …)
├── config.py               Laden/Validieren von settings.yaml, profile.yaml, .env → Pydantic Settings
├── db.py                   Verbindung (WAL), Migrationen, kleine Repository-Funktionen
├── models.py               Pydantic-Modelle für DB-Zeilen und Domänenobjekte
├── state.py                Status-Maschine für applications (erlaubte Übergänge, zentral erzwungen)
├── dedup.py                Normalisierung, Fingerprints, Sperrfrist-Prüfung
├── limits.py               Tages-/Wochenlimits, Sendefenster, Kill-Switch
├── events.py               Event-Log (jede Aktion → events-Tabelle)
├── mail/
│   ├── gmail.py            Gmail-API-Client: OAuth, list/get/send, Labels, History
│   ├── imap.py             Fallback: IMAP lesen / SMTP senden (nur falls kein Google)
│   ├── parse.py            MIME → Text, Zitate/Signaturen entfernen, Thread-Zuordnung
│   └── send.py             Versand-Layer: prüft limits + approval, dann gmail/imap, dry_run → outbox
├── channels/
│   ├── telegram_bot.py     Daemon: Handler für Befehle, Callbacks, Freitext; Conversation-States
│   ├── telegram_send.py    Einfache Sende-Funktionen (für Batch-Jobs, ohne Daemon)
│   └── render.py           Nachrichtentexte bauen (Entwurf-Karte, Status, Report)
├── sources/
│   ├── base.py             JobSource-Interface, RawJob-Modell
│   ├── adzuna.py           Offizielle API (CH/AT/DE)
│   ├── arbeitsagentur.py   Bundesagentur für Arbeit (DE, inoffiziell dokumentiert)
│   ├── jobroom.py          job-room.ch (CH) – zu verifizieren
│   ├── jobspy_source.py    Wrapper um python-jobspy (Indeed/Google) – optional, AGB-Frage
│   ├── careerpage.py       Watcher für Karriereseiten einzelner Firmen (Sitemap/JSON-LD)
│   └── manual.py           Von Paula per /add <url> eingereichte Stellen
├── companies/
│   ├── discovery.py        Firmenlisten-Import (CSV/Zefix/opendata), Priorisierung
│   └── research.py         Aufruf LLM T6, Ergebnis in companies schreiben
├── llm/
│   ├── client.py           Anthropic-Client, Caching-Header, Fallbacks, Retry, Kostenzähler
│   ├── schemas.py          Pydantic-Output-Schemas aller Aufgaben
│   ├── prompts.py          Lädt prompts/*.md, füllt Platzhalter
│   ├── tasks.py            Eine Funktion pro Aufgabe T1…T11
│   └── factcheck.py        T8 + regelbasierte Checks (Zahlen, Firmennamen, Jahreszahlen)
├── pipeline/
│   ├── inbox.py            scan-inbox (historisch + inkrementell)
│   ├── portals.py          sweep-portals
│   ├── companies.py        sweep-companies
│   ├── replies.py          process-replies
│   └── drafts.py           Entwurf erzeugen → Faktencheck → Approval anlegen → Telegram
└── report.py               Wochenreport, /status, /report
```

## Laufzeit-Verhalten

- **Nebenläufigkeit:** SQLite im WAL-Modus, `busy_timeout=5000`. Batch-Jobs und Bot schreiben beide; Konflikte werden durch kurze Transaktionen vermieden. systemd-Timer sind so gesetzt, dass Batch-Jobs sich nicht überlappen (`scan-inbox` → `sweep-portals` → `process-replies` nacheinander in einem Wrapper `paula run-cycle`).
- **Fehler:** Jeder Batch-Job fängt Exceptions pro Element (pro Mail, pro Job), loggt sie mit Kontext, schreibt ein `events(kind=error)`, macht weiter. Am Ende: wenn > 20 % der Elemente fehlgeschlagen sind → Telegram an Admin-Chat.
- **Wiederanlauf:** Jeder Job merkt sich Fortschritt in `sync_state` (z. B. Gmail `historyId`, Adzuna `last_run_at`), so dass Abbruch und Neustart keine Duplikate erzeugen.
- **Zeitzone:** Alles in UTC in der DB, Anzeige in `settings.timezone` (Europe/Zurich o. ä.).
- **Sendefenster:** Versand nur Mo–Fr, `limits.send_window` (Start 08:00–18:00 Ortszeit). Freigaben außerhalb werden gespeichert und im nächsten Fenster versendet (Paula wird informiert: "wird morgen um 8 Uhr gesendet").

## Architekturentscheidungen (ADR-Kurzform)

| # | Entscheidung | Alternativen | Warum so |
|---|---|---|---|
| A1 | SQLite statt Postgres | Postgres, Supabase | Ein Nutzer, ein Server, < 1 GB. Kein Betrieb einer DB nötig. Backup = Dateikopie |
| A2 | Anthropic SDK direkt, kein Agent-Framework | LangChain, CrewAI, LangGraph | Nur eine Stelle (T6) ist agentisch, und da reichen die Server-Tools (web_search/web_fetch) in einem einzigen API-Call. Frameworks verstecken Kosten und Fehler |
| A3 | Telegram statt WhatsApp/Signal/E-Mail | WhatsApp Business API, Signal, E-Mail-Freigabe | Kostenlos, 10 Minuten Setup, Inline-Buttons. WhatsApp braucht Business-Verifizierung + Template-Freigaben; Signal hat keine offizielle API. E-Mail-Freigabe ist Fallback (siehe offene Fragen) |
| A4 | Gmail API mit OAuth statt IMAP + App-Passwort | IMAP/SMTP | Google phasen App-Passwörter aus; Gmail API liefert Thread-IDs, History-API (inkrementell), Labels. IMAP bleibt Fallback für Nicht-Google |
| A5 | Batch-Jobs schicken Telegram-Nachrichten selbst | Alles über den Daemon, Queue-Tabelle | Weniger bewegliche Teile. Ein HTTP-POST an die Bot-API ist trivial. Der Daemon braucht nur Callback-Handling |
| A6 | Regel-Vorfilter vor jedem LLM-Call | Alles ans Modell | Kosten und Rauschen. 90 % der Inserate fallen durch Ort/Pensum/Keywords raus, ohne Token zu kosten |
| A7 | Faktentreue durch getrennten Prüf-Call (T8) plus Regeln | Nur Prompt-Anweisung | Ein Modell prüft den Output eines anderen Calls zuverlässiger als sich selbst. Regeln fangen Zahlen/Jahre/Firmennamen deterministisch |
| A8 | Stilprofil + Faktenblock als Markdown-Dateien, menschlich kuratiert | Vektor-DB, Few-Shot aus Live-Mails bei jedem Call | Lesbar, versionierbar, korrigierbar. Werden per Prompt-Caching mitgeschickt, kosten nach dem ersten Call fast nichts |
| A9 | Status-Maschine zentral in `state.py` | Status frei setzen | Verhindert unmögliche Übergänge (z. B. sent ohne approved) durch Code, nicht Disziplin |
| A10 | Keine Web-UI | Streamlit, Flask-Dashboard | Paula braucht keine, der Betreiber hat CLI + `/report`. Später nachrüstbar |
| A11 | systemd statt Docker | Docker Compose, Cron | Ein Prozess, ein VPS, ein Nutzer. systemd-Timer + Journal-Logs sind ausreichend und für den Betreiber leichter zu verstehen. Docker als spätere Option |
| A12 | Anschreiben als Mailtext + CV-PDF als Anhang, kein generiertes PDF-Anschreiben | PDF-Anschreiben generieren | Mail-Text ist das, was gelesen wird. PDF-Generierung ist Aufwand ohne Nutzen in Etappe 1. Optional in M9 |

## Abhängigkeiten (initial)

`anthropic`, `pydantic`, `pydantic-settings`, `pyyaml`, `httpx`, `typer`, `structlog`, `python-telegram-bot`, `google-api-python-client`, `google-auth-oauthlib`, `google-auth-httplib2`, `beautifulsoup4`, `lxml`, `rapidfuzz` (Firmennamen-Fuzzy-Match), `python-dateutil`, `tenacity` (Retries). Dev: `pytest`, `pytest-asyncio`, `ruff`, `respx` (httpx-Mocks), `freezegun`.

Optional, nur nach Entscheidung des Auftraggebers: `python-jobspy`.

## Entscheidungen während der Umsetzung

*(Die ausführende KI trägt hier Entscheidungen ein, die der Plan offen ließ. Format: Datum – Entscheidung – Begründung.)*
