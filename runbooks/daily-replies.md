# Täglicher Lauf: Rückkanal

Läuft direkt nach `daily-jobs.md`. Dauer 5–15 Minuten. Zwei Fragen: Hat Paula etwas
abgeschickt? Ist eine Antwort gekommen?

## Schritt 0 · Gedächtnis

`memory/textwissen.md` lesen – hier fallen die Beobachtungen an, die dort hingehören.

## Schritt 1 · Hat sie gesendet?

```
python scripts/gmail_fetch.py --sent --newer-than 7d
```

Für jede Bewerbung auf `ready`: Gibt es eine gesendete Mail an ihre
Empfängeradresse? Treffer → Status `sent`, mit echtem Datum und Gesprächsfaden-
Kennung (die brauchen wir für spätere Antworten).

**Sie muss nichts abhaken.** Das ist die Zusage aus `docs/00-vision.md`.

Dabei zwei Dinge beobachten und in `memory/textwissen.md` festhalten:

- **Wie lange lag die Karte, bevor sie sie abgeschickt hat?** Lange Liegezeit heißt:
  Text zu lang, Stelle nicht überzeugend, oder zu viele Karten auf einmal
- **Hat sie den Text verändert?** Die gesendete Fassung mit der vorbereiteten
  vergleichen. Jede Abweichung ist ein Hinweis, dass dem Stilprofil etwas fehlt –
  wertvoller als jede Rückfrage, weil ehrlicher

## Schritt 2 · Neue Antworten

```
python scripts/gmail_fetch.py --incremental
```

Zuordnen in dieser Reihenfolge: Gesprächsfaden-Kennung → Absenderdomain gegen
bekannte Firmendomains → Betreff-Ähnlichkeit. Nichts davon greift → mit
Kandidatenliste beurteilen (**U10**).

Einordnen in: Eingangsbestätigung, Absage, Einladung, Rückfrage, Angebot, sonstiges.
Unsicher (unter 0,7) → `needs_human`, Karte fragt Paula.

## Schritt 3 · Reagieren

| Fall | Was passiert |
|---|---|
| **Eingangsbestätigung** | Nur Status. Keine Meldung – sie soll nicht für jede Automatik-Mail eine Karte bekommen |
| **Absage** | Status, Dankestext vorbereiten (**U11**), Karte in Block 3 |
| **Einladung** | **Block 0, sofort.** Terminvorschläge herausziehen. Kein Termin wird zugesagt – sie wählt, dann wird der Text fertiggestellt |
| **Rückfrage** | Antwort so weit vorbereiten, wie der Faktenblock reicht. Alles andere bleibt als sichtbare Lücke stehen. Lieber unfertig als erfunden |
| **Angebot** | Nur Meldung, kein Text. Das bespricht sie selbst |
| **Unklar** | Karte mit Auszug und der Frage, worum es geht |

U9 läuft auch für diese Texte.

## Schritt 4 · Verlaufene Bewerbungen

Gesendet vor mehr als 42 Tagen ohne Antwort → `no_reply`, Nachfass-Vorschlag in
Block 2. Ohne Aktivität seit 90 Tagen → `closed`.

## Schritt 5 · Streifzug

Was sagen die Antworten über den Markt?

- Kommen aus bestimmten Branchen nie Antworten?
- Gibt es Muster im Wortlaut von Absagen, die auf etwas Behebbares hindeuten?
  („Wir suchen jemanden mit X" dreimal → fehlt etwas im Profil oder im Text?)
- Ist die Antwortquote seit einer Änderung gestiegen oder gefallen?
- Wie lange dauert es im Schnitt bis zur Antwort? Das bestimmt, wann Nachfassen sinnvoll ist

Ergebnis nach `memory/marktwissen.md` bzw. `memory/textwissen.md`.

## Schritt 6 · Gedächtnis und Abschluss

Wie in `daily-jobs.md`, Schritte 9 und 10.

**Besonders wichtig hier:** Antwortquoten sind die einzige harte Rückmeldung, die
das System je bekommt. Sie gehören gepflegt, sobald genug Daten da sind (ab etwa
zwanzig gesendeten Bewerbungen).
