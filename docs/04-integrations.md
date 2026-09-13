# 04 – Integrationen

> **Version 2.** Land: **Österreich**. Gmail nur lesend. Kein Telegram. Kein Versand.

---

## 4.1 Gmail – nur lesen

### Berechtigung

Ein einziger Bereich: `https://www.googleapis.com/auth/gmail.readonly`

Mehr nicht. Kein Senden, kein Ändern, kein Label-Setzen. Das System **kann** technisch nichts in Paulas Postfach anstellen, selbst wenn es wollte. Das ist der stärkste Sicherheitsmechanismus des ganzen Projekts – stärker als jede Prüfung im Code.

### Einrichtung (macht Alexander, ausführliche Anleitung in `deploy/SETUP.md`)

1. Google Cloud Console → neues Projekt anlegen
2. Gmail API aktivieren
3. OAuth-Zustimmungsbildschirm: Typ **Extern**, Bereich `gmail.readonly` hinzufügen, Paulas Adresse als Testnutzerin
4. **Wichtige Falle:** Solange die App im Status *Testing* steht, verfällt die Anmeldung nach **7 Tagen**. Der Veröffentlichungsstatus muss auf **In Produktion** gesetzt werden. Google zeigt dann beim Login eine Warnung „nicht verifizierte App" (mit „Erweitert → trotzdem fortfahren") – das ist bei eigener Nutzung in Ordnung, eine Verifizierung braucht es unter 100 Nutzern nicht.
5. Zugangsdaten → OAuth-Client-ID → Typ **Desktop-App** → JSON herunterladen
6. `python scripts/gmail_auth.py` – öffnet den Anmeldelink. **Paula meldet sich hier selbst an und stimmt zu.** Das ist zugleich ihre technische Einwilligung.
7. Das entstehende Token wird als Geheimnis in der Umgebung hinterlegt, in der die Routine läuft – nicht ins Repo (siehe `docs/06-operations.md`).

### Lesen

**Phase 0, Lauf 1 (breit, flach):** `users.messages.list` mit Suchausdruck, dann `users.messages.get(format="metadata")` – liefert **nur** Kopfzeilen, keinen Inhalt. Das ist die technische Umsetzung der Auflage „ansonsten ihre E-Mails in Ruhe lassen".

Suchausdruck (mehrsprachig, in `config/settings.yaml` pflegbar):
```
newer_than:36m (bewerbung OR bewerbungsunterlagen OR "ihre bewerbung" OR absage OR
  "vorstellungsgespräch" OR "bewerbungsgespräch" OR einladung OR lebenslauf OR
  motivationsschreiben OR application OR "your application" OR interview OR
  stelle OR position)
```
Getrennt auch `in:sent` – die gesendeten Bewerbungen sind die wertvollste Quelle.

**Phase 0, Lauf 2 (tief, schmal):** Nur für die in Lauf 1 als relevant erkannten IDs: `format="full"` plus `users.messages.attachments.get` für die Anhänge. Nur hier werden Dateien heruntergeladen – und nur aus Mails, die Paula selbst als Bewerbung verschickt hat.

**Laufend:** `users.history.list(startHistoryId=…)` holt nur Änderungen seit dem letzten Lauf. Wenn Google die History nicht mehr hat (älter als etwa eine Woche), Rückfall auf `newer_than:7d` mit Abgleich gegen `seen`.

**Versanderkennung:** `in:sent newer_than:7d` – für jede Bewerbung im Status `ready` wird geprüft, ob eine gesendete Mail an ihre Empfängeradresse existiert. Treffer → Status `sent`, mit echtem Datum und Thread-ID (die brauchen wir, um spätere Antworten zuzuordnen).

### Aufbereitung (`scripts/extract.py`)

`text/plain` bevorzugen, sonst HTML zu Text. Zitate entfernen (`>`-Zeilen, „Am … schrieb …", „On … wrote", „-----Ursprüngliche Nachricht-----"), Signatur nach `--` abschneiden. Auf 8.000 Zeichen kürzen. Anhänge außerhalb von Phase 0: nur Dateiname, Typ und Größe merken, **nicht** herunterladen.

### Lebensläufe lesen

PDF über `pypdf`, DOCX über `python-docx`. Gescannte PDFs ohne Textebene → die Datei wird trotzdem gespeichert (Paula kann sie herunterladen), aber der Inhalt geht nicht in den Faktenblock; stattdessen ein Vermerk in `open_questions`.

---

## 4.2 Stellenquellen für Österreich

> Ausführliche Begründung und Abdeckungsanalyse: **[`docs/12-quellen-abdeckung.md`](12-quellen-abdeckung.md)**

Vier Wege, die sich ergänzen. Keiner allein reicht, zusammen decken sie den Markt ab.

| # | Quelle | Zugang | Rolle |
|---|---|---|---|
| 1 | **EURES** (EU-Stellenportal) | Öffentliche Schnittstelle, ohne Anmeldung | **Der Weg zu den AMS-Stellen.** Die nationalen Arbeitsverwaltungen melden dorthin |
| 2 | **METAJob.at** | Job-Mail, evtl. RSS | Größte Meta-Suchmaschine Österreichs. Findet auch Stellen, die **nirgends inseriert** sind – von KMU, NGOs, öffentlichen Stellen, direkt von Firmenwebsites |
| 3 | **Adzuna AT** | Offizielle Schnittstelle, kostenloser Schlüssel | Stabile Primärquelle, aggregiert die großen Portale |
| 4 | **Job-Mails der Portale** | Suchaufträge, die Paula einrichtet | karriere.at, willhaben, StepStone, hokify – der einzige vorgesehene maschinelle Weg dorthin |

Dazu: von Paula eingereichte Links, Karriereseiten beobachteter Firmen.

### 4.2.1 EURES

```
POST https://europa.eu/eures/api/jv-searchengine/public/jv-search/search
GET  https://europa.eu/eures/api/jv-searchengine/public/jv/id/{id}?requestLang=de
```

Ohne Anmeldung. Der Suchkörper nimmt `keywords`, `locationCodes` (NUTS-Regionen, Österreich `AT`), `publicationPeriod`, `positionScheduleCodes` (Arbeitszeit), `occupationUris` (ESCO-Berufscodes), `requiredLanguages`, `page`, `resultsPerPage`, `sortSearch` (`MOST_RECENT`). Ergebnis: Arbeitgeber, Ort, Gehalt, Bewerbungskontakt, ESCO-Einordnung. Höchstens 10.000 Treffer pro Suche – für uns bedeutungslos.

Die Endpunkte sind nur von der Gemeinschaft dokumentiert (nicht offiziell). Sie können sich ändern, ohne Ankündigung. Deshalb: Testfälle, und nach drei Fehlläufen schaltet sich die Quelle selbst ab.

**Erste Aufgabe in M4 [prüfen]:** Wie viele österreichische Stellen liefert EURES, und sind die AMS-Stellen tatsächlich enthalten? Davon hängt ab, wie wichtig diese Quelle ist.

### 4.2.2 METAJob.at

Durchsucht laufend das österreichische Web – Portale **und** Firmenwebsites – und kommt auf rund 108.000 Stellen. Die für Paula entscheidende Eigenschaft: Dort stehen auch Stellen kleiner Betriebe, die sich die Portalgebühren sparen. Auf solche Stellen bewerben sich zehn Leute, nicht zweihundert.

Zugang: Job-Mail einrichten. Ob es RSS gibt, ist in M4 zu prüfen.

### 4.2.3 Adzuna

```
https://api.adzuna.com/v1/api/jobs/at/search/1
  ?app_id=…&app_key=…&what=…&where=Wien&distance=30
  &max_days_old=2&results_per_page=50&sort_by=date
```

Zwei Fallen: Die Beschreibung ist ein **Auszug** – ab Schwellwert wird die Zielseite geladen und der Volltext über die eingebettete Stellenbeschreibung geholt. Und als Firma steht oft ein **Personalvermittler** (ISG, epunkt, Hill, Trenkwalder, Manpower…); für die gilt die 180-Tage-Sperre nicht, die Karte weist aber darauf hin. Liste in `config/staffing_agencies.txt`.

Kostenloses Kontingent beim Registrieren prüfen. Drei Läufe täglich mit vier Suchbegriffen bleiben darunter.

### 4.2.4 Job-Mails der Portale

Paula richtet bei **karriere.at**, **willhaben Jobs**, **StepStone AT**, **hokify** und **METAJob** je einen täglichen Suchauftrag an ihre Adresse ein. Das System erkennt die Mails am Absender und liest Titel, Firma, Ort und Link heraus.

Warum das die richtige Lösung ist und nicht ein Notbehelf: Es ist der Weg, den die Portale selbst anbieten. Kein Verstoß gegen Nutzungsbedingungen, keine Sperre, kein Bruch beim nächsten Seiten-Umbau. Und es erreicht genau die Portale, die maschinell verschlossen sind.

Ein kleiner Leser je Portal, mit einer Beispielmail als Testfall. Einrichtung: zehn Minuten mit Paula, gehört zu M2.

### 4.2.5 Einmalig: Jooble

Kostenloser Zugang auf Anfrage, aber mit einem Gesamtkontingent von 500 Abfragen je Schlüssel. Nicht für den Dauerbetrieb – gut für einen einmaligen breiten Durchgang zu Beginn, um den Bestand zu füllen.

### 4.2.6 Karriereseiten und eingereichte Links

Für beobachtete Firmen: täglich die Karriereseite laden, Stellen über die eingebettete Stellenbeschreibung herausziehen. Häufige Plattformen mit offenen Stellenlisten: Personio (in Österreich verbreitet), Greenhouse, Lever, SmartRecruiters.

Eingereichte Links: Paula fügt im Dashboard einen Link ein, der nächste Lauf holt die Stellenbeschreibung.

### 4.2.7 Was die Abdeckung wirklich begrenzt

Nicht die Zahl der Quellen, sondern die **Breite der Suchbegriffe**. Wer nur nach einer Berufsbezeichnung sucht, verpasst die fünf anderen Bezeichnungen für dieselbe Arbeit. Deshalb wird das Suchprofil in Phase 1 aus ihren bisherigen Bewerbungen erarbeitet, bewusst breit angesetzt und erweitert, sobald im Datenstrom neue Bezeichnungen für verwandte Rollen auftauchen.

## 4.3 Firmen für Initiativbewerbungen

> Die vollständige Strategie steht in **[`docs/13-initiativbewerbungen.md`](13-initiativbewerbungen.md)**. Hier nur die technischen Zugänge.

Das Grundprinzip: nicht Firmenlisten abarbeiten, sondern **Signale für Einstellungsbedarf** erkennen. Angeschrieben wird nur, wo sich ein Satz formulieren lässt, der ausschließlich auf diese Firma zutrifft.

### Grundgesamtheit – welche Firmen existieren

| Quelle | Inhalt | Zugang |
|---|---|---|
| **OpenStreetMap / Overpass** | Alle erfassten Betriebe mit Name, Adresse, Website, Telefon, Branche. Bezirksweise abfragbar | Offen, ohne Schlüssel, ODbL (Namensnennung). **Bester Einstieg** |
| **GISA** (Gewerbeinformationssystem Austria) | Zentrales Gewerberegister: Name, Standort, Gewerbeberechtigung | Kostenlose Online-Abfrage **[prüfen]** |
| **WKO Firmen A–Z** | Branchenverzeichnis nach Branche und Bezirk | Öffentlich, Bedingungen für automatisierten Abruf **[prüfen]** |
| **Firmenbuch-Neueintragungen** | Täglich veröffentlichte Neueintragungen und Änderungen | Öffentlich |
| Aus dem eigenen Bestand | Firmen aus Paulas Mailbox, aus jedem gesehenen Inserat, aus Vergabedaten | intern |

### Signalquellen – wo gerade Bedarf entsteht

| Signal | Quelle | Aufwand |
|---|---|---|
| Firma schreibt mehrere andere Stellen aus | **Der eigene Inseratsstrom** – kostet nichts extra | trivial |
| Firma hat einen öffentlichen Auftrag gewonnen | **OffeneVergaben.at**, tägliches CSV, alle Zuschläge über 50.000 € | gering |
| Inserat läuft ungewöhnlich lange | eigener Bestand über die Zeit | trivial |
| Firmenbuch-Bewegung | Neueintragungen und Änderungen | mittel |
| Wachstumsnachricht | **wiederkehrende Websuchen** nach Bezirk und Branche | gering |
| Branchennachbarschaft | eigene Firmendatenbank | trivial |
| Regionale Nachfrage | **AMS-Daten auf data.gv.at**: offene Stellen nach Bezirk und Beruf (Summen, keine Einzelinserate) | gering |
| Alte Kontakte | Bewerbungshistorie aus Phase 0 | trivial |

Sechs der acht fallen aus Daten ab, die das System ohnehin verarbeitet.

### Ausdrücklich nicht

Keine Massenabfragen bei Kartendiensten, kein Auslesen sozialer Netzwerke, keine gekauften Adresslisten, keine Signale über einzelne **Personen** – nur über Firmen, und nur aus öffentlich bekannten Tatsachen.

## 4.4 Das Dashboard

Eine veröffentlichte Seite mit eigener Datenbank, Dateiablage und Download-Funktion.

- **Datenbank:** dieselbe, die die Session über `read_db`/`write_db` beschreibt
- **Dateiablage:** Paulas Lebenslauf-Dateien, in Phase 0 aus den Mail-Anhängen übernommen. Die Karte bietet sie zum Herunterladen an
- **Zugriffsrechte:** Paula darf lesen und Status-Felder ändern (abhaken, verwerfen, Firma sperren, Änderungswunsch schreiben). Sie kann keine Bewerbungen anlegen und keine Fakten ändern – Letzteres nur über den bestätigten Weg im Profil-Bereich
- **Veröffentlichen und aktualisieren:** aus der Claude-Session, gleiche Adresse, siehe `dashboard/README.md`

Zur Frage „wie kommen die Texte dorthin": Die Session schreibt sie direkt in die Datenbank. Kein Umweg über GitHub, keine Datei, die jemand hochlädt.

---

## 4.5 Was es **nicht** gibt

Keinen Versandweg. Keinen SMTP-Zugang. Keinen Mailversanddienst. Kein Telegram, kein WhatsApp. Keine Browser-Steuerung, die Formulare ausfüllt. Diese Abwesenheit ist eine Eigenschaft des Entwurfs, kein fehlendes Feature.
