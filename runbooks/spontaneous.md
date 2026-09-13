# Nachtlauf: Initiativbewerbungen

Läuft nachts, einmal täglich, 20–40 Minuten. Grundlage:
[`docs/13-initiativbewerbungen.md`](../docs/13-initiativbewerbungen.md).

> **Die eiserne Regel: kein Signal, kein Brief.** Eine Firma wird nur angeschrieben,
> wenn sich ein Satz formulieren lässt, der ausschließlich auf sie zutrifft.

## Schritt 0 · Gedächtnis

`memory/marktwissen.md`, Abschnitt Signale – welches trägt, welches nicht? Ein
Signal, das nach zwanzig Briefen keine Antwort gebracht hat, wird heruntergestuft.

## Schritt 1 · Signale einsammeln

| Signal | Woher |
|---|---|
| **S2 Öffentlicher Auftrag** | `scripts/sources/vergaben.py` – CSV von gestern, Zuschläge in Paulas Region. Auftragnehmer über die Firmenbuchnummer eindeutig zuordnen |
| **S4 Firmenbuch-Bewegung** | Neueintragungen und Änderungen von gestern |
| **S5 Wachstumsnachricht** | 3–5 Websuchen, nach Bezirk und Branche abwechselnd. Suchmuster in `docs/13`, S5. Nicht jede Nacht dieselben |
| **S1 / S3 / S6** | Aus dem Inseratsstrom – wurde von `daily-jobs.md` schon abgelegt |
| **S9 Alte Kontakte** | Wöchentlich: Firmen, bei denen sie weit kam, letzter Kontakt über 6 Monate her |
| **S7 AMS-Regionaldaten** | Monatlich |

Jedes Signal bekommt Datum und Quelle. Älter als 90 Tage → verfällt.

## Schritt 2 · Neu bewerten

Alle Firmen mit mindestens einem gültigen Signal:

```
Rang = Signalstärke × Nähe × Passung der Größe × Frische
```

Nähe nach Ringen (Paula ist umzugsbereit, also ist Ring 3 aktiv, aber mit höherer
Hürde). Größe: unter ~10 Mitarbeitenden selten eigener Bürobedarf, über ~200 meist
eine Personalabteilung mit eigenem Verfahren – der Bereich dazwischen ist der
ergiebigste.

## Schritt 3 · Die zehn stärksten recherchieren

**U7** für jede: Was machen sie, wie schreiben sie, Karriereseite, Bewerbungskontakt,
ob Initiativbewerbungen erwähnt werden.

Adresse nur von der Firmenwebsite, Domain muss passen. Nichts gefunden →
`no_contact`, Firma bleibt mit Signal liegen (vielleicht findet sich später etwas).

## Schritt 4 · Den Aufhänger formulieren – oder abbrechen

Für jede recherchierte Firma **einen Satz** schreiben, der nur auf sie zutrifft und
der belegt ist.

Prüfen:
- Stimmt er nachweislich? (Quelle muss benennbar sein, falls die Firma zurückfragt)
- Ist er öffentlich bekannt? (Auftrag, Zeitungsartikel, eigene Website – ja.
  Etwas über eine einzelne **Person** – nein, niemals)
- Würde ihn ein Mensch als aufmerksam empfinden, nicht als unheimlich?

**Geht das nicht: keine Bewerbung.** Firma bleibt liegen, kein Ersatz durch
allgemeine Formulierungen. Das ist der Punkt, an dem dieses System sich von
Massenversand unterscheidet, und er wird nicht aufgeweicht, wenn die Woche mager war.

## Schritt 5 · Schreiben und prüfen

**U8** Variante „Initiativ": 120–180 Wörter, Aufhänger im **ersten** Satz, ein
Angebot statt einer Bitte. Dann **U9**.

Zusätzlich: Ähnlichkeit zu den letzten zwanzig Texten unter 0,7. Darüber → neu
schreiben. Serienbriefe erkennt jeder.

## Schritt 6 · Schlussdurchsicht

> **Würde ich diesen Brief so an diese Firma schicken?**

Besonders: Wirkt der Aufhänger aufmerksam oder aufdringlich? Bei Zweifel weglassen
und die Firma zurückstellen.

Kartenvariante festlegen (wie in `daily-jobs.md`, Schritt 6) – bei kleinen Betrieben
die **Telefonvariante**, die hier oft die bessere ist.

## Schritt 7 · Karten

Höchstens fünf Initiativbewerbungen pro Woche, höchstens zwei pro Nacht. Lieber
weniger. Der Engpass ist nicht die Technik, sondern wie viele gute Briefe entstehen
und wie viele Paula tatsächlich abschickt.

## Schritt 8 · Firmenbasis erweitern

Ein- bis zweimal pro Woche einen neuen Bezirk über OpenStreetMap holen
(`scripts/companies/osm.py`). Die Liste darf tausende Einträge haben – angeschrieben
wird nur, wo ein Signal ist.

## Schritt 9 · Streifzug

Hier ist der Streifzug am ergiebigsten, weil das Gebiet am wenigsten erschlossen ist:

- **Gibt es ein zehntes Signal?** Etwas, das Einstellungsbedarf verrät und im Plan
  nicht steht. Öffentliche Förderzusagen? Baubewilligungen? Messeauftritte?
  Insolvenz eines Mitbewerbers, dessen Arbeit irgendwohin muss?
- **Welches Signal trägt wirklich?** Zahlen in `memory/marktwissen.md` nachtragen
- **Eine Firma, die dir mehrfach begegnet ist**, ohne dass ein Signal griff – warum?
- **Eine Datenquelle, die du noch nie angesehen hast**

Neue Signalideen kommen als Experiment nach `memory/experimente.md` – mit Hypothese,
bevor sie angewendet werden.

## Schritt 10 · Gedächtnis und Abschluss

Wie in `daily-jobs.md`.

---

## Grenzen

- Verschickt nichts
- Keine Signale über Personen. Nur über Firmen, nur aus öffentlich Bekanntem
- Keine Bewerbung ohne belegten Aufhänger
- Keine Firma, die als gesperrt oder `accepts_spontaneous: no` vermerkt ist
- Bricht nach 60 Minuten ab
