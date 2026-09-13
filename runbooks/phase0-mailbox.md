# Einmalig: Mailbox-Archäologie

Der Grundstein. Läuft nicht als Routine, sondern von Hand, in mehreren Abschnitten,
mit Alexander in Reichweite. Kann je nach Mailboxgröße Stunden dauern.

> **Nur lesen.** Der Gmail-Zugriff kann technisch nichts anderes.

## Voraussetzungen

`state/consent` gesetzt · Anmeldung erfolgt · `scripts/gmail_fetch.py --list --months 1`
liefert plausible Ausgaben

## Durchgang 1 · Breit und flach

```
python scripts/gmail_fetch.py --list --months 36 --format metadata
```

`metadata` überträgt **nur** Absender, Betreff, Datum und Anhangsnamen. Der Inhalt
verlässt Googles Server nicht. Das ist die technische Umsetzung der Auflage
„ansonsten ihre E-Mails in Ruhe lassen".

**U1** je Mail: bewerbungsbezogen, ja oder nein.

- Anhänge wie `Lebenslauf*`, `CV*`, `Bewerbung*`, `Motivationsschreiben*` in einer
  **gesendeten** Mail → fast sicher ja
- Job-Alerts von Portalen → nein, aber als Stellenquelle vermerken
- Newsletter, Rechnungen, Privates → nein, nur Kennnummer nach `seen`

Im Zweifel **ja** – Durchgang 2 korrigiert. Eine übersehene Bewerbung bedeutet ein
Risiko für Doppelbewerbung; eine zu viel geprüfte Mail kostet nur Zeit.

In Abschnitten arbeiten, Fortschritt in `state/gmail.initial_scan_cursor`.

## Durchgang 2 · Tief und schmal

Nur die Treffer: Volltext plus Anhänge.

```
python scripts/gmail_fetch.py --fetch <ids> --with-attachments
```

**U2** je Mail: Art, Firma, Stelle, Datum, Anhänge.

Aus **gesendeten** Bewerbungen: an wen, worauf, wann, welche Dateien, welcher Text.
Aus **empfangenen**: was daraus wurde.

Alle Lebenslauf- und Zeugnisdateien in die Dateiablage des Dashboards, verzeichnet
in `profile/documents`.

## Durchgang 3 · Historie bauen

Gesendete Bewerbung → `applications` mit `kind: historical`. Spätere Mails im selben
Gesprächsfaden oder von derselben Domain → Status fortschreiben. Firmen anlegen und
zusammenführen (fünfstufiges Verfahren aus `docs/02-data-model.md`).

Sicherheit ausweisen: Zuordnung nur über Domain und Zeitfenster → niedrigere
Sicherheit, später Warnhinweis auf der Karte.

## Durchgang 4 · Bericht

Tabelle: Firma, Stelle, wann beworben, was kam zurück, wie sicher. Als Markdown und
CSV. Alexander geht sie mit Paula durch; Falsches wird korrigiert.

## Streifzug

Dieser Lauf ist der informationsreichste des ganzen Projekts. Hier lohnt sich mehr
Zeit als sonst:

- **In welchem Rhythmus hat sie sich beworben?** Schübe oder gleichmäßig? Das sagt
  etwas darüber, wie das Werkzeug ihr helfen kann
- **Worauf kam Antwort, worauf nicht?** Die erste belastbare Grundlinie
- **Wie haben sich ihre Bewerbungen über die Zeit verändert?** Wurden die Texte
  kürzer, sicherer, verzweifelter?
- **Welche Arbeitgebertypen hat sie angeschrieben?** Und welche auffällig nicht?
- **Gibt es Stellen, auf die sie sich beworben hat, die du ihr nie vorgeschlagen
  hättest?** Dann ist das Suchprofil zu eng gedacht
- **Wie lange lagen Absagen unbeantwortet?** Sagt etwas über ihre Belastung

Alles nach `memory/LERNTAGEBUCH.md`, erster Eintrag – das ist die Grundlinie, an der
sich alles Spätere messen lässt.

## Grenzen

- Keine Mail ohne Bewerbungsbezug wird gelesen oder gespeichert
- Keine Anhänge aus fremden Mails – nur aus ihren eigenen gesendeten Bewerbungen
- Nichts wird verschickt, nichts in Gmail verändert (technisch ausgeschlossen)
