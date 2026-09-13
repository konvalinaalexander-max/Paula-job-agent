# 10 – Das Dashboard

> **Version 2.** Ersetzt das frühere Telegram-Konzept vollständig. Dies ist die einzige Oberfläche, die Paula je sieht.

## Haltung

Paula sucht dringend Arbeit. Das Dashboard ist damit kein Werkzeug, das sie bedienen lernt, sondern eine Seite, die ihr **Arbeit abnimmt**. Jede Entscheidung der Gestaltung folgt daraus:

- **Öffnen, sehen, handeln.** Kein Login-Dialog mit Erklärtext, keine Tour, keine Einstellungen im Weg. Oben steht, was heute zu tun ist.
- **Eine Bewerbung = eine Karte = drei Klicks.** Text kopieren, Lebenslauf laden, als gesendet markieren – und selbst das dritte erkennt das System meistens von allein.
- **Ruhe.** Viel Weißraum, eine Akzentfarbe, keine Fortschrittsbalken, keine Konfetti, keine Zahlen, die niemand braucht. Ein Bewerbungsprozess ist anstrengend genug.
- **Keine Technik.** Nirgends "Score", "KI", "Modell", "Pipeline", "Datenbank". Statt „Score 78" steht „Passt gut".
- **Nichts blinkt, nichts drängt.** Ausnahme: eine Einladung zum Gespräch. Die darf auffallen.

## Aufbau: fünf Blöcke, von oben nach unten

```
┌─────────────────────────────────────────────────────────────┐
│  Guten Morgen, Paula                     Stand: heute 07:32 │
│  3 bereit zum Senden · 7 unterwegs · 1 Einladung            │
└─────────────────────────────────────────────────────────────┘

╔═════════════════════════════════════════════════════════════╗
║  ⬥ BRAUCHT DICH JETZT                            (1)        ║   Block 0
║  Nur sichtbar, wenn es etwas gibt. Einladungen,             ║   erscheint nur
║  Rückfragen, Zusagen. Hervorgehoben.                        ║   bei Bedarf
╚═════════════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────────────┐
│  BEREIT ZUM SENDEN                                   (3)    │   Block 1
│  Alles vorbereitet. Du musst nur noch abschicken.           │
│  ▸ Karte · ▸ Karte · ▸ Karte                                │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  UNTERWEGS                                           (7)    │   Block 2
│  Abgeschickt, warten auf Antwort.                           │
│  Kompakte Zeilen, kein Handlungsbedarf.                     │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  ABSAGEN – KURZE ANTWORT LIEGT BEREIT                (2)    │   Block 3
│  Zwei Sätze Danke. Kostet dich 20 Sekunden.                 │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  ▸ Erledigt (23)                                            │   Block 4
│  Eingeklappt. Zum Nachschlagen.                             │
└─────────────────────────────────────────────────────────────┘
```

Fünf statt der vorgeschlagenen vier: Block 0 ist neu. Eine Einladung zum Gespräch ist das Wichtigste, was in diesem ganzen System passieren kann – die darf nicht zwischen Vorschlägen untergehen. Er ist leer und unsichtbar, solange nichts ansteht.

## Block 1 im Detail – die Bewerbungskarte

Eingeklappt (Standard, alle Karten):

```
┌──────────────────────────────────────────────────────────────┐
│  Projektassistenz (Teilzeit 30h)              Passt gut      │
│  Muster GmbH · 1030 Wien · seit gestern online               │
│                                                              │
│  Du hast drei Jahre Assistenzerfahrung im Bau, genau das     │
│  verlangt die Stelle. Wien ist in deinem Radius.             │
│                                                              │
│  ⚠ Sie wünschen Französisch B2 – in deinem Lebenslauf B1.    │
│                                                              │
│  [ Bewerbung ansehen ]        [ Inserat ]     [ Nein danke ] │
└──────────────────────────────────────────────────────────────┘
```

Ausgeklappt:

```
│  An:      bewerbung@muster.at                    [ kopieren ]│
│  Betreff: Bewerbung als Projektassistentin       [ kopieren ]│
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Sehr geehrte Frau Muster,                              │  │
│  │                                                        │  │
│  │ … der vollständige Text, so wie er abgeschickt wird …  │  │
│  │                                                        │  │
│  │ Mit freundlichen Grüßen                                │  │
│  │ Paula …                                                │  │
│  └────────────────────────────────────────────────────────┘  │
│                                     [ Ganzen Text kopieren ] │
│                                                              │
│  Anhängen:  📎 Lebenslauf_Paula_2025-11.pdf    [ laden ]     │
│             📎 Zeugnisse.pdf                   [ laden ]     │
│                                                              │
│  [ In Gmail öffnen ]   [ Text ändern ]   [ Hab ich geschickt ]│
└──────────────────────────────────────────────────────────────┘
```

**„In Gmail öffnen"** ist der eigentliche Trick: Ein Link der Form `https://mail.google.com/mail/?view=cm&to=…&su=…&body=…` öffnet in Paulas Gmail ein neues Fenster mit **bereits ausgefülltem** Empfänger, Betreff und Text. Sie muss nur noch den Lebenslauf anhängen und auf Senden drücken. Aus drei Klicks werden zwei.

*(Einschränkung: Die Länge solcher Links ist begrenzt. Wenn der Text zu lang wird, fällt die Karte auf „Text kopieren" zurück und sagt das auch. Muss in M3 an einem echten langen Text geprüft werden.)*

**„Hab ich geschickt"** ist freiwillig. Normalerweise erkennt das System den Versand beim nächsten Lauf selbst (es findet die Mail im Gesendet-Ordner) und schiebt die Karte von allein in Block 2. Der Knopf ist für den Fall, dass sie über ein anderes Konto oder per Post gesendet hat.

**„Text ändern"** öffnet ein Feld: *„Was soll anders sein?"* Sie schreibt frei hinein („kürzer", „weniger steif", „erwähn meine Zeit bei Firma X"). Das wird gespeichert; beim nächsten Lauf schreibt Claude den Text neu, und die Karte trägt dann den Hinweis „Neue Fassung – geändert: kürzer, lockerer". Bis dahin bleibt der alte Text sichtbar und benutzbar.

> Wenn ihr Änderungswunsch einen **neuen Fakt** enthält („ich war zwei Jahre in Wien"), der nicht im Faktenblock steht, wird er **nicht** in den Text übernommen. Stattdessen erscheint auf der Karte: *„Das steht nicht in deinen Unterlagen. Soll ich es dauerhaft aufnehmen?"* mit Ja/Nein. Bei Ja wandert es in `profile/facts` – und ist ab dann für alle künftigen Bewerbungen verfügbar.

**„Nein danke"** verwirft. Beim zweiten Mal für dieselbe Firma fragt die Karte: *„Muster GmbH in Zukunft ganz weglassen?"*

## Block 0 – die dringenden Fälle

### Einladung

```
╔══════════════════════════════════════════════════════════════╗
║  Muster GmbH lädt dich ein.                                  ║
║  Projektassistenz · beworben am 3. September                 ║
║                                                              ║
║  Vorgeschlagen:   Di 16. Sept, 14:00   ·   Do 18. Sept, 10:00║
║  Vor Ort: Ungargasse 12, 1030 Wien                           ║
║  Kontakt: Frau Beispiel, 01 234 56 78                        ║
║                                                              ║
║  Welcher Termin passt?  [ Di 14:00 ] [ Do 10:00 ] [ anderer ]║
║                                                              ║
║  ▸ Ganze Mail lesen                                          ║
╚══════════════════════════════════════════════════════════════╝
```

Nach der Terminwahl wird daraus eine normale Karte mit fertigem Zusagetext zum Kopieren. **Das System schlägt nie selbst einen Termin vor und sagt nie selbst zu.**

### Rückfrage

Wie eine Bewerbungskarte, aber die Antwort ist teilweise ausgefüllt. Fragen, die der Faktenblock nicht beantwortet, stehen als Lücke im Text:

```
│ … meine Verfügbarkeit ist ab 1. Oktober.                     │
│                                                              │
│ ▸▸ SAP-Erfahrung: das steht nicht in deinen Unterlagen.      │
│    Schreib kurz, was stimmt: [_________________]             │
│                                                              │
│ [ Text vervollständigen ]                                    │
```

Erst wenn die Lücken gefüllt sind, gibt es „Text kopieren". Lieber eine unfertige Antwort als eine erfundene.

### Zusage

```
║  🎉  Muster GmbH bietet dir die Stelle an.                    ║
║  Das besprichst du besser selbst – ich halte mich raus.       ║
║  ▸ Ganze Mail lesen          [ Als abgeschlossen markieren ] ║
```

## Block 2 – Unterwegs

Kompakte Zeilen, sortiert nach Datum. Kein Handlungsbedarf, nur Überblick.

```
  Muster GmbH        Projektassistenz       gesendet 3. Sept   ✓ bestätigt
  Beispiel AG        Sachbearbeitung        gesendet 5. Sept   – still
  Test OG            Assistenz Leitung      gesendet 8. Sept   – still
```

Nach sechs Wochen Funkstille: *„Bei Muster GmbH ist es 6 Wochen her. Nachfragen? [Text vorbereiten]"*

## Block 3 – Absagen mit vorbereitetem Dank

```
┌──────────────────────────────────────────────────────────────┐
│  Beispiel AG hat abgesagt.            Sachbearbeitung        │
│  „…haben wir uns für eine andere Bewerberin entschieden…"     │
│                                                              │
│  Deine Antwort ist fertig:                                   │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Sehr geehrte Frau …, vielen Dank für Ihre Rückmeldung  │  │
│  │ und die Mühe … Ich wünsche Ihnen …                     │  │
│  └────────────────────────────────────────────────────────┘  │
│  [ In Gmail antworten ]  [ kopieren ]  [ Nicht antworten ]   │
└──────────────────────────────────────────────────────────────┘
```

Nach dem Senden (wieder automatisch erkannt) wandert die Karte nach Block 4.

## Block 4 – Erledigt

Eingeklappt. Ausgeklappt eine schlichte Tabelle: Firma, Stelle, gesendet, Ergebnis. Darunter eine einzige Zeile Statistik:

> *Seit Beginn: 23 Bewerbungen · 4 Einladungen · Antwortquote 39 %*

Keine Diagramme. Keine Trends.

## Der Profil-Bereich (Phase 1 und danach)

Über einen unauffälligen Link **„Meine Unterlagen"** erreichbar, in Phase 1 aber als erste Seite angezeigt:

```
┌──────────────────────────────────────────────────────────────┐
│  Ich habe deine bisherigen Bewerbungen durchgesehen.          │
│  Bitte schau einmal drüber, ob das stimmt:                    │
│                                                              │
│  BERUFSERFAHRUNG                                             │
│  Assistentin der Bauleitung · Bau GmbH · 03/2019 – 11/2024   │
│    ✓ stand in 12 von 15 deiner Lebensläufe            [ok]   │
│                                                              │
│  Sachbearbeiterin · Handels OG · 2017 – 2019                 │
│    ⚠ In einem Lebenslauf steht 2018 als Beginn.              │
│      Was stimmt?   [ 2017 ]  [ 2018 ]  [ anders: ____ ]      │
│                                                              │
│  SPRACHEN                                                     │
│  Deutsch (Muttersprache), Englisch (B2), Französisch (B1)     │
│    ✓ übereinstimmend                                  [ok]   │
│                                                              │
│  …                                                           │
│                                                              │
│  [ Passt alles – los geht's ]                                │
└──────────────────────────────────────────────────────────────┘
```

Genauso für das Stilprofil (*„So klingst du in deinen Bewerbungen – stimmt das?"* mit drei Beispielabsätzen aus ihren eigenen Texten) und das Suchprofil (*„Danach würde ich suchen"*).

Das ist der Moment, in dem das System sein Vertrauen verdient oder verliert. Es muss zeigen, dass es sie **gelesen** hat, nicht dass es klug ist.

## Gestaltung

| | |
|---|---|
| Schrift | Eine serifenlose Systemschrift. Fließtext 16px, großzügige Zeilenhöhe |
| Farbe | Warmes Off-White als Grund, sehr dunkles Grau für Text, **eine** ruhige Akzentfarbe (gedecktes Blaugrün) für Aktionen. Rot ausschließlich für Fehler, nie für Absagen |
| Karten | Weiß, weicher Rahmen, sehr dezenter Schatten, großzügig gepolstert |
| Knöpfe | Ein gefüllter Hauptknopf pro Karte, Rest als Textlink. Nie zwei gleich laute Knöpfe nebeneinander |
| Dichte | Lieber scrollen als drängen |
| Dunkelmodus | Ja, automatisch nach Systemeinstellung |
| Handy | Vollwertig – Paula liest das unterwegs. Karten stapeln sich, „kopieren" funktioniert |
| Bewegung | Nur das Aufklappen. Sonst nichts |

## Was Paula nie sieht

Zahlenwerte von Bewertungen, Modellnamen, Kosten, Fehlermeldungen, verworfene Kandidaten unterhalb der Schwelle, Rohdaten der Firmenrecherche, das Wort „KI".

## Was der Betreiber zusätzlich sieht

Am Seitenende, nur für ihn sichtbar: letzter Lauf, Anzahl geprüfter Inserate, Fehler, Warnungen. Alles Weitere macht er in der Claude-Session.
