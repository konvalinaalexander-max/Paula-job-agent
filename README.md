# Paula Job Agent

Ein halbautomatisches Bewerbungssystem für eine einzelne Person ("Paula"), das

1. ihre Mailbox liest und die bisherige Bewerbungshistorie rekonstruiert (keine Doppelbewerbungen),
2. ihren Schreibstil und ihre Fakten (Lebenslauf) lernt,
3. mehrmals täglich Jobportale und – gezielt – Firmen für Spontanbewerbungen durchsucht,
4. passende Stellen bewertet, Bewerbungsmails in ihrem Stil entwirft,
5. **jeden Entwurf per Telegram zur Freigabe vorlegt** (Senden / Ändern / Verwerfen),
6. nach Freigabe versendet, Antworten liest, einordnet (Absage / Einladung / Rückfrage) und Reaktionen vorschlägt.

**Kernprinzip: Nichts verlässt das System ohne Paulas Klick.** Das ist keine Komfortfunktion, sondern die Grundlage dafür, dass das Ganze rechtlich, ethisch und für ihre Mail-Reputation sauber ist.

## Status

**Planungsphase.** Dieses Repository enthält den vollständigen Projektplan, die Datenmodelle, Prompt-Spezifikationen und ein Code-Gerüst. Es ist so geschrieben, dass eine ausführende KI (z. B. Claude Code) das Projekt Etappe für Etappe umsetzen kann. Es gibt noch keinen lauffähigen Code.

## Für die ausführende KI

**Lies zuerst [`CLAUDE.md`](CLAUDE.md).** Dort stehen Arbeitsweise, harte Regeln und die Reihenfolge.

## Dokumentation

| Datei | Inhalt |
|---|---|
| [`docs/00-vision.md`](docs/00-vision.md) | Ziel, Nicht-Ziele, Prinzipien, Rollen, Erfolgskriterien |
| [`docs/01-architecture.md`](docs/01-architecture.md) | Komponenten, Datenfluss, Laufzeitmodell, Modulstruktur, Architekturentscheidungen |
| [`docs/02-data-model.md`](docs/02-data-model.md) | Datenbankschema, Status-Maschine, Dedup-Regeln |
| [`docs/03-llm-tasks.md`](docs/03-llm-tasks.md) | Jede KI-Aufgabe einzeln: Input, Output-Schema, Modell, Guardrails, Tests |
| [`docs/04-integrations.md`](docs/04-integrations.md) | Gmail, Telegram, Jobquellen, Firmen-Discovery, Versand – konkret |
| [`docs/05-safety-legal.md`](docs/05-safety-legal.md) | Guardrails, Einwilligung, Datenschutz, Faktentreue, Kill-Switch |
| [`docs/06-operations.md`](docs/06-operations.md) | Deployment, Cron, Logging, Backups, Secrets, Kostenkontrolle |
| [`docs/07-milestones.md`](docs/07-milestones.md) | Etappen M0–M9 mit Aufgaben, Tests und Definition of Done |
| [`docs/08-open-questions.md`](docs/08-open-questions.md) | Offene Fragen an den Auftraggeber, mit Default-Annahmen |
| [`docs/09-research-notes.md`](docs/09-research-notes.md) | Recherche: bestehende Projekte, APIs, was verworfen wurde |
| [`docs/10-telegram-flows.md`](docs/10-telegram-flows.md) | Der komplette Dialog mit Paula: Befehle, Nachrichten, Buttons |
| [`docs/11-testing.md`](docs/11-testing.md) | Teststrategie: Fixtures, Golden-Tests, Dry-Run, Staging |

## Struktur

```
.
├── CLAUDE.md               Anweisungen für die ausführende KI
├── docs/                   Der Plan (siehe Tabelle)
├── config/                 Beispiel-Konfiguration (Profil, Settings)
├── prompts/                Prompt-Templates als Dateien (Entwürfe, zu verfeinern)
├── db/                     schema.sql + Migrationen
├── src/paula/              Python-Package (Gerüst mit Docstrings, noch ohne Logik)
├── tests/                  Tests + Fixtures
├── deploy/                 systemd-Units, Deploy-Skript
├── data/                   Laufzeitdaten (DB, Dokumente, Profile) — nicht in Git
└── .env.example            Welche Secrets gebraucht werden
```

## Rollen

- **Auftraggeber / Betreiber:** Alexander – richtet ein, betreibt, hat Admin-Zugang.
- **Nutzerin:** Paula – sucht den Job, gibt frei, kommuniziert nur über Telegram.
- **Ausführende KI:** setzt den Plan um, fragt bei Unklarheit den Auftraggeber.
