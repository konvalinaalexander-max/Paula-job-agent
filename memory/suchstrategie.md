# Suchstrategie

Die Suchbegriffe stehen technisch in `config/settings.yaml` und `profile/search`
in der Datenbank. Hier steht, **warum** – und was noch auszuprobieren ist.

## Stand

*Wird nach Phase 1 gefüllt. Bis dahin ist Paulas Beruf nicht bekannt – er wird
aus ihrer Mailbox erarbeitet, nicht abgefragt.*

## Wie die Liste wächst

Die wichtigste Einsicht aus `docs/12-quellen-abdeckung.md`: **Nicht die Zahl der
Quellen begrenzt die Abdeckung, sondern die Breite der Begriffe.** Dieselbe Arbeit
heißt bei fünf Arbeitgebern fünf Mal anders.

Bei jedem Lauf mitlaufen lassen:

1. **Titel lesen, die knapp nicht passten.** Wenn ein Inserat gut aussah, aber unter
   keinem der Suchbegriffe gefunden wurde, fehlt ein Begriff.
2. **Aus Inseratstexten lernen.** Wie nennt die Stelle sich selbst im Fließtext,
   verglichen mit der Überschrift?
3. **Aus Absagen lernen.** Steht dort eine andere Bezeichnung für dieselbe Rolle?
4. **Nachbarbegriffe prüfen.** Eine neue Bezeichnung eine Woche testen, dann
   entscheiden: bringt sie eigene Treffer oder nur Dubletten?

## Zu probieren

*(Liste wächst im Betrieb. Jeder Eintrag: Begriff, Erwartung, Ergebnis, Entscheidung.)*

## Verworfen

*(Begriffe, die nur Rauschen brachten – mit Grund, damit sie nicht wiederkehren.)*

## Regionen

Paula ist **umzugsbereit** (Antwort des Auftraggebers, 13.09.2026). Damit gilt
nicht mehr nur der Pendelradius:

| Ring | Reichweite | Behandlung |
|---|---|---|
| 1 | Tagespendeln | Standard, alle Signale, niedrigster Schwellwert |
| 2 | Erweiterte Region | wie Ring 1, leicht höherer Schwellwert |
| 3 | Restliches Österreich | **aktiv**, aber deutlich höherer Schwellwert – eine Stelle muss einen Umzug wert sein. Die Karte weist auf die Entfernung hin |

Zu beobachten: Nimmt sie Vorschläge aus Ring 3 an oder verwirft sie sie? Nach
zwanzig Karten sollte die Antwort im Lerntagebuch stehen.
