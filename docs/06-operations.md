# 06 – Betrieb

## 6.1 Zielumgebung

- **VPS:** Hetzner CX22 (2 vCPU, 4 GB, ~4–5 €/Monat) oder vergleichbar, Ubuntu 24.04 LTS, Standort EU. Alternativen: Raspberry Pi 4 daheim (gleiche Anleitung, nur ohne Cloud-Firewall); **nicht** GitHub Actions (kein persistenter Zustand, personenbezogene DB müsste ins Repo).
- Ein Systemnutzer `paula` ohne Login-Shell für den Dienst; der Betreiber arbeitet über SSH mit seinem eigenen Nutzer + `sudo`.
- Python 3.12 + `uv`. Kein Docker in V1 (A11).

## 6.2 Einrichtung (Runbook für den Betreiber; die ausführende KI schreibt es in M0 als `deploy/SETUP.md` Schritt für Schritt aus, inklusive der genauen Befehle)

1. VPS bestellen, SSH-Key hinterlegen, Firewall: nur 22/tcp (Telegram Long-Polling und alle APIs sind ausgehend).
2. `apt update && apt upgrade`, `unattended-upgrades` aktivieren, `fail2ban`.
3. Nutzer `paula` anlegen, Repo nach `/opt/paula` klonen, `uv sync`.
4. `.env` aus `.env.example` befüllen (siehe 5.8). `data/` anlegen, Rechte 700.
5. `uv run paula doctor` → prüft Python, Rechte, `.env`-Vollständigkeit, Anthropic-Key (Testcall mit 5 Tokens), Telegram-Token (`getMe`), Adzuna (1 Suche), Gmail-Token vorhanden.
6. `uv run paula auth gmail` (mit Paula zusammen, siehe 4.1).
7. `uv run paula db migrate`.
8. `deploy/install-systemd.sh` → kopiert Units, `systemctl enable --now paula-bot paula-cycle.timer paula-companies.timer paula-backup.timer paula-weekly.timer`.
9. Erster Lauf manuell: `uv run paula scan-inbox --initial` (dauert je nach Mailbox 10–60 Min., Batch-API asynchron).
10. `dry_run` bleibt `true` bis M5 abgenommen.

## 6.3 Zeitplan (systemd-Timer, Ortszeit `settings.timezone`)

| Timer | Zeit | Führt aus |
|---|---|---|
| `paula-cycle.timer` | 07:30, 12:30, 17:00 Mo–Sa | `paula run-cycle` = scan-inbox → process-replies → sweep-portals → send-approved → reminders |
| `paula-companies.timer` | 02:00 täglich | `paula sweep-companies` |
| `paula-backup.timer` | 03:30 täglich | `paula backup` |
| `paula-weekly.timer` | So 18:00 | `paula report --weekly --send` |
| `paula-bot.service` | dauerhaft | `paula bot`, `Restart=always`, `RestartSec=10` |

`send-approved` verschickt Freigaben, die außerhalb des Sendefensters kamen. Warum 3 feste Zeiten und nicht stündlich: Paula bekommt Vorschläge gebündelt statt tröpfchenweise; Adzuna-Limit; Kosten.

`run-cycle` nimmt ein Lock (`data/cycle.lock`, `flock`), damit sich Läufe nie überlappen. Ein Lauf, der > 45 Min. dauert, wird abgebrochen und gemeldet.

## 6.4 Logging und Monitoring

- `structlog` → JSON auf stdout → systemd-Journal (`journalctl -u paula-bot -f`). Retention: Journal auf 500 MB begrenzen.
- Jeder Batch-Lauf schreibt am Ende eine Zusammenfassungszeile + `events(kind=run_summary, payload={fetched, new, scored, proposed, errors, duration, cost_usd})`.
- **Admin-Benachrichtigungen (Telegram, Admin-Chat):**
  - Batch-Job abgestürzt oder > 20 % Elementfehler
  - Gmail 401 / Telegram 401
  - Tages-LLM-Budget zu 80 % erreicht / überschritten
  - Quelle automatisch deaktiviert (3 Fehlläufe)
  - Faktencheck 2× fehlgeschlagen (Entwurf verworfen)
  - Paula hat /stop gedrückt
  - Kein `run-cycle` seit > 12 h (Watchdog-Timer, separat)
- Kein externes Monitoring in V1. Optional: Healthchecks.io-Ping am Ende jedes `run-cycle` (kostenlos, meldet Ausbleiben).

## 6.5 Backups

- Täglich `paula backup` (SQLite-Online-Backup), 14 Tage lokal.
- Wöchentlich verschlüsseltes Off-Site-Backup (Q12: wohin – Hetzner Storage Box, Betreiber-NAS, …), `age`-verschlüsselt mit Betreiber-Key. Enthält `data/paula.db`, `data/facts.md`, `data/style_profile.md`, `config/`. **Nicht** `token.json` (bei Restore neu einloggen – sicherer).
- Restore-Test in M8 einmal durchführen und dokumentieren.

## 6.6 Updates und Deploy

- `deploy/deploy.sh`: `git pull` → `uv sync` → `paula db migrate` → `systemctl restart paula-bot`. Timer-Jobs nehmen die neue Version beim nächsten Start.
- Vor Deploy: `uv run pytest` lokal grün. Kein Deploy während `run-cycle` läuft (Lock prüfen).
- Rollback: `git checkout <vorheriger-tag>` + Deploy; Migrationen sind vorwärts-only, daher vor riskanten Migrationen Backup.

## 6.7 Kostenkontrolle

- `llm_calls` summiert; `paula report --costs` zeigt pro Tag/Aufgabe/Modell.
- `limits.llm_budget_usd_per_day` hart; bei Erreichen: T6 (teuerste) zuerst aussetzen, dann T5, nie T9/T10 (Antworten auf Firmen haben Vorrang).
- Prompt-Caching prüfen: `cache_read_input_tokens` in `llm_calls` muss bei T5/T7/T8 nach dem ersten Call > 0 sein, sonst ist der Systemprompt nicht stabil (Bug). `paula doctor --cache` testet das.
- Erwartung: 20–45 $/Monat LLM + 5 € VPS. Über 60 $/Monat → etwas stimmt nicht (Admin-Warnung bei 2 $/Tag über 3 Tage).

## 6.8 Betriebs-CLI (Übersicht)

```
paula doctor [--cache]            Umgebung prüfen
paula auth gmail                  OAuth-Login
paula consent --confirmed-by … --date …
paula db migrate | backup | purge [--all | --messages-older-than 12m]
paula scan-inbox [--initial] [--since 2025-01-01] [--dry-run]
paula sweep-portals [--source adzuna] [--limit 20]
paula sweep-companies [--limit 5]
paula process-replies
paula send-approved
paula run-cycle
paula import-companies --source zefix|csv|opendata … 
paula style build                 T3 → data/style_profile.draft.md
paula facts build --cv data/documents/CV.pdf   T4 → data/facts.draft.md
paula report [--weekly] [--costs] [--send]
paula export --for-user
paula bot
paula kill | unkill | pause | resume
paula debug application <id> | company <id> | message <id>
paula replay <application_id>     Entwurf mit aktuellen Prompts neu erzeugen (ohne Versand), für Prompt-Tuning
```
