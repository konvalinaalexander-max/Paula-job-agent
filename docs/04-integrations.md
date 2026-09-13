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

Der Markt ist hier anders als in der Schweiz oder Deutschland: **karriere.at**, **willhaben Jobs** und **StepStone AT** dominieren, das **AMS** hat die größte öffentliche Sammlung – und keine davon bietet eine offene Schnittstelle für Suchende.

### Rangfolge der Quellen

| # | Quelle | Zugang | Bewertung |
|---|---|---|---|
| 1 | **Adzuna Österreich** | Offizielle Schnittstelle, kostenlos, Kennung per Registrierung | **Primärquelle.** Aggregiert unter anderem österreichische Portale. Startpunkt der Umsetzung |
| 2 | **Job-Mails der Portale** | Suchaufträge, die Paula bei karriere.at, willhaben, StepStone, AMS einrichtet | **Die wichtigste Quelle für Österreich.** Sauber, stabil, vom Portal selbst vorgesehen. Deckt genau die Portale ab, die keine Schnittstelle haben |
| 3 | **Karriereseiten** einzelner Firmen | Öffentlich | Für Firmen, die Paula interessieren. Viele nutzen Personio/Greenhouse/Lever mit offenen Job-Listen |
| 4 | **Von Paula eingereichte Links** | Dashboard | Sie sieht etwas, fügt den Link ein, das System bereitet die Bewerbung vor |
| 5 | AMS „alle jobs" direkt | Schwierig | Die Suche läuft zwar über eine JSON-Schnittstelle, aber jede Anfrage braucht ein signiertes Merkmal, das nur die eigene Weboberfläche erzeugen kann. Ohne echten Browser nicht nutzbar. **Deshalb: E-Mail-Suchauftrag statt Abruf** |
| 6 | willhaben / karriere.at direkt | Nein | Keine offene Schnittstelle; fertige Auslese-Dienste existieren, verstoßen aber gegen die Nutzungsbedingungen. Nur nach ausdrücklicher Entscheidung (offene Frage Q8) |

### 4.2.1 Adzuna (Primärquelle)

Registrierung auf dem Entwicklerportal ergibt Kennung und Schlüssel. Abfrage:

```
https://api.adzuna.com/v1/api/jobs/at/search/1
  ?app_id=…&app_key=…
  &what=Projektassistenz&where=Wien&distance=30
  &max_days_old=2&results_per_page=50&sort_by=date
```

Land `at`. Felder: Titel, Firma, Ort, Beschreibung (**gekürzt**), Weiterleitungslink, Datum, Gehalt.

**Zwei Fallen:**
- Die Beschreibung ist ein Auszug. Sobald eine Stelle über dem Schwellwert liegt, wird die Zielseite geladen und der Volltext über die eingebettete Stellenbeschreibung (`JobPosting`-Auszeichnung) oder den Haupttext geholt. Klappt das nicht, wird mit dem Auszug weitergearbeitet und das vermerkt.
- Als Firma steht oft der **Personalvermittler** (ISG, epunkt, Hill, Trenkwalder, Manpower…). Für diese gilt die 180-Tage-Sperre nicht, weil man sich bei derselben Agentur auf verschiedene Stellen bewirbt – aber die Karte weist darauf hin. Liste in `config/staffing_agencies.txt`.

Das kostenlose Kontingent liegt in der Größenordnung von einigen hundert bis tausend Abfragen im Monat – **beim Registrieren nachsehen**. Drei Läufe täglich mit vier Suchbegriffen und ein bis zwei Seiten bleiben darunter.

### 4.2.2 Job-Mails der Portale (`scripts/sources/mailalert.py`)

Der pragmatische Kern der Österreich-Lösung. Paula richtet bei **karriere.at**, **willhaben Jobs**, **StepStone AT** und **AMS alle jobs** je einen täglichen Suchauftrag ein, der an ihre Adresse geht. Das System erkennt diese Mails am Absender, liest Titel, Firma, Ort und Link heraus und behandelt sie wie jede andere Stellenquelle.

Warum das die beste Lösung ist: Es ist genau der Weg, den die Portale selbst anbieten. Kein Verstoß, keine Sperre, keine kaputte Auslese nach dem nächsten Seiten-Umbau. Und es deckt exakt die Portale ab, an die man sonst nicht herankommt.

Je Portal ein kleiner Leser mit einer Beispielmail als Testfall. Der Volltext wird bei Bedarf über den Link nachgeladen (mit Pause zwischen Abrufen, `robots.txt` beachtet, Kennung im User-Agent).

Einrichtung gehört in Etappe M2 und braucht zehn Minuten mit Paula.

### 4.2.3 Karriereseiten (`scripts/sources/careerpage.py`)

Für Firmen mit `careers_url`: täglich laden, Stellen über die `JobPosting`-Auszeichnung oder Linkmuster herausziehen. Häufige Plattformen mit offenen Stellenlisten: Personio (in Österreich sehr verbreitet), Greenhouse, Lever, SmartRecruiters, Workday. Für die ersten vier lohnt je ein kleiner Leser – die Listen sind offen abrufbar und ändern sich selten.

### 4.2.4 Von Paula eingereicht (`scripts/sources/manual.py`)

Sie fügt im Dashboard einen Link ein. Der nächste Lauf lädt die Seite, holt die Stellenbeschreibung und bereitet die Bewerbung vor. Lässt sich die Seite nicht lesen, fragt die Karte nach dem Text zum Einfügen.

---

## 4.3 Firmen für Initiativbewerbungen (Österreich)

| Quelle | Zugang | Anmerkung |
|---|---|---|
| **WKO Firmen A–Z** | Öffentliches Branchenverzeichnis | Nahezu vollständig für gewerbliche Betriebe, nach Branche und Bezirk durchsuchbar. Nutzungsbedingungen vor automatisiertem Abruf prüfen; notfalls von Hand exportieren |
| **data.gv.at** | Offene Verwaltungsdaten | Enthält verschiedene Unternehmensdatensätze; vor M6 sichten, was nutzbar ist |
| **Firmenbuch / Wirtschafts-Compass** | Einzelabfragen kostenlos | Kein Massenabruf. Gut zur Prüfung einzelner Firmen |
| **Firmen aus Paulas Mailbox** | intern | Wo sie schon war – und ähnliche Firmen |
| **Firmen aus Inseraten** | intern | Wer inseriert, stellt ein. Auch wenn die konkrete Stelle nicht passte |
| **Startliste** `config/companies_seed.csv` | Alexander und Paula | Die Firmen, die sie ohnehin im Kopf hat. **Bester Startpunkt** |

Ablauf: sammeln → regelbasiert vorsortieren (Branche, Umkreis, Größe, nicht gesperrt) → nur die besten zehn pro Nacht recherchieren (U7) → bewerten → Text vorbereiten.

Ausdrücklich nicht: Google-Maps-Massenabfragen, LinkedIn-Firmenauslese, gekaufte Adresslisten.

---

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
