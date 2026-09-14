# Offene Fäden

Dinge, denen ich nachgehen wollte, als gerade keine Zeit war. Beim Streifzug
(letzter Abschnitt jedes Runbooks) hier zuerst nachsehen.

Format: `- [ ] Was · warum interessant · wann aufgefallen`

## Offen

- [ ] Liefert EURES tatsächlich AMS-Stellen? · entscheidet über den Wert der Quelle · 13.09.2026
- [ ] Hat METAJob einen RSS-Zugang, oder nur Job-Mails? · RSS wäre stabiler · 13.09.2026
- [ ] Wie weit reicht die Firmenabdeckung von OpenStreetMap außerhalb der Städte? · entscheidet, ob GISA oder WKO zusätzlich nötig sind · 13.09.2026
- [ ] Bedingungen von WKO Firmen A–Z für automatisierten Abruf prüfen · 13.09.2026
- [ ] Gibt es Job-Mails, die Stellen enthalten, die keine andere Quelle hat? · misst den Eigenanteil · 13.09.2026
- [ ] Wie lang darf der vorausgefüllte Gmail-Link sein, bevor er bricht? · betrifft den bequemsten Weg für Paula · 13.09.2026

- [ ] App-Passwoerter bei Google beobachten · sie gelten als auslaufend; wenn sie abgeschaltet werden, muss `scripts/mail.py` auf den Cloud-Weg umgestellt werden (und dann stellt sich die 7-Tage-Frage neu) · 14.09.2026

## Erledigt

- [x] **Wie wird Paulas Mailbox angebunden?** · 14.09.2026 · Ergebnis: **App-Passwort + IMAP**, nicht der Cloud-Weg. Grund: `gmail.readonly` ist bei Google ein besonders geschuetzter Bereich; ohne Sicherheitsaudit verfaellt die Berechtigung alle 7 Tage. App-Passwoerter laufen nicht ab und kosten Paula zwei Klicks. Preis: technisch Vollzugriff statt reinem Leserecht - dafuer enthaelt `scripts/mail.py` nachweislich keinen Versandweg

*(mit Datum und Ergebnis, damit nichts zweimal untersucht wird)*
