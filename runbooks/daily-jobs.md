# Täglicher Lauf: Stellen finden und Bewerbungen vorbereiten

Läuft dreimal täglich. Dauer 10–25 Minuten. Das ist der Lauf, der am häufigsten
stattfindet – hier entscheidet sich, ob das System etwas taugt.

## Voraussetzungen

- `state/phase.current_phase` ist 2 oder höher (Profil ist bestätigt)
- `profile/facts`, `profile/style`, `profile/search` haben `confirmed_by_user_at`
- `state/consent` ist gesetzt
- Nicht pausiert (`state/phase.paused`)

Fehlt eines davon: Lauf beenden, Grund in `events`, keine Fehlermeldung an Paula.

---

## Schritt 0 · Gedächtnis laden

Lies **vor allem anderen**:

- `memory/LERNTAGEBUCH.md` – die letzten fünf Einträge
- `memory/suchstrategie.md` – vollständig
- `memory/offene-faeden.md` – für den Streifzug am Ende
- `memory/experimente.md` – läuft gerade eines? Dann Regeln einhalten

Das ist kein Ritual. Ohne diesen Schritt wiederholt dieser Lauf die Fehler des
letzten.

## Schritt 1 · Stellen holen

```
python scripts/jobs_fetch.py --since-last-run
```

Holt aus allen aktiven Quellen. Eine Quelle, die ausfällt, hält den Lauf nicht auf –
Fehler protokollieren, weitermachen. Dritter Ausfall in Folge: Quelle abschalten,
Alexander verständigen, Eintrag in `memory/marktwissen.md`.

Ergebnis notieren: Wie viele Stellen je Quelle? Auffällig wenige oder viele ist
selbst eine Information.

## Schritt 2 · Bekanntes aussortieren

```
python scripts/dedup.py --incoming
```

Entfernt **nur Hartes**:

- Fingerabdruck schon in der Datenbank → dieselbe Stelle aus einer anderen Quelle
- Firma gesperrt
- Sperrfrist läuft (180 Tage, gilt nicht für Personalvermittler)
- Auf diese Stelle schon beworben
- Offene Bewerbung bei dieser Firma

**Was hier nicht passiert:** kein Filter nach Titel, Ausschlusswörtern oder
Entfernung. Das lese ich selbst. Ein Titel, den kein Suchbegriff trifft, kann genau
passen; „Nachtschicht" im Fließtext kann sich auf einen anderen Bereich beziehen.
Der Grund steht in `docs/14-arbeitsweise.md`.

## Schritt 3 · Lesen und beurteilen

Jede verbliebene Stelle gegen Faktenblock und Suchprofil (**U6**,
`docs/03-llm-tasks.md`). Ergebnis pro Stelle: Punktwert, zwei Sätze Begründung für
Paula, Bedenken, harte Ausschlussgründe, Aufhänger.

Dabei mitlaufen lassen – das ist der Unterschied zwischen Abarbeiten und Hinschauen:

- **Fehlt ein Suchbegriff?** Eine gute Stelle, die nur zufällig gefunden wurde, heißt:
  ein Begriff fehlt. → `memory/suchstrategie.md`, Abschnitt „Zu probieren"
- **Firmensignal ablegen.** Auch Stellen, die für Paula nicht passen, sagen etwas
  über die Firma: Sie stellt ein. Signal bei der Firma vermerken (S1 in
  `docs/13-initiativbewerbungen.md`). Kostet nichts und ist die Grundlage für M7
- **Läuft das Inserat lange?** Schon einmal gesehen, immer noch offen → Signal S3
- **Neue Branche?** Ein Arbeitgebertyp, an den ich nicht gedacht hatte →
  `memory/marktwissen.md`

## Schritt 4 · Firmen recherchieren

Für Stellen über dem Schwellwert, deren Firma unbekannt oder länger als 180 Tage
nicht angesehen ist: **U7**. Websuche und Seitenabruf, sparsam.

Kein Bewerbungskontakt auffindbar → Firma auf `no_contact`, Karte zeigt später den
Link zum Bewerbungsformular. Unter zehn Mitarbeitenden und Telefonnummer vorhanden
→ Telefonvariante vormerken (siehe Schritt 6).

## Schritt 5 · Schreiben

Für jede Stelle über dem Schwellwert, bis zum Tageslimit: **U8** Brief, **U9**
Faktenprüfung.

U9 meldet einen schweren Verstoß → **einmal** neu schreiben, mit den
Beanstandungen als Vorgabe. Wieder → Bewerbung auf `blocked`, Paula sieht sie
nicht, Eintrag für den Bericht an Alexander.

## Schritt 6 · Schlussdurchsicht

**Der wichtigste Schritt. Kein Skript kann ihn ersetzen.**

Jeden Brief noch einmal ganz lesen und eine Frage beantworten:

> **Würde ich das so abschicken?**

Nicht: Ist alles belegt (das war U9). Sondern: Klingt das nach einem Menschen, der
diese Stelle will? Ist der Bezug zur Firma echt oder aufgesetzt? Steht irgendwo ein
Satz, der unterwürfig, aufgeblasen oder nichtssagend ist? Würde ein Personalverant-
wortlicher nach zwei Zeilen weiterlesen?

Nein → neu schreiben. Ohne Runden zu zählen.

Hier auch die **Kartenvariante** festlegen:

| Lage | Variante |
|---|---|
| Bewerbungsadresse vorhanden | Normale Karte mit Mailtext |
| Nur Bewerbungsformular | Karte mit Text zum Kopieren **und** Link zum Formular |
| Betrieb unter ~10 Mitarbeitenden, Telefonnummer bekannt | **Telefonvariante:** Nummer, beste Anrufzeit, drei Sätze Gesprächseinstieg, und darunter der Mailtext als Rückfallebene |
| Ring 3 (weit weg) | Normale Karte, aber mit Entfernungshinweis und der Frage, ob ein Umzug in Frage käme |

## Schritt 7 · Karten anlegen

Bewerbungen auf `ready`, ab in die Datenbank, sortiert nach Punktwert. Tageslimit
aus `config/settings.yaml` (`grenzen.karten_pro_tag`). Der Rest bleibt bewertet
liegen und kommt beim nächsten Lauf dran.

**Ausnahme vom Limit:** Eine außergewöhnlich gute Stelle wartet nicht bis morgen.

## Schritt 8 · Streifzug

*Zehn bis fünfzehn Minuten, ohne Vorgabe.*

Sieh zuerst in `memory/offene-faeden.md`. Sonst: Was ist dir heute aufgefallen?

Beispiele, keine Liste zum Abarbeiten:

- Eine Firma, die in drei Wochen fünf verschiedene Stellen ausgeschrieben hat –
  was ist da los?
- Eine Formulierung, die dir in mehreren Absagen begegnet ist
- Eine Stelle, die formal nicht passt und die du trotzdem interessant fandest –
  warum? Fehlt dem Suchprofil etwas?
- Eine Quelle, die du nie ausprobiert hast
- Eine Region, aus der auffällig wenig kommt – liegt es an der Region oder an den
  Begriffen?
- Ein Signaltyp für Initiativbewerbungen, der im Plan nicht steht

**Schreib das Ergebnis auf, auch wenn nichts dabei herauskam.** „Nachgesehen,
nichts Auffälliges" ist ein gültiges Ergebnis und verhindert, dass dieselbe Spur
dreimal verfolgt wird.

## Schritt 9 · Gedächtnis fortschreiben

- Gab es etwas zu lernen → Eintrag in `memory/LERNTAGEBUCH.md`
- Neue Suchbegriffe → `memory/suchstrategie.md`
- Zahlen zu Quellen → `memory/marktwissen.md`
- Streifzug-Ergebnis → wohin es gehört
- Erledigte Fäden abhaken, neue eintragen

Dann committen. Eine Zeile, was dieser Lauf gelernt hat.

## Schritt 10 · Abschluss

`events` mit Zusammenfassung: geholt, aussortiert, beurteilt, geschrieben, Karten,
Fehler, Dauer. `state/sources` und `state/counters` aktualisieren.

Alexander verständigen, wenn: Lauf abgebrochen, über ein Fünftel Fehler, Quelle
abgeschaltet, zweimal Faktenprüfung gescheitert, seit zehn Tagen wartende Karten
ohne dass Paula etwas abgeschickt hat.

---

## Grenzen dieses Laufs

- Verschickt nichts. Es gibt keinen Weg dazu
- Ändert `profile/facts` und `profile/style` nicht – nur Paula über das Dashboard
- Schreibt keine Initiativbewerbungen (das macht `spontaneous.md`), sammelt aber
  die Signale dafür ein
- Bricht nach 45 Minuten ab und meldet sich
