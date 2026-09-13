# Paula Job Agent

Ein Assistenzsystem für **eine** Person auf Stellensuche in Österreich. Es liest ihre Mailbox, lernt daraus, wer sie ist und wie sie schreibt, sucht mehrmals täglich passende Stellen und legt ihr **fertig vorbereitete Bewerbungen** auf ein Dashboard – Text, Empfänger, Lebenslauf.

**Abgeschickt wird von Hand.** Das System hat keinen Versandweg; der Gmail-Zugriff ist ausschließlich lesend. Paula kopiert den Text und sendet aus ihrem eigenen Mailprogramm. Dass sie gesendet hat, merkt das System beim nächsten Durchgang selbst.

## Wie es funktioniert

```
PHASE 0   Mailbox-Archäologie       Wer ist sie? Wie schreibt sie?
          (einmalig, nur lesen)      Wo hat sie sich beworben?
             │
PHASE 1   Profil bestätigen         Sie sieht es durch und korrigiert
             │
PHASE 2   Stellen finden            3× täglich: suchen, bewerten,
          und vorbereiten            Bewerbung schreiben → Dashboard
             │
PHASE 3   Rückkanal                 Gesendet? Antwort da? Status wandert,
                                     Dankestext liegt bereit
```

Die Besonderheit ist Phase 0. In Paulas Mailbox liegen bereits dutzende Fassungen ihres Lebenslaufs, alle ihre Motivationsschreiben und die vollständige Geschichte ihrer Bewerbungen. Niemand muss ein Formular ausfüllen – die Antworten sind schon da. Was in vierzehn von fünfzehn Lebenslauf-Fassungen steht, stimmt; wo sich zwei Fassungen widersprechen, wird sie gefragt.

## Was es nicht tut

Keine Mails verschicken · keine Formulare ausfüllen · keine Lebensläufe umschreiben · keine Angaben erfinden · keine Mails lesen, die nichts mit Bewerbungen zu tun haben · nicht „ganz Österreich anschreiben"

## Status

**Planung abgeschlossen, Umsetzung noch nicht begonnen.** Dieses Repository enthält den vollständigen Plan, die Datenstrukturen und das Gerüst. Es ist so geschrieben, dass eine ausführende KI es Etappe für Etappe bauen kann.

## Für die ausführende KI

**Zuerst [`CLAUDE.md`](CLAUDE.md) lesen.**

## Der Plan

| Datei | Inhalt |
|---|---|
| [`docs/00-vision.md`](docs/00-vision.md) | Ziel, Nicht-Ziele, Prinzipien, Erfolgskriterien |
| [`docs/01-architecture.md`](docs/01-architecture.md) | Wie das Ganze läuft – ohne eigenen Server |
| [`docs/02-data-model.md`](docs/02-data-model.md) | Datenstruktur, Statuswege, Doppelbewerbungs-Schutz |
| [`docs/03-llm-tasks.md`](docs/03-llm-tasks.md) | Die zwölf Urteile: Regeln, Ergebnisform, Prüffälle |
| [`docs/04-integrations.md`](docs/04-integrations.md) | Gmail, Stellenquellen Österreich, Firmendaten, Dashboard |
| [`docs/05-safety-legal.md`](docs/05-safety-legal.md) | Einwilligung, Datensparsamkeit, Wahrheit in den Texten |
| [`docs/06-operations.md`](docs/06-operations.md) | Betrieb, Automatik, Kosten, was bei Störungen zu tun ist |
| [`docs/07-milestones.md`](docs/07-milestones.md) | Etappen M0–M7 mit Abnahmekriterien |
| [`docs/08-open-questions.md`](docs/08-open-questions.md) | Beantwortet und offen |
| [`docs/09-research-notes.md`](docs/09-research-notes.md) | Was recherchiert wurde, was verworfen |
| [`docs/10-dashboard.md`](docs/10-dashboard.md) | Die Oberfläche, Block für Block |
| [`docs/11-testing.md`](docs/11-testing.md) | Wie geprüft wird |
| [`docs/12-quellen-abdeckung.md`](docs/12-quellen-abdeckung.md) | Stellenquellen Österreich: wie viel des Marktes wir erreichen |
| [`docs/13-initiativbewerbungen.md`](docs/13-initiativbewerbungen.md) | Firmen finden, die gerade jemanden brauchen – ohne Inserat |
| [`docs/14-arbeitsweise.md`](docs/14-arbeitsweise.md) | Warum hier kein Programm arbeitet, sondern jemand mitdenkt |

## Aufbau

```
CLAUDE.md      Anweisungen für die ausführende KI
docs/          Der Plan
scripts/       Helfer: Daten holen und schreiben (keine Urteile)
runbooks/      Arbeitsanweisungen für die Läufe
memory/        Was zwischen den Läufen erhalten bleibt: Gelerntes, Strategie, Experimente
dashboard/     Die Seite, die Paula sieht
config/        Listen und Einstellungen
tests/         Tests und erfundene Beispieldaten
deploy/        Einrichtungsanleitungen
```

**Keine personenbezogenen Daten in diesem Repository.** Mails, Lebensläufe, Firmen und Bewerbungen liegen ausschließlich in der Dashboard-Datenbank.

## Rollen

- **Alexander** – richtet ein, betreibt, entscheidet
- **Paula** – sucht die Stelle, sieht nur das Dashboard, sendet selbst
- **Claude** – baut das System und macht später die täglichen Läufe
