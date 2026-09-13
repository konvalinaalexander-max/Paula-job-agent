# 01 – Architektur

> **Version 2** (13.09.2026). Grundlegend neu: kein eigener Server, keine eigene API-Integration, kein Telegram. Die Intelligenz läuft in Claude-Sessions, die Daten liegen in der Dashboard-Datenbank, die Oberfläche ist das Dashboard selbst.

## Die Kernentscheidung

Der Auftraggeber will (a) dass die KI-Arbeit über sein Claude läuft und nicht über eine separat bezahlte Schnittstelle, (b) dass er nicht jedes Mal "mach jetzt" tippen muss, und (c) dass Paula eine Website bekommt. Diese drei Wünsche passen genau zu einer Bauform, die ohne eigenen Server auskommt:

```
   ┌──────────────────────────────────────────────────────────────┐
   │  ROUTINE (geplanter Trigger, 3× täglich)                     │
   │  startet automatisch eine Claude-Session in der Cloud        │
   └───────────────────────────┬──────────────────────────────────┘
                               ▼
   ┌──────────────────────────────────────────────────────────────┐
   │  CLAUDE-SESSION  (Container, lebt nur für diesen Lauf)       │
   │                                                              │
   │   1. Repo auschecken → Skripte + Arbeitsanweisung            │
   │   2. Helfer-Skripte ausführen (deterministisch):             │
   │        gmail_fetch.py   Mails holen                          │
   │        jobs_fetch.py    Inserate holen                       │
   │        db_io.py         Datenbank lesen/schreiben            │
   │   3. Claude selbst denkt (kein API-Call, keine Extrakosten): │
   │        Mails verstehen · Stellen bewerten · Texte schreiben  │
   │   4. Ergebnisse in die Dashboard-Datenbank schreiben         │
   └───────────────────────────┬──────────────────────────────────┘
                               ▼
   ┌──────────────────────────────────────────────────────────────┐
   │  DASHBOARD-DATENBANK  (dauerhaft, überlebt jede Session)     │
   │  Firmen · Stellen · Bewerbungen · Nachrichten · Profil       │
   └───────────────────────────┬──────────────────────────────────┘
                               ▼
   ┌──────────────────────────────────────────────────────────────┐
   │  DASHBOARD  (Website, die Paula öffnet)                      │
   │  4 Blöcke · Text kopieren · CV herunterladen · abhaken       │
   └──────────────────────────────────────────────────────────────┘
```

Was daran gut ist: kein Server, den jemand warten muss. Keine zweite Rechnung. Die teuerste und heikelste Arbeit – Sprache verstehen und formulieren – macht Claude direkt in der Session, mit vollem Kontext und ohne dass ein Prompt durch drei Schichten muss.

Was daran unbequem ist: Der Container ist nach jedem Lauf weg. Alles, was zwischen zwei Läufen erhalten bleiben muss, gehört in die Dashboard-Datenbank – es gibt keine lokale Datei, die überlebt. Das ist eine Disziplin, kein Hindernis.

## Die drei Bausteine im Detail

### 1. Die Dashboard-Datenbank

Die Website ist eine veröffentlichte Seite auf claude.ai mit einer eigenen, dauerhaften Datenbank. Diese Datenbank ist von **beiden Seiten** erreichbar:

- **von der Website aus** – Paula klickt, die Seite liest und schreibt live
- **aus der Claude-Session heraus** – über die Werkzeuge `read_db` / `write_db`, die direkt auf dieselben Daten zugreifen

Das löst die Frage des Auftraggebers ("wie kommen dort die E-Mail-Texte hin – legst du sie im GitHub ab und die Website nimmt sie von dort?"): **Nein, nichts von Paulas Daten geht je ins GitHub-Repo.** Das Repo enthält nur Programmcode und den Plan. Die Bewerbungstexte, Firmen und Mails liegen ausschließlich in der Dashboard-Datenbank.

Die Datenbank ist ein Dokumentspeicher: Sammlungen mit JSON-Dokumenten unter Pfaden wie `applications/a_0142`. Kein SQL, keine Migrationen. Schema in `docs/02-data-model.md`.

### 2. Die Claude-Session (der Arbeiter)

Eine Routine startet 3× täglich automatisch eine Session. Die Session liest ihre Arbeitsanweisung aus `runbooks/` im Repo und arbeitet sie ab. Sie hat drei Arten von Werkzeugen:

| Werkzeug | Art | Beispiel |
|---|---|---|
| Helfer-Skripte im Repo | deterministisch, Python | Gmail abfragen, Adzuna abfragen, HTML zu Text |
| Datenbank-Werkzeuge | deterministisch | `read_db`, `write_db` |
| Claude selbst | Intelligenz | "Ist das eine Absage?", "Passt diese Stelle?", "Schreib den Text" |

Die Skripte tun **nur** das Holen und Schreiben von Daten. Sie enthalten keine Logik, die ein Urteil fällt. Umgekehrt schreibt Claude nie direkt in die Datenbank, ohne dass ein Skript die Struktur geprüft hat. Diese Trennung ist der Grund, warum das System nachvollziehbar bleibt.

### 3. Das Dashboard (die Oberfläche)

Eine einzelne Seite mit vier Blöcken (Details in `docs/10-dashboard.md`). Sie liest die Datenbank live, zeigt Bewerbungen als Karten, bietet "Text kopieren" und "Lebenslauf herunterladen" und schreibt Paulas Aktionen (abgehakt, verworfen, Firma sperren) zurück in dieselbe Datenbank. Beim nächsten Lauf sieht Claude, was sie getan hat.

## Datenfluss – Phase 0: Mailbox-Archäologie (einmalig)

Das ist der Setup-Schritt, den der Auftraggeber verlangt hat: erst die Mailbox verstehen, dann daraus alles Übrige ableiten.

```
 Lauf 1  Breiter Blick, minimale Tiefe
   gmail_fetch.py --list --months 36
     → nur Absender, Betreff, Datum, Anhangs-Dateinamen. Keine Inhalte.
   Claude sortiert: bewerbungsbezogen ja/nein
     → Nicht-Treffer werden NICHT gespeichert, nur als "geprüft" vermerkt

 Lauf 2  Tiefer Blick, nur auf Treffer
   gmail_fetch.py --fetch <ids> --with-attachments
     → Volltext + Anhänge NUR dieser Mails
   Aus GESENDETEN Bewerbungsmails:
     · an welche Firma, welche Stelle, wann
     · welche Dateien hingen dran  → alle CV-Versionen sammeln
     · der Text selbst             → Stilprofil
   Aus EMPFANGENEN Mails:
     · Eingangsbestätigung / Absage / Einladung / Rückfrage
     → Bewerbungshistorie rekonstruieren

 Lauf 3  Verdichten
   Alle gefundenen CV-Versionen (oft dutzende) vergleichen:
     · neueste Fassung identifizieren
     · widersprüchliche Angaben markieren
     · daraus EINEN Faktenblock bauen
   Alle Motivationsschreiben vergleichen:
     · Stilprofil bauen
     · wiederkehrende Formulierungen sammeln
   Aus Berufsbezeichnungen + beworbenen Stellen:
     · Suchprofil vorschlagen (welche Jobtitel, welche Orte, welches Ausmaß)

 Lauf 4  Bestätigen
   Faktenblock + Stilprofil + Suchprofil erscheinen im Dashboard
   als "Bitte einmal durchsehen" → Paula korrigiert, bestätigt
   → erst danach startet Phase 2
```

Der Punkt an Lauf 3: Weil Paula dutzende CV-Fassungen verschickt hat, ist die *Menge* der Versionen selbst eine Information. Was in allen Fassungen steht, ist sicher wahr. Was nur in einer steht, ist entweder neu oder ein Ausrutscher – und wird zur Rückfrage.

## Datenfluss – Phase 2: Laufender Betrieb (3× täglich)

```
 1. jobs_fetch.py → neue Inserate aus allen aktiven Quellen
 2. Abgleich gegen die Datenbank: schon gesehen? schon beworben? Firma gesperrt?
 3. Regel-Vorfilter: Ort, Ausmaß, Ausschlusswörter   (kostet nichts)
 4. Claude bewertet die Übriggebliebenen (Score + Begründung + Bedenken)
 5. Über Schwellwert → Firma recherchieren (falls unbekannt) → Bewerbungstext schreiben
 6. Faktenprüfung gegen den Faktenblock
 7. Bestanden → Dokument in der Datenbank anlegen, Status "vorbereitet"
    → erscheint im Dashboard, Block 1
```

## Datenfluss – Phase 3: Rückkanal (3× täglich)

Zwei Dinge werden geprüft:

**Hat Paula gesendet?** Der Gesendet-Ordner wird nach Mails an die Empfänger vorbereiteter Bewerbungen durchsucht. Treffer → Status springt von "vorbereitet" auf "gesendet", mit dem echten Sendedatum. **Paula muss nichts abhaken.** (Sie kann es trotzdem, falls sie über ein anderes Konto gesendet hat – Knopf "hab ich geschickt".)

**Ist eine Antwort gekommen?** Neue Mails werden den laufenden Bewerbungen zugeordnet, eingeordnet (Bestätigung / Absage / Einladung / Rückfrage / Angebot) und der Status wandert:

```
 vorbereitet ──(Paula sendet)──▶ gesendet ──┬─▶ Bestätigung  (bleibt "gesendet")
                                            ├─▶ Absage       → Block 3, Dankestext wird vorbereitet
                                            ├─▶ Einladung    → ganz oben, hervorgehoben
                                            ├─▶ Rückfrage    → Antworttext wird vorbereitet
                                            └─▶ keine Antwort nach 6 Wochen → Nachfass-Vorschlag
```

## Was im Repo liegt und was nicht

| Im Repo (GitHub) | In der Dashboard-Datenbank | Nirgends gespeichert |
|---|---|---|
| Helfer-Skripte | Firmen, Stellen, Bewerbungen | Mails ohne Bewerbungsbezug |
| Arbeitsanweisungen (`runbooks/`) | Bewerbungstexte, Antworttexte | Anhänge fremder Mails |
| Plan (`docs/`) | Faktenblock, Stilprofil, Suchprofil | Roh-HTML von Mails |
| Dashboard-Quellcode | Auszüge bewerbungsbezogener Mails | Zugangsdaten im Klartext |
| Tests, Beispieldaten (erfunden) | Paulas Lebenslauf-Dateien | |

**Keine personenbezogenen Daten im Repo. Keine Ausnahme.**

## Modulstruktur

```
scripts/                      Helfer, von der Session aufgerufen
├── gmail_fetch.py            Liste holen / Mails holen / Anhänge holen (NUR LESEN)
├── gmail_auth.py             Einmalige Anmeldung, Token erneuern
├── jobs_fetch.py             Alle aktiven Quellen abfragen → normalisierte Stellen
├── sources/
│   ├── adzuna.py             Offizielle Schnittstelle (Österreich)
│   ├── mailalert.py          Job-Mails der Portale auswerten
│   ├── careerpage.py         Karriereseiten einzelner Firmen
│   └── manual.py             Von Paula eingereichte Links
├── db_io.py                  Datenbank lesen/schreiben, Schema prüfen
├── dedup.py                  Firmennamen normalisieren, Doppelte finden
├── extract.py                PDF/DOCX → Text; HTML → Text; Zitate entfernen
└── checks.py                 Faktenprüfung (regelbasierter Teil)

runbooks/                     Arbeitsanweisungen für die Session
├── phase0-mailbox.md         Mailbox-Archäologie, Schritt für Schritt
├── phase1-profile.md         Faktenblock, Stilprofil, Suchprofil bauen
├── daily-jobs.md             Der 3×-tägliche Lauf
├── daily-replies.md          Rückkanal
└── weekly-review.md          Wochenbericht, Schwellwerte nachjustieren

dashboard/
├── index.html                Die ganze Seite (eine Datei)
└── README.md                 Wie veröffentlichen, wie aktualisieren

docs/                         Dieser Plan
tests/                        Tests + erfundene Beispieldaten
```

Kein Python-Package, keine CLI mit zwanzig Befehlen, kein SQLite. Die Skripte sind einzeln aufrufbar, tun genau eine Sache und geben JSON aus.

## Architekturentscheidungen

| # | Entscheidung | Alternativen | Warum so |
|---|---|---|---|
| A1 | Dashboard-Datenbank statt eigener Datenbank | SQLite auf VPS, Supabase, Postgres | Kein Server zu betreiben. Von Website **und** Claude-Session erreichbar. Keine zweite Rechnung |
| A2 | Claude-Session statt API-Integration | Anthropic-Schnittstelle mit eigenem Schlüssel | Ausdrücklicher Wunsch. Keine getrennten Kosten, kein Schlüssel-Management, voller Kontext beim Denken |
| A3 | Geplante Routine statt Cron auf Server | systemd-Timer, GitHub Actions | Kein Server. Läuft im selben Container-System wie die Entwicklung |
| A4 | Gmail **nur lesend** (`gmail.readonly`) | `gmail.modify` + `gmail.send` | Das System sendet nicht. Minimaler Zugriff = minimales Risiko. Auch kein Label-Setzen |
| A5 | Website als veröffentlichte Seite | Eigene Domain + Vercel + Supabase | Sofort verfügbar, Datenbank eingebaut, Zugriff auf Organisationsmitglieder beschränkt. **Siehe Vorbehalt unten** |
| A6 | Paula sendet selbst | Automatischer Versand nach Freigabe | Löst Reputations-, Rechts- und Technikprobleme auf einen Schlag |
| A7 | Versand wird **erkannt**, nicht gemeldet | Paula hakt manuell ab | Der Gesendet-Ordner sagt die Wahrheit. Kein Pflegeaufwand für sie |
| A8 | Profil aus der Mailbox statt aus einem Formular | Fragebogen an Paula | Die Antworten liegen schon in ihren dutzenden CV-Versionen. Schneller, vollständiger, ehrlicher |
| A9 | Faktenblock + Stilprofil als Markdown-Dateien in der Datenbank | Vektor-Datenbank, Beispiele bei jedem Aufruf | Lesbar, von Paula korrigierbar, versionierbar |
| A10 | Skripte holen Daten, Claude urteilt | Alles in Python mit Modellaufrufen; oder alles Claude | Deterministisches bleibt deterministisch und testbar. Urteile bleiben beim Modell mit vollem Kontext |
| A11 | Ein Dashboard mit vier Blöcken, keine Unterseiten | Mehrseitige App mit Navigation | Paula soll alles auf einen Blick sehen. Scrollen statt klicken |

## Vorbehalt zu A5: Wer kann das Dashboard öffnen?

Eine veröffentlichte Seite mit Datenbank ist **organisationsintern** – jede Person, die sie öffnet, muss bei claude.ai angemeldet und Mitglied der Organisation des Betreibers sein. Das steht im Widerspruch zur ursprünglichen Annahme, Paula habe keinen Claude-Zugang.

Drei Wege, in der Reihenfolge meiner Empfehlung:

1. **Paula bekommt einen Zugang in Alexanders Organisation.** Sie loggt sich einmal ein, setzt ein Lesezeichen, fertig. Für sie ist das eine Website mit Login – dass Claude dahintersteckt, muss sie nie erfahren. Ob das ein bezahlter Platz ist, hängt von Alexanders Abo ab (**offene Frage Q17**).
2. **Eigene Website**, klassisch: eine kleine Seite bei einem Hoster, eine gemietete Datenbank, ein Passwort. Voll unter Kontrolle, für Paula nur eine URL. Kostet ~0–10 €/Monat und etwa eine Woche Mehrarbeit. Der Plan bleibt sonst identisch – nur `db_io.py` und die Dashboard-Datei ändern sich.
3. **Übergangslösung:** Alexander leitet den Dashboard-Inhalt täglich als Mail oder Nachricht an Paula weiter. Unbefriedigend, aber funktioniert ab Tag eins.

Diese Frage muss vor Etappe M3 beantwortet sein; alles davor ist davon unberührt.

## Abhängigkeiten

Python 3.12 mit: `google-api-python-client`, `google-auth-oauthlib` (Gmail lesen), `httpx` (Job-Quellen), `beautifulsoup4` + `lxml` (HTML), `pypdf` + `python-docx` (Lebensläufe lesen), `rapidfuzz` (Firmennamen vergleichen), `python-dateutil`. Entwicklung: `pytest`, `ruff`, `respx`.

Kein Anthropic-SDK, kein Agent-Framework, keine Datenbank-Bibliothek, kein Telegram, kein Webserver.

## Entscheidungen während der Umsetzung

*(Die ausführende KI trägt hier ein, was der Plan offen ließ. Format: Datum – Entscheidung – Begründung.)*
