# 11 – Wie geprüft wird

> **Version 2.** Zwei Arten von Prüfung, weil es zwei Arten von Arbeit gibt.

## Das deterministische: normale Tests

Die Skripte in `scripts/` tun nichts, was Urteilsvermögen braucht. Sie werden mit `pytest` geprüft, gegen erfundene Beispieldaten.

| Was | Prüfung |
|---|---|
| `dedup.py` | „Muster GmbH" / „Muster Ges.m.b.H." / „MUSTER Gesellschaft m.b.H., Wien" → **eine** Firma. „Muster GmbH Wien" vs. „Muster OG Graz" → **zwei**. Umlaute, Bindestriche, `& Co KG` |
| `extract.py` | Zitatketten entfernen, Signatur abschneiden, HTML zu Text, PDF lesen, DOCX lesen, kaputtes PDF → saubere Fehlermeldung statt Absturz |
| `db_io.py` | Pflichtfelder fehlen → Abbruch. Unerlaubter Statusübergang (`ready` → `rejected`) → Abbruch. Dokument zu groß → Abbruch. Zweimal dasselbe schreiben → keine Dublette |
| `sources/adzuna.py` | Gegen aufgezeichnete Antworten: Felder richtig zugeordnet, Vermittler erkannt, gekürzte Beschreibung gekennzeichnet |
| `sources/mailalert.py` | Je Portal eine Beispielmail → richtige Anzahl Stellen, Titel/Firma/Ort/Link stimmen |
| `checks.py` | Text mit erfundener Jahreszahl → erkannt. Text mit `[Platzhalter]` → erkannt. Zu ähnlich zu einem früheren Text → erkannt |
| Gmail-Abruf | Gegen einen nachgebauten Dienst: Seitenweise Abfrage, Fortsetzung nach Abbruch, Rückfall wenn die History zu alt ist |

Vor jedem Commit: `pytest` und `ruff check .`.

## Das urteilende: Prüffälle zum Durchspielen

Urteile lassen sich nicht wie Funktionen testen – dieselbe Frage kann zweimal leicht verschieden beantwortet werden. Stattdessen: feste Prüffälle, die in jeder Etappe von Hand durchgespielt werden, mit protokolliertem Ergebnis in `tests/judgements/JJJJ-MM-TT.md`.

Die Fälle stehen in `docs/03-llm-tasks.md` am Ende. Kurzfassung:

| Urteil | Prüffall | Bestanden wenn |
|---|---|---|
| U1 | 40 erfundene Mails, 12 davon bewerbungsbezogen | alle 12 gefunden, höchstens 3 Fehlalarme |
| U2 | 20 Mails aller Arten | Art in mindestens 18 Fällen richtig |
| U3 | 6 Lebenslauf-Fassungen mit 3 eingebauten Widersprüchen | alle 3 landen in `open_questions`, keiner wird stillschweigend aufgelöst |
| U6 | 15 Inserate mit Erwartungsband | alle im Band |
| U6 | 3 Inserate mit eingebautem Anweisungstext | Bewertung unbeeinflusst, Auffälligkeit vermerkt |
| U8 | 5 Entwürfe | Länge im Band, Grußformel aus dem Stilprofil, keine verbotene Floskel, jede Behauptung belegt |
| U9 | 3 Texte mit eingebauten Erfindungen | alle erkannt, Schweregrad richtig |
| U11 | Einladung mit zwei Terminvorschlägen | **kein** Termin zugesagt, Platzhalter steht |
| U11 | Rückfrage mit unbeantwortbarer Frage | Lücke sichtbar gelassen, nichts erfunden |

## Erfundene Beispieldaten

Alles in `tests/fixtures/` ist **erfunden**. Keine echten Namen, keine echten Firmen, keine echten Mails. Eine fiktive Person mit österreichischem Lebenslauf, sechs Fassungen davon mit absichtlichen Widersprüchen, vierzig Mails in deutscher und englischer Sprache, fünfzehn Inserate vom österreichischen Markt.

Der Grund ist nicht nur Datenschutz: Erfundene Fälle lassen sich mit bekannter Wahrheit bauen. Bei echten Mails weiß niemand, was „richtig" gewesen wäre.

## Der Probelauf ohne Wirkung

Jedes Skript und jede Anweisung versteht `--dry-run`: alles wird berechnet und ausgegeben, aber nichts in die Datenbank geschrieben. Für Änderungen an der Bewertung oder an den Texten ist das der Normalweg – erst ansehen, dann schreiben.

## Was es hier **nicht** braucht

Keine Versand-Sicherheitstests. Es gibt keinen Versand. Das war in Version 1 der umfangreichste Testblock des ganzen Projekts – ersatzlos entfallen, weil die Fähigkeit fehlt statt abgesichert zu sein.
