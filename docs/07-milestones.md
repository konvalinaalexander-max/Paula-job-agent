# 07 – Etappenplan

> **Version 2.** Neue Reihenfolge: Die Mailbox-Auswertung ist jetzt das **Fundament**, nicht ein Zwischenschritt. Erst wenn das System weiß, wer Paula ist, sucht es Stellen.

Acht Etappen. Jede endet mit etwas Vorzeigbarem und einer Abnahme. **Nichts in diesem Plan verschickt je eine Mail** – der gefährlichste Teil des ursprünglichen Entwurfs ist ersatzlos gestrichen.

---

## M0 – Fundament

**Ziel:** Zugänge stehen, Skripte laufen, die Datenbank nimmt Daten an.

**Aufgaben:**
1. `scripts/db_io.py` – lesen, schreiben, Schema prüfen, Statusübergänge, Ausfuhr/Rücksicherung. Das Skript ist die einzige Tür zur Datenbank; alles andere geht durch es hindurch.
2. `scripts/gmail_auth.py` + `scripts/gmail_fetch.py` – Anmeldung, Liste holen (`metadata`), Mails holen (`full`), Anhänge holen. **Nur Lesezugriff.**
3. `scripts/extract.py` – MIME zu Text, HTML zu Text, Zitate und Signaturen entfernen, PDF und DOCX lesen.
4. `scripts/dedup.py` – Firmennamen normalisieren (österreichische Rechtsformen!), Fingerabdrücke, Ähnlichkeitsvergleich.
5. Google-Projekt anlegen, Berechtigung einrichten, **Paula meldet sich an**. Adzuna registrieren.
6. `docs/einwilligung.md`, mit Paula durchgehen, `state/consent` setzen.
7. `deploy/SETUP.md` – die Anleitung für Alexander, Klick für Klick.
8. Tests für dedup, extract, db_io mit erfundenen Beispieldaten.

**Fertig, wenn:** `python scripts/gmail_fetch.py --list --months 1` gibt eine Liste aus. `python scripts/db_io.py --selftest` legt ein Testdokument an und löscht es. Tests grün.

**Abnahme:** Alexander führt beides aus und sieht plausible Ausgaben.

---

## M1 – Mailbox-Archäologie *(der Kern)*

**Ziel:** Das System weiß, wo Paula sich beworben hat, was daraus wurde, und hat alle ihre Lebenslauf-Fassungen beisammen.

**Aufgaben:**
1. **Lauf 1 – breit, flach.** Alle Mails der letzten 36 Monate, nur Kopfzeilen. U1 sortiert. Nicht-Treffer landen als Kennnummer in `seen`, ihr Inhalt wird nie abgerufen.
2. **Lauf 2 – tief, schmal.** Nur die Treffer: Volltext plus Anhänge. U2 ordnet ein.
3. **Lebensläufe sichern.** Alle Anhänge aus gesendeten Bewerbungen in die Dateiablage, Verzeichnis in `profile/documents`.
4. **Historie bauen.** Gesendete Bewerbung → `applications` mit `kind: historical`. Spätere Mails im selben Gesprächsfaden oder von derselben Domain → Status fortschreiben. Firmen anlegen und zusammenführen.
5. **Bericht.** Eine Tabelle: Firma, Stelle, wann beworben, was kam zurück, wie sicher.
6. Test: 40 erfundene Mails, davon 12 bewerbungsbezogen – alle müssen gefunden werden.

**Fertig, wenn:** Der Bericht existiert und Alexander geht ihn mit Paula durch. Sie erkennt ihre Bewerbungen wieder. Falsches wird korrigiert. Ein zweiter Lauf erzeugt keine Duplikate.

**Abnahme:** Paula bestätigt, dass die Liste im Wesentlichen stimmt.

**Hinweise:** Je nach Mailboxgröße dauert Lauf 1 lange – in Abschnitten arbeiten, Fortschritt in `state/gmail`. Mehrsprachigkeit nicht vergessen (deutsche und englische Bewerbungen). Wenn sie mehrere Adressen benutzt hat, alle erfassen (Q3b).

---

## M2 – Wer ist Paula

**Ziel:** Faktenblock, Stilprofil, Suchprofil – aus ihren eigenen Unterlagen erarbeitet und von ihr bestätigt.

**Aufgaben:**
1. **U3:** Alle Lebenslauf-Fassungen vergleichen. Für jede Angabe zählen, in wie vielen sie steht. Widersprüche sammeln.
2. **U4:** Stilprofil aus den Mailtexten.
3. **U5:** Suchprofil vorschlagen – bewusst breiter als ihre bisherigen Bewerbungen.
4. Profil-Bereich im Dashboard bauen (`docs/10-dashboard.md`), damit sie alles durchsehen kann.
5. Job-Suchaufträge bei karriere.at, willhaben, StepStone und AMS einrichten – zusammen mit ihr, zehn Minuten.
6. Probe: drei erfundene Inserate, drei Bewerbungstexte erzeugen und ihr zeigen.

**Fertig, wenn:** Paula hat alles bestätigt, offene Fragen geklärt, und sagt zu den Probetexten: **„das klingt nach mir."**

**Abnahme:** Ihr Urteil über die Probetexte. Das ist die wichtigste Abnahme des ganzen Projekts. Wenn die Texte nicht nach ihr klingen, wird sie das System nicht benutzen – dann wird das Stilprofil nachgebessert und die Probe wiederholt, so oft wie nötig.

---

## M3 – Das Dashboard

**Ziel:** Paula kann die Seite öffnen und benutzen.

**Aufgaben:**
1. Alle fünf Blöcke, Karten ein- und ausklappbar, nach `docs/10-dashboard.md`.
2. Kopieren-Knöpfe, Lebenslauf-Download, „In Gmail öffnen"-Link (**mit langem Text prüfen** – Längenbegrenzung).
3. Paulas Aktionen schreiben zurück: abgehakt, verworfen, Firma sperren, Änderungswunsch, Link einreichen, Pause.
4. Zugriffsrechte: sie ändert Status, nicht Inhalte.
5. Handy-Ansicht, Dunkelmodus, kein waagrechtes Scrollen.
6. Veröffentlichen, Adresse an Paula, Lesezeichen einrichten.
7. **Zugangsfrage klären** (Q17), bevor diese Etappe beginnt.

**Fertig, wenn:** Paula öffnet die Seite auf ihrem Handy und ihrem Rechner, kommt allein zurecht, kopiert einen Text, lädt einen Lebenslauf.

**Abnahme:** Sie benutzt es, ohne dass jemand danebensitzt.

---

## M4 – Stellen finden und Bewerbungen vorbereiten

**Ziel:** Jeden Tag liegen passende, fertige Bewerbungen im Dashboard.

**Aufgaben:**
1. `scripts/sources/adzuna.py` mit Volltext-Nachladen; Vermittler-Erkennung.
2. `scripts/sources/mailalert.py` – ein Leser je Portal, mit Beispielmail als Testfall.
3. `scripts/sources/manual.py`.
4. Regel-Vorfilter: Ort, Ausmaß, Ausschlusswörter, gesperrte Firmen, Sperrfrist.
5. U6 Bewertung, U7 Firmenrecherche, U8 Text, U9 Faktenprüfung, U12 Nachbessern.
6. `runbooks/daily-jobs.md` – die Anweisung für den täglichen Lauf.
7. Testfälle: 15 Inserate mit Erwartungsband, 3 mit eingebauten Anweisungen.

**Fertig, wenn:** Eine Woche Betrieb von Hand. Mindestens 15 Karten erzeugt. Paula hat mindestens fünf Bewerbungen abgeschickt. Alexander liest alle Texte gegen und findet keine erfundene Angabe.

**Abnahme:** Beide. Paula sagt, ob die Vorschläge taugen.

---

## M5 – Der Rückkanal

**Ziel:** Das System merkt, was Paula gesendet hat und was zurückkommt.

**Aufgaben:**
1. Versanderkennung aus dem Gesendet-Ordner → Status springt von allein.
2. Antworten zuordnen (Gesprächsfaden → Absenderdomain → Betreff) und einordnen (U10).
3. U11: Absagen-Dank, Einladungs-Zusage mit Terminwahl, Rückfragen mit sichtbaren Lücken.
4. Blöcke 0 und 3 im Dashboard mit Leben füllen.
5. Nachfass-Vorschlag nach sechs Wochen; automatisches Schließen nach 90 Tagen.
6. `runbooks/daily-replies.md`.

**Fertig, wenn:** Eine echte gesendete Bewerbung wandert ohne Zutun in Block 2. Eine echte Antwort wird richtig eingeordnet. Eine Absage bekommt einen Dankestext, den Paula tatsächlich verschickt.

**Abnahme:** Paula prüft den Ton der Dankestexte – hier ist der Ton alles.

---

## M6 – Automatik und Betriebsreife

**Ziel:** Läuft ohne Alexander.

**Aufgaben:**
1. Routinen einrichten (§ 6.1), Anweisungen fertigstellen.
2. Meldungen an Alexander (§ 6.5), einmal jede auslösen und prüfen.
3. Wöchentliche Ausfuhr, Rücksicherung einmal üben, `deploy/RESTORE.md`.
4. Wochenbericht: was lief, Schwellwert-Vorschlag aus Paulas Verhalten.
5. Selbstkalibrierung: verwirft sie zu viel, Schwellwert hoch; verwirft sie fast nichts, runter.
6. `deploy/RUNBOOK.md`.

**Fertig, wenn:** 14 Tage ohne Eingriff. Karten kamen zuverlässig. Kein Lauf blieb unbemerkt hängen.

---

## M7 – Initiativbewerbungen

**Ziel:** Auch Firmen ohne Ausschreibung werden angesprochen.

**Aufgaben:**
1. Firmenliste aufbauen: Startliste, Firmen aus der Mailbox, Firmen aus Inseraten, WKO-Verzeichnis (Bedingungen prüfen), data.gv.at sichten.
2. Regelbasiert vorsortieren → `priority_score`.
3. Nachts die besten zehn recherchieren (U7), bewerten, Text vorbereiten – Variante „Initiativ".
4. Prüfung: Empfängeradresse muss zur Firmendomain passen. Keine Adresse → Karte zeigt stattdessen den Link zum Bewerbungsformular.
5. Ähnlichkeitsprüfung gegen die letzten 20 Texte (kein Serienbrief).
6. Karriereseiten-Beobachtung für recherchierte Firmen.
7. Schalter im Dashboard: Initiativbewerbungen an/aus.

**Fertig, wenn:** Fünf Nächte gelaufen, mindestens fünf Initiativ-Karten, Alexander prüft die Recherchen stichprobenartig gegen die echten Websites – keine erfundenen Adressen.

**Hinweis:** Das ist bewusst die **letzte** Etappe. Sie ist die teuerste, unsicherste und am schwersten zu beurteilende. Bis dahin läuft das System seit Wochen stabil mit ausgeschriebenen Stellen.

---

## M8 – Später, nur nach neuer Entscheidung

Weitere Quellen · Anschreiben als PDF, wenn Firmen es verlangen · Bausteine für Web-Formulare zum Kopieren · Terminkalender für Einladungen · Lern-Schleife, die aus Paulas Änderungswünschen Vorschläge fürs Stilprofil macht · eigene Website statt veröffentlichter Seite, falls die Zugangsfrage das nötig macht.

---

## Warum diese Reihenfolge

M1 und M2 zuerst, weil in Paulas Mailbox bereits alles liegt, was das System über sie wissen muss – und weil ohne Faktenblock und Stilprofil kein Text erzeugt werden kann, der sie nicht blamiert. M3 vor M4, weil die Oberfläche existieren muss, bevor es etwas zu zeigen gibt. M4 vor M5, weil Antworten erst kommen, wenn beworben wurde. M6 erst, wenn die Sache von Hand bewiesen ist – Automatik auf einem ungeprüften Ablauf vervielfacht nur die Fehler. M7 zuletzt, aus den genannten Gründen.

Der Weg bis zur ersten echten Bewerbung führt über M0–M4. Das ist das Ziel, auf das alles davor hinarbeitet – und weil Paula dringend etwas braucht, sollte M3 notfalls abgespeckt werden (eine einfache Liste tut es zunächst auch), um schneller dorthin zu kommen.
