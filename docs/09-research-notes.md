# 09 – Recherche-Notizen

Stand: September 2026. Alles mit **[verifizieren]** wurde nur aus Suchergebnissen abgeleitet und muss die ausführende KI vor der Nutzung in der jeweiligen Etappe selbst prüfen (Endpunkt aufrufen, Doku lesen, `robots.txt` lesen).

## Bestehende Projekte – was wir gelernt haben

| Projekt | Was es macht | Was wir übernehmen | Was wir bewusst anders machen |
|---|---|---|---|
| **ApplyPilot** (github.com/Pickle-Pixel/ApplyPilot, AGPL) | 6-stufige Pipeline: Discover → Enrich → Score (1–10) → Tailor → Cover Letter → Auto-Apply über Browser-Automation. Dedup per URL | Die Stufenlogik; Score-Schwellwert vor teuren Schritten; Anreicherung über JSON-LD `JobPosting` | **Kein** Auto-Apply, **kein** CV-Umschreiben, Freigabe-Schritt statt Vollautomatik, Dedup per Firmenidentität statt URL, AGPL-Code nicht übernehmen (Lizenz) |
| **AIHawk / linkedIn_auto_jobs_applier** und Forks | LinkedIn-Easy-Apply-Bot mit GPT-Antworten auf Formularfragen | Nichts direkt; zeigt, was schiefgeht (Konto-Sperren, generische Texte) | Kein LinkedIn, keine Formulare |
| **python-jobspy** (github.com/speedyapply/JobSpy, MIT) | Scraper-Bibliothek für Indeed/LinkedIn/Glassdoor/Google/ZipRecruiter, ein Aufruf → DataFrame; Indeed/Glassdoor unterstützen CH/AT/DE | Optionaler Adapter (Q8). `RawJob`-Felder orientieren sich an deren Spaltenschema | Nur nach Entscheidung; nie LinkedIn; automatische Deaktivierung bei Bruch |
| **Job-apply-AI-agent** (imon333) | n8n + Selenium + OpenAI, Google Sheets als DB | Idee "Tabelle als Wahrheit" → bei uns SQLite | Kein n8n (zusätzliche Plattform ohne Nutzen für einen Nutzer) |
| **anandanair/job-scraper** | Scraping + CV-Parsing + Scoring auf GitHub Actions | Bestätigt: Scoring gegen CV funktioniert | GitHub Actions ungeeignet wegen personenbezogener DB |

Gemeinsamer Befund: Alle öffentlichen Projekte optimieren auf **Menge** (50+ Bewerbungen/Stunde) und haben **keinen Freigabe-Schritt**. Kein einziges liest die Mailbox für Dedup oder Antwort-Tracking. Genau diese Lücken sind unser Kern.

## Jobquellen

| Quelle | Land | Status | Notizen |
|---|---|---|---|
| **Adzuna API** | CH, AT, DE (+16) | Offiziell, kostenlos, App-ID/Key | Free-Tier-Limit in Größenordnung "einige hundert bis 1.000 Calls/Monat" **[verifizieren beim Registrieren]**. Endpoint `api.adzuna.com/v1/api/jobs/{cc}/search/{page}`. Beschreibung gekürzt |
| **Bundesagentur für Arbeit Jobsuche** | DE | Inoffiziell dokumentiert (bundesAPI/jobsuche-api) | `rest.arbeitsagentur.de/jobboerse/jobsuche-service/pc/v4/app/jobs`, Header `X-API-Key: jobboerse-jobsuche`, Details `/pc/v4/jobdetails/{base64(refnr)}`. Keine Limits dokumentiert |
| **job-room.ch** | CH | Web-App mit internem JSON-Endpunkt **[verifizieren]**; offizielle API nur zum *Publizieren* (SECO, Zugang per Mail) | Stellenmeldepflicht-Inserate 5 Tage exklusiv. Apify-Scraper existieren → Endpunkt ist nutzbar. E-Mail-Suchagent als saubere Alternative |
| **jobs.ch / jobup.ch** | CH | Keine öffentliche API gefunden | E-Mail-Suchagent (4.4.6). Möglicherweise über Adzuna aggregiert **[verifizieren]** |
| **AMS alle jobs** | AT | Keine öffentliche Such-API; HR-API nur Arbeitgeber | E-Mail-Suchagent oder interner Endpunkt **[verifizieren]** |
| **karriere.at, StepStone** | AT/DE | Keine öffentliche API | E-Mail-Suchagenten |
| **Indeed** | alle | RSS eingestellt; keine API für Suchende | Nur via JobSpy (Q8) oder E-Mail-Alert |
| **LinkedIn** | alle | Keine API; aktive Anti-Scraping-Maßnahmen | Nur /add oder E-Mail-Alert |
| **Google Jobs** | alle | Keine API | Nur via JobSpy (Q8) |
| **Karriereseiten-Plattformen** | alle | Greenhouse (`boards-api.greenhouse.io/v1/boards/{slug}/jobs`), Lever (`api.lever.co/v0/postings/{slug}`), Personio (`{slug}.jobs.personio.de/search.json` o. ä.), SmartRecruiters (`api.smartrecruiters.com/v1/companies/{slug}/postings`) – alle öffentlich, kein Key **[Pfade verifizieren]** | Erkennung über Link-Muster auf der Karriereseite. In CH häufig auch Prospective/Ostendis/Umantis – haben meist RSS oder JSON-LD |

## Firmen-Discovery

| Quelle | Land | Status |
|---|---|---|
| **Zefix PublicREST** (`zefix.admin.ch/ZefixPublicREST/`) | CH | Kostenloses Konto, Basic Auth, Einzelabfragen (Name/UID/Ort). Kein Bulk. Swagger-Doku vorhanden **[verifizieren: Suchparameter für Ort + Rechtsform, Rate-Limit]** |
| **opendata.swiss** Handelsregister-Datensätze | CH (einige Kantone: BS, SZ, …) | Offene CSV/JSON; je Kanton anderes Schema |
| **OffeneRegister.de** | DE | Bulk-Dump, Snapshot |
| **WKO Firmen A–Z** | AT | Web-Suche, keine API |

## Mail

- Google phast App-Passwörter aus; OAuth 2.0 ist der Weg. Gmail API mit Desktop-OAuth-Client funktioniert headless über Copy-Paste-Flow. **Gotcha:** OAuth-App im Status "Testing" → Refresh-Token läuft nach 7 Tagen ab → "In Production" setzen (keine Verifizierung nötig unter 100 Nutzern, Warnbildschirm akzeptieren).
- Microsoft stellt Basic Auth für IMAP/POP ein (Outlook.com) → dort wäre MSAL/OAuth nötig. Nur relevant bei Q3 = Outlook.

## Telegram

- Bot-API kostenlos, Long Polling ohne öffentlichen Port, Inline-Keyboards mit Callback-Daten (max. 64 Bytes), Nachrichten max. 4096 Zeichen, `editMessageText`/`editMessageReplyMarkup` für Statusupdates. `python-telegram-bot` v21+ async.
- WhatsApp Business API: kostenpflichtig, Meta-Business-Verifizierung, Templates für selbst-initiierte Nachrichten → ungeeignet. Signal: keine offizielle API.

## Anthropic API (aus der aktuellen SDK-Dokumentation, Stand Juni 2026)

- Modelle: `claude-opus-5` ($5/$25 pro 1M In/Out), `claude-haiku-4-5` ($1/$5), `claude-sonnet-5` ($2/$10). Exakte IDs ohne Datumssuffix.
- Thinking: `thinking={"type":"adaptive"}`; `output_config={"effort": "low|medium|high"}`. Kein `budget_tokens`.
- Strukturierte Ausgaben: `client.messages.parse(..., output_format=PydanticModel)`.
- Server-Tools: `web_search_20260209`, `web_fetch_20260209` mit `max_uses`, `allowed_domains`. Ein Call, Schleife serverseitig.
- Batches API für den historischen Scan (50 % Rabatt, asynchron).
- Prompt-Caching: `cache_control` auf stabilen Blöcken; Reihenfolge tools → system → messages; Cache-Treffer über `usage.cache_read_input_tokens` prüfen.
- Server-side-Fallbacks (`fallbacks`) und `stop_reason == "refusal"` behandeln.
- PDF als `document`-Block (base64), für T4.

## Verworfen

- **Managed Agents / Agent-Frameworks:** Für einen agentischen Schritt (T6) mit Server-Tools nicht nötig; würde Deployment und Kostenmodell verkomplizieren.
- **Vektor-Datenbank für Stil/Fakten:** Zwei Markdown-Dateien im gecachten Systemprompt sind billiger, lesbarer und korrigierbar.
- **GitHub Actions als Runtime:** Kein persistenter Zustand; personenbezogene DB müsste ins Repo.
- **Transaktionsmail-Dienste (SendGrid, Mailgun):** Falsche Absender-Infrastruktur für Bewerbungen, Tracking, Reputationsrisiko.
- **Google-Places-Massenabfragen für Firmen:** Kosten + AGB.
- **PDF-Anschreiben generieren (V1):** Aufwand ohne Nutzen, Mailtext ist das Anschreiben.

## Abweichungen (von der ausführenden KI zu pflegen)

*(Datum – Was im Plan stand – Was tatsächlich gilt – Was stattdessen gemacht wurde)*
