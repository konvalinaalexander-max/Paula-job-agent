# 04 – Integrationen

Jede externe Anbindung: was sie tut, wie sie eingerichtet wird, welche Fallstricke bekannt sind, was der Fallback ist.

---

## 4.1 Mailbox: Gmail API

**Annahme:** Paulas Konto ist bei Google (offene Frage Q3; sonst → 4.2 IMAP).

### Einrichtung (macht der Betreiber, Anleitung in `docs/06-operations.md` Schritt für Schritt)

1. Google Cloud Console → neues Projekt "paula-job-agent".
2. API "Gmail API" aktivieren.
3. OAuth-Zustimmungsbildschirm: Typ **Extern**, App-Name, Support-Mail. Scopes hinzufügen (unten). Testnutzer: Paulas Adresse.
4. **Wichtig – Gotcha:** Solange die App im Status *Testing* ist, laufen Refresh-Tokens nach **7 Tagen** ab → das System würde wöchentlich sterben. Deshalb: Veröffentlichungsstatus auf **In Production** setzen. Google zeigt dann beim Login einen "nicht verifizierte App"-Warnbildschirm (mit "Erweitert → trotzdem fortfahren"), was für die eigene Nutzung in Ordnung ist. Verifizierung ist **nicht** nötig, solange < 100 Nutzer.
5. Anmeldedaten → OAuth-Client-ID → Typ **Desktop-App** → `credentials.json` herunterladen → nach `data/credentials.json`.
6. `paula auth gmail` ausführen: öffnet Browser-Login (**Paula muss sich hier selbst anmelden und zustimmen** – das ist zugleich ihre technische Einwilligung), speichert `data/token.json`. Auf einem VPS ohne Browser: `run_console()`-Flow bzw. den Link kopieren und Code eingeben – die ausführende KI implementiert den Headless-Flow.

### Scopes (minimal, nicht erweitern)

- `https://www.googleapis.com/auth/gmail.modify` – lesen, Labels setzen, **kein** dauerhaftes Löschen
- `https://www.googleapis.com/auth/gmail.send` – senden

Kein `gmail.readonly` zusätzlich (in `modify` enthalten), kein `https://mail.google.com/` (Vollzugriff).

### Lesen

- **Historischer Scan (M1):** `users.messages.list` mit Query, über `settings.mail.history_months` (Start 24). Query-Vorschlag (wird in `config/settings.yaml` gepflegt, mehrsprachig):
  ```
  newer_than:24m (bewerbung OR application OR candidature OR candidatura OR absage OR "vorstellungsgespräch" OR interview OR "ihre unterlagen" OR "your application" OR "votre candidature" OR stelle OR position OR "job")
  ```
  Beide Richtungen: `in:sent` separat abfragen (für Stilprofil und `application_sent`). Pagination über `nextPageToken`. Danach `sync_state.gmail.initial_scan_done=1` und `gmail.history_id` = aktuelle `historyId` aus `users.getProfile`.
- **Inkrementell (jeder Lauf):** `users.history.list(startHistoryId=…, historyTypes=["messageAdded"])`. Bei HTTP 404 (History zu alt, > ~1 Woche) → Fallback auf `messages.list(q="newer_than:7d")` mit `messages_seen`-Dedup.
- **Format:** `messages.get(format="full")`, MIME-Parsing in `mail/parse.py`: `text/plain` bevorzugen, sonst HTML → Text (BeautifulSoup, Skripte/Styles raus). Zitate entfernen (Zeilen mit `>`, "Am … schrieb …", "On … wrote", "-----Original Message-----"), Signaturen abschneiden (nach `--`, "Mit freundlichen Grüssen" + max 6 Zeilen). Anhänge: nur Dateinamen und MIME-Typen notieren, **nicht** herunterladen (Datenschutz; Ausnahme M2: Paulas eigener CV aus einer gesendeten Mail, falls `data/documents/` leer – nur mit Freigabe des Betreibers).
- **Labels:** Das System setzt ein Label `Paula-Agent/Bewerbung` auf Mails, die es als bewerbungsbezogen einstuft, und `Paula-Agent/Gesendet` auf eigene Sendungen. Paula sieht so in Gmail, was das System kennt. Labels beim ersten Lauf anlegen (`users.labels.create`).

### Senden

- `users.messages.send` mit MIME-Multipart (Text + Anhänge aus `data/documents/`). `From` = Paulas Adresse (automatisch), `Reply-To` nicht setzen.
- **Antworten** (T10): gleiche `threadId`, Header `In-Reply-To` und `References` auf die eingehende Mail setzen, Betreff `Re: …` beibehalten. Sonst landet die Antwort beim Empfänger als neuer Thread.
- Nach dem Senden: `gmail_message_id`, `gmail_thread_id` in `applications` speichern; `messages(direction=out, kind=application_sent)` anlegen.
- Absender-Name: `profile.display_name` ("Paula Muster").

### Rate Limits / Fehler

Gmail-API-Quota ist für diesen Umfang irrelevant (Millionen Einheiten/Tag). Bei 429/5xx: `tenacity`-Retry mit Exponential Backoff, max 5 Versuche. Bei 401 (Token ungültig): Admin-Telegram "Gmail-Login nötig: `paula auth gmail`", Batch-Job beendet sich sauber.

---

## 4.2 Fallback: IMAP/SMTP

Nur wenn Paulas Anbieter nicht Google ist (GMX, Bluewin, Outlook, eigene Domain).

- Lesen: `imaplib` (stdlib) mit `UID SEARCH SINCE …`; Threading über `Message-ID`/`In-Reply-To`/`References` selbst nachbauen (Gmail-Thread-ID gibt es nicht → `gmail_thread_id` speichert dann die Root-`Message-ID`).
- Senden: `smtplib` + STARTTLS.
- Auth: App-Passwort des Anbieters (Outlook.com stellt Basic Auth ein → dort OAuth über MSAL nötig; das wäre ein eigener Adapter, erst bei Bedarf).
- Interface identisch zu `mail/gmail.py` (`MailClient`-Protocol in `mail/base.py`), damit die Pipeline nichts merkt.

---

## 4.3 Telegram-Bot

### Einrichtung

1. In Telegram `@BotFather` → `/newbot` → Name z. B. "Paula Bewerbungshilfe" → Token in `.env` als `TELEGRAM_BOT_TOKEN`.
2. `@BotFather` → `/setcommands` mit der Befehlsliste aus `docs/10-telegram-flows.md`.
3. Paula startet den Bot (`/start`). Der Bot loggt ihre `chat_id`; der Betreiber trägt sie in `.env` als `TELEGRAM_USER_CHAT_ID` ein. Ebenso `TELEGRAM_ADMIN_CHAT_ID` (Alexander). **Bis beide gesetzt sind, antwortet der Bot allen anderen nur mit "Dieser Bot ist privat."**
4. Privacy Mode beim BotFather ist egal (1:1-Chat, kein Gruppenchat).

### Bibliothek und Betrieb

- `python-telegram-bot` ≥ 21, asyncio, **Long Polling** (kein Webhook → kein öffentlicher Port, keine Domain, kein TLS-Zertifikat nötig). Läuft als systemd-Service `paula-bot`.
- Batch-Jobs senden Nachrichten **ohne** den Daemon über `channels/telegram_send.py` (ein `httpx.post` an `https://api.telegram.org/bot<TOKEN>/sendMessage`). Der Daemon sieht diese Nachrichten nicht, muss aber Callbacks darauf verarbeiten → deshalb steht alles Nötige in `approvals` (`telegram_message_id`), nicht im Prozess-Speicher.
- **Nachrichtenlänge:** Telegram-Limit 4096 Zeichen. Entwürfe sind kürzer, aber Karte + Entwurf + Begründung kann drüber gehen → `render.py` splittet: Karte 1 = Kontext + Begründung, Karte 2 = Entwurf + Buttons. Buttons immer an der **letzten** Nachricht.
- **Formatierung:** `parse_mode=HTML` (robuster als Markdown bei Sonderzeichen in Firmennamen). Alle Nutzer-/Fremdtexte HTML-escapen.
- **Callback-Daten:** max. 64 Bytes. Format `a:<approval_id>:<action>` mit action ∈ `ok|rev|no|blk|snz|dt`. Nie den Entwurf selbst in Callback-Daten.
- **Conversation-State:** Wenn Paula "✏️ Ändern" klickt, erwartet der Bot als nächste Textnachricht ihr Feedback. State in `settings_runtime` (`awaiting_feedback_for=<approval_id>`, mit Timeout 30 min), **nicht** im Prozess-Speicher (Neustart-sicher).
- **Sicherheit:** Jeder Handler prüft `update.effective_chat.id ∈ {USER, ADMIN}`. Admin-Befehle (`/kill`, `/resume-system`, `/costs`) nur ADMIN. Callback-Klicks nur USER (Admin darf nicht für Paula freigeben – Ausnahme: `settings.admin_may_approve`, Standard false, für Tests).
- **Idempotenz:** Doppelklick auf ✅ → zweiter Klick findet `status != pending` → "Schon erledigt." Kein zweiter Versand.
- **Nach Entscheidung** wird die Karte editiert (`editMessageReplyMarkup` → Buttons weg, `editMessageText` → Status-Zeile "✅ Gesendet 09:14" / "❌ Verworfen" / "✏️ Überarbeitung läuft…").

---

## 4.4 Jobquellen

### Interface

```python
class RawJob(BaseModel):
    source: str; source_id: str; source_url: str
    title: str; company_name: str; location: str | None
    description: str | None; posted_at: datetime | None
    workload_min: int | None; workload_max: int | None
    employment_type: str | None; salary_min: float | None; salary_max: float | None; salary_currency: str | None
    raw: dict                      # Originalantwort, nur für Debugging, nicht persistieren

class JobSource(Protocol):
    name: str
    def fetch(self, search: SearchProfile, since: datetime | None) -> Iterable[RawJob]: ...
    def enrich(self, job: RawJob) -> RawJob: ...     # Volltext nachladen, falls die Liste nur Snippets liefert
```

Jede Quelle ist in `config/settings.yaml` unter `sources:` aktivierbar, mit eigenen Suchbegriffen und Orten (Portale verstehen unterschiedliche Formulierungen). Reihenfolge der Umsetzung: **Adzuna zuerst** (offiziell, stabil), dann landesabhängig.

### 4.4.1 Adzuna (offizielle API, kostenlos) – **Primärquelle**

- Registrierung auf dem Adzuna-Developer-Portal → `app_id`, `app_key` → `.env`.
- Endpoint-Muster: `https://api.adzuna.com/v1/api/jobs/{country}/search/{page}?app_id=…&app_key=…&what=…&where=…&distance=…&max_days_old=…&results_per_page=50&sort_by=date`. `country` ∈ `ch`, `at`, `de` (alle drei unterstützt). Felder: `title`, `company.display_name`, `location.display_name`, `description` (gekürzt!), `redirect_url`, `created`, `salary_min/max`, `contract_time`.
- **Gotcha:** `description` ist ein Auszug. Für T5 reicht er meist; bei Score ≥ Threshold `enrich()` = `redirect_url` laden und Volltext per JSON-LD (`JobPosting`) oder Haupttext extrahieren. Wenn die Zielseite blockt: mit Auszug weitermachen, Flag `description_truncated`.
- Free-Tier-Limit (Größenordnung: einige hundert bis 1.000 Calls/Monat – **exakte Zahl beim Registrieren prüfen**). Bei 3 Läufen/Tag × 3–5 Suchbegriffe × 1–2 Seiten = ~600/Monat → passt knapp. Deshalb: `max_days_old=2` und nur so viele Seiten wie nötig.
- Firmenname ist oft der Name des Portals/Vermittlers ("Adecco", "Randstad", "Michael Page"). Liste in `config/staffing_agencies.txt`; solche Inserate bekommen `company_id` = die Agentur **und** einen Hinweis in der Karte "Über Personalvermittler". Sperrfrist gilt dann pro Agentur, was falsch wäre → für Agenturen `dedup.company_cooldown_days` ignorieren, nur `same_job` prüfen.

### 4.4.2 job-room.ch (Schweiz, staatlich, RAV) – **zu verifizieren**

- Öffentliche Web-App unter `job-room.ch`; die Angular-Oberfläche lädt Inserate über einen internen JSON-Endpunkt (vermutlich `POST …/jobAdvertisements/_search` mit `page`, `size`, `sort` und einem Suchobjekt). Es gibt eine dokumentierte **Publish-API** für Arbeitgeber (Zugang per Mail an SECO) – die ist für uns irrelevant. Ob der **Such**-Endpunkt ohne Login und stabil nutzbar ist, muss die ausführende KI in M4 prüfen (Browser-DevTools, Network-Tab, dann `httpx` nachbauen, `robots.txt` beachten). Apify-Actors dafür existieren, was zeigt, dass es geht.
- Wert: Inserate mit **Stellenmeldepflicht** sind hier 5 Tage exklusiv, bevor sie anderswo erscheinen. Für gewisse Berufe (je nach Arbeitslosenquote) ist das die beste Quelle der Schweiz.
- Fallback, wenn der Endpunkt nicht sauber nutzbar ist: E-Mail-Abo/Suchagent von job-room.ch auf Paulas Adresse einrichten → die Mails landen in der Inbox → `sources/mailalert.py` parst sie (siehe 4.4.6). Das ist sogar AGB-technisch die sauberste Variante.

### 4.4.3 Bundesagentur für Arbeit (Deutschland) – nur wenn Deutschland relevant

- Inoffiziell dokumentiert (bundesAPI/jobsuche-api). Base `https://rest.arbeitsagentur.de/jobboerse/jobsuche-service/`, Header `X-API-Key: jobboerse-jobsuche`, Suche `/pc/v4/app/jobs?was=…&wo=…&umkreis=…&veroeffentlichtseit=2&size=50&page=1`, Details `/pc/v4/jobdetails/{base64(refnr)}`. Keine dokumentierten Limits; höflich bleiben (≤ 1 Request/s).

### 4.4.4 Österreich (AMS "alle jobs") – nur wenn Österreich relevant

- `jobs.ams.at` hat keine öffentliche Such-API; die AMS HR-API ist für Arbeitgeber. Optionen: (a) Adzuna AT, (b) E-Mail-Suchagent von AMS/karriere.at → `mailalert.py`, (c) interner Endpunkt der Web-App prüfen (wie 4.4.2). Reihenfolge a → b → c.

### 4.4.5 Indeed / LinkedIn / Google Jobs über `python-jobspy` – **nur nach Entscheidung des Auftraggebers**

- Bibliothek scrapt inoffiziell; Indeed unterstützt CH/AT/DE (`country_indeed="switzerland"` etc.), LinkedIn sperrt schnell (Rate-Limit ~10 Seiten/IP), Glassdoor ebenfalls möglich. Bricht regelmäßig, wenn die Portale ihre Seiten ändern.
- **AGB:** Scraping verstößt gegen die Nutzungsbedingungen von LinkedIn und Indeed. Rechtliches Risiko für einen Privatnutzer mit wenigen Abfragen/Tag ist gering, aber real (Konto-Sperre bei LinkedIn, wenn eingeloggt gescrapt wird – JobSpy nutzt für LinkedIn die öffentliche Jobsuche ohne Login). Entscheidung liegt beim Auftraggeber (`docs/08-open-questions.md`, Q8). Wenn ja: nur Indeed + Google, nicht LinkedIn; max. 2 Läufe/Tag; `hours_old=24`.
- Adapter kapselt alles; wenn die Bibliothek bricht, wird die Quelle automatisch deaktiviert (3 Fehlläufe in Folge → `sources.jobspy.enabled=false` in `settings_runtime`, Admin-Info).

### 4.4.6 E-Mail-Suchagenten der Portale → `sources/mailalert.py`

Fast jedes Portal (jobs.ch, jobup.ch, karriere.at, StepStone, Indeed, LinkedIn, job-room.ch) bietet "Jobs per Mail". Diese Mails sind **die legitimste und stabilste Quelle** für Portale ohne API:

- Paula (bzw. der Betreiber mit ihr) richtet auf 2–4 Portalen Suchagenten ein, täglich, an ihre Adresse.
- `scan-inbox` erkennt sie (Absender-Liste in `config/settings.yaml: mail_alerts.senders`), parst Titel/Firma/Ort/Link aus dem HTML (pro Portal ein kleiner Parser mit Fixture-Test), erzeugt `RawJob`s, markiert die Mail `unrelated` für T1 (keine Bewerbungsmail) und labelt sie `Paula-Agent/Jobalert`.
- Volltext: `enrich()` lädt den Link (mit Timeout, `robots.txt`-Respekt, User-Agent gesetzt). Wenn geblockt: nur Titel + Snippet an T5, mit Hinweis.

Das ist der geplante Weg für **jobs.ch / jobup.ch** (Schweiz, keine öffentliche API bekannt) und ein guter Fallback für alles andere.

### 4.4.7 Karriereseiten-Watcher (`sources/careerpage.py`)

Für Firmen, die Paula besonders interessieren (Liste `profile.watch_companies` + alle Firmen mit `status=researched` und `careers_url`): täglich `careers_url` laden, JSON-LD `JobPosting` oder Links mit Job-Mustern extrahieren, Fingerprint, neue → `RawJob`. Viele Firmen nutzen Plattformen (Greenhouse, Lever, Personio, SmartRecruiters, Workday, Prospective/Ostendis in CH) – die ersten vier haben öffentliche JSON-Endpunkte für die Jobliste; Adapter dafür sind klein und lohnen sich (Tabelle in `docs/09-research-notes.md`).

### 4.4.8 Manuell (`sources/manual.py`)

Paula schickt `/add <url>` (oder einfach einen Link). Bot legt `manual_submissions` an; nächster `sweep-portals` lädt die Seite, extrahiert `JobPosting`/Haupttext, T5, normaler Weg. Wenn nichts extrahierbar: Paula bekommt "Konnte die Seite nicht lesen – kannst du mir den Text kopieren?" und kann den Inseratstext als Nachricht schicken.

---

## 4.5 Firmen-Discovery (Spontanbewerbungen)

Ziel: eine **priorisierte** Liste von Firmen in Paulas Region und Zielbranche, nicht "alle Firmen".

### Quellen nach Land

| Land | Quelle | Zugang | Anmerkung |
|---|---|---|---|
| CH | **Zefix PublicREST** (Handelsregister) | kostenloses Konto, Basic Auth, Einzelabfragen nach Name/UID/Ort | Kein Bulk-Export. Suche nach Ort + Rechtsform möglich; Branche (NOGA) nicht immer enthalten |
| CH | **opendata.swiss** – kantonale Handelsregister-Exporte (z. B. Basel-Stadt, Schwyz) | CSV/JSON, offen | Nur einige Kantone; je Kanton anderes Format |
| CH | Branchenverzeichnisse (local.ch, search.ch, Verbände) | Web | Scraping-AGB prüfen; Verbands-Mitgliederlisten sind oft frei |
| AT | WKO Firmen A–Z | Web-Suche | Keine API; Firmenbuch kostenpflichtig |
| DE | OffeneRegister.de (Bulk-Dump des Handelsregisters), handelsregister.de | offen / Web | OffeneRegister ist ein Snapshot, aber für Discovery reichend |
| alle | **Firmen aus Paulas Mailbox** | intern | Firmen, bei denen sie schon war → verwandte Firmen (gleiche Branche, gleicher Ort) |
| alle | **Firmen aus Portal-Inseraten** | intern | Wer inseriert, stellt ein – auch wenn die konkrete Stelle nicht passte |
| alle | **LLM-Vorschlagsliste** (T6-Variante "list companies in <Branche> in <Region>") | Anthropic web_search | Unzuverlässig als einzige Quelle, gut als Ergänzung; jeder Vorschlag wird per T6 verifiziert |
| alle | Manuelle Liste `config/companies_seed.csv` | Betreiber/Paula | Die Firmen, die Paula sowieso im Kopf hat |

### Ablauf

1. `paula import-companies --source zefix --canton ZH --legal-form AG,GmbH` (o. ä.) → `companies(status=discovered)`. Rate-limitiert, über mehrere Nächte.
2. `companies/discovery.py:prioritize()` – regelbasiert, **ohne LLM**: +Branche passt (Keyword-Liste aus `profile.target_industries`), +Ort im Radius, +Größe medium/large (mehr Stellen), +hat Website, −Rechtsform Verein/Stiftung (falls ausgeschlossen), −Holding/Immobilien-Vehikel (Namensmuster). → `priority_score`, `status=prioritized`.
3. `sweep-companies` nimmt pro Nacht Top-N `prioritized` → T6 → `researched` oder `no_contact` → T5b → ggf. Entwurf. Firmen mit `accepts_spontaneous=no` → Score-Abzug 30.
4. Wochenreport an Betreiber: wie viele discovered/prioritized/researched/suggested/no_contact, damit er die Filter nachjustieren kann.

### Was wir bewusst nicht tun

Keine Google-Maps-/Places-Massenabfragen (kostenpflichtig, AGB), kein LinkedIn-Firmen-Scraping, keine gekauften Adresslisten.

---

## 4.6 Versand-Layer (`mail/send.py`) – die letzte Sicherung

Einzige Funktion, die je eine Mail nach außen schickt. Prüft in dieser Reihenfolge, bricht beim ersten Fehler ab (und loggt ihn):

1. `settings_runtime.kill_switch` / `stopped` / `paused` nicht gesetzt
2. `approvals` mit `status=approved` für genau diese `application_id`/`message_id` existiert, entschieden von `TELEGRAM_USER_CHAT_ID`
3. `applications.status == approved` (Status-Maschine)
4. Sendefenster offen (Wochentag + Uhrzeit), sonst → in `approved` belassen, nächster Lauf schickt
5. Tageslimit `limits.sends_per_day` und Wochenlimit `limits.applications_per_week` nicht erreicht
6. Mindestabstand `limits.min_minutes_between_sends` seit letztem Versand eingehalten
7. Empfänger-Adresse syntaktisch gültig, Domain hat MX-Record (DNS-Check), nicht auf `config/blocked_domains.txt`
8. Anhänge existieren und sind ≤ `limits.attachment_mb_total` (Start 8 MB)
9. Faktencheck der gesendeten Version ist `passed` oder nur `minor`
10. `dry_run` → schreibe `.eml` nach `data/outbox/` und **tu so, als wäre gesendet** (Status geht auf `sent`, Event `dry_run=true`), sonst → Gmail/IMAP senden

Dann: Status `sent`, `messages`-Eintrag, `companies.last_contact_at`, Telegram-Karte editieren, Event.

Diese Funktion bekommt den ausführlichsten Test des ganzen Projekts (jede Prüfung einzeln durchfallen lassen).
