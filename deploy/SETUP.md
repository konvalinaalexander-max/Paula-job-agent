# Paulas Mailbox verbinden

Das ist der erste praktische Schritt. Danach kann das System lesen, was es braucht,
und alles Weitere baut darauf auf.

**Zeitaufwand:** 10 Minuten für Paula, 5 Minuten für dich.
**Was Paula dabei tun muss:** zwei Einstellungen in ihrem Google-Konto. Nichts installieren.

---

## Vorab: Warum dieser Weg und nicht der andere

Es gibt zwei Möglichkeiten, an eine Gmail-Mailbox heranzukommen. Ich habe beide
geprüft, und die naheliegendere ist die schlechtere:

| | **App-Passwort** (dieser Weg) | Google-Cloud-Projekt (OAuth) |
|---|---|---|
| Aufwand für dich | 5 Minuten | 45 Minuten in der Google-Konsole |
| Aufwand für Paula | 2 Einstellungen | Anmeldung mit Warnbildschirm „nicht überprüfte App" |
| **Hält es?** | **Ja, dauerhaft** | **Vermutlich nicht** – siehe unten |
| Rückzug möglich | Jederzeit, ein Klick | Jederzeit |

**Das Problem mit dem Cloud-Weg:** Der Zugriff auf Gmail-Inhalte gilt bei Google als
besonders heikel. Solange eine App nicht überprüft ist, verfällt die Berechtigung nach
**7 Tagen** – Paula müsste sich wöchentlich neu anmelden. Eine Überprüfung verlangt ein
Sicherheitsaudit durch einen externen Prüfer; das kostet Geld und Monate und ist für ein
Projekt mit einer einzigen Nutzerin absurd.

Deshalb: App-Passwort. Es funktioniert, es läuft nicht ab, und für Paula ist es
einfacher.

**Der eine Nachteil, den du kennen solltest:** Ein App-Passwort ist technisch ein
Vollzugriff auf die Mailbox – anders als beim Cloud-Weg, wo man ein reines Leserecht
vergeben kann. Das System nutzt es ausschließlich zum Lesen; es gibt im gesamten Code
keinen Versandweg, und `scripts/mail.py` enthält nachweislich kein einziges Wort
„SMTP". Aber die Beschränkung ist hier eine Selbstverpflichtung, keine technische
Sperre. Das gehört in das Gespräch mit Paula.

---

## Schritt 1 · Paula: Zwei-Faktor-Anmeldung einschalten

*Ohne diese gibt es keine App-Passwörter. Wenn sie schon aktiv ist, weiter zu Schritt 2.*

1. [myaccount.google.com/security](https://myaccount.google.com/security) öffnen
2. **„Bestätigung in zwei Schritten"** anklicken
3. Dem Ablauf folgen – üblicherweise Handynummer bestätigen
4. Fertig

## Schritt 2 · Paula: App-Passwort erzeugen

1. [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords) öffnen
   *(Wenn die Seite nicht erscheint: Zwei-Faktor-Anmeldung ist noch nicht aktiv →
   zurück zu Schritt 1.)*
2. Als Namen eingeben: **Bewerbungshilfe**
3. Auf **Erstellen** klicken
4. Es erscheint ein **16-stelliges Passwort in vier Blöcken**, etwa `abcd efgh ijkl mnop`
5. **Dieses Passwort kopieren und dir schicken** – über einen Weg, der nicht die Mailbox
   selbst ist (Signal, WhatsApp, Zettel). Es wird nur einmal angezeigt.

> **Das ist kein Passwort für ihr Konto.** Es öffnet nur diesen einen Zugang, und sie
> kann ihn auf derselben Seite jederzeit wieder löschen. Ihr Hauptpasswort bleibt
> geheim und ändert sich nicht.

## Schritt 3 · Du: Die Zugangsdaten hinterlegen

Die beiden Werte kommen als **Umgebungsvariablen** in die Umgebung, in der ich
arbeite – nicht in eine Datei, nicht in eine Nachricht, nicht ins Repository.

| Name | Wert |
|---|---|
| `PAULA_IMAP_USER` | Paulas vollständige Mailadresse |
| `PAULA_IMAP_PASSWORD` | Das 16-stellige App-Passwort (Leerzeichen dürfen drin bleiben) |

In **Claude Code im Web**: Einstellungen der Umgebung → Umgebungsvariablen → beide
anlegen. Wenn du die Stelle nicht findest, sag Bescheid – ich schaue nach, wo sie in
deiner Einrichtung liegt.

## Schritt 4 · Probe

Sag mir Bescheid, sobald die beiden Werte gesetzt sind. Ich führe dann aus:

```
python3 scripts/mail.py pruefen
```

Das meldet zurück: ob die Verbindung steht, wie die Ordner heißen, wie viele Mails im
Posteingang liegen und wie viele davon in den letzten 30 Tagen nach Bewerbung aussehen.

**Es liest dabei keinen einzigen Mailinhalt.** Nur Zahlen.

Sieht das plausibel aus, geht es weiter mit dem großen Durchgang.

---

## Was danach passiert

**Durchgang 1 – breit und flach.** Alle Mails der letzten 36 Monate, aber nur
Absender, Betreff, Datum und die Namen der Anhänge. Der Inhalt wird technisch gar nicht
erst übertragen (`BODY.PEEK[HEADER.FIELDS …]` holt ausschließlich die genannten
Kopfzeilen). Außerdem markiert das Skript keine Mail als gelesen – Paula merkt nichts
davon in ihrem Posteingang.

Aus dieser Liste erkenne ich, welche Mails mit Bewerbungen zu tun haben.

**Durchgang 2 – tief und schmal.** Nur für diese Mails: Volltext und Anhänge. Und hier
liegt der Schatz – ihre Lebenslauf-Fassungen und Motivationsschreiben, die sie über
Jahre verschickt hat.

**Durchgang 3 – verdichten.** Aus dutzenden Lebenslauf-Fassungen wird ein Faktenblock.
Was in vierzehn von fünfzehn Fassungen steht, stimmt. Wo sich zwei widersprechen, wird
sie gefragt statt geraten.

Danach weiß das System, welchen Beruf sie hat, wie sie schreibt, wo sie sich schon
beworben hat – und die Stellensuche kann anfangen.

---

## Wenn etwas nicht geht

| Meldung | Ursache | Abhilfe |
|---|---|---|
| Anmeldung fehlgeschlagen | App-Passwort falsch kopiert | Leerzeichen sind erlaubt, aber keine anderen Zeichen. Notfalls neues erzeugen |
| Seite „App-Passwörter" fehlt | Zwei-Faktor-Anmeldung nicht aktiv | Schritt 1 |
| Später plötzlich Fehler | Paula hat ihr Kontopasswort geändert | Dabei verfallen alle App-Passwörter. Neues erzeugen, Schritt 2 |
| Wenige oder keine Treffer | Andere Mailadresse für Bewerbungen? Andere Sprache? | Sag mir Bescheid, ich passe die Suche an |

## Wenn Paula aussteigen will

[myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords) →
Eintrag „Bewerbungshilfe" löschen. Ab diesem Moment kommt das System nicht mehr an ihre
Mailbox, ohne dass jemand etwas tun muss. Das gehört zu dem, was sie vorher wissen
sollte.

---

## Später: der Cloud-Weg als Alternative

Falls Google die App-Passwörter irgendwann abschaltet, ist der Wechsel klein: Die
Mailbox-Anbindung steckt vollständig in `scripts/mail.py`, mit einer schmalen
Schnittstelle. Der Rest des Systems merkt davon nichts. Ein Hinweis dazu steht in
`memory/offene-faeden.md`, damit es nicht vergessen wird.
