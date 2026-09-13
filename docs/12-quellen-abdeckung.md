# 12 – Stellenquellen: Wie viel des österreichischen Marktes erreichen wir?

> Geschrieben am 13.09.2026 nach gezielter Recherche. Einträge mit **[prüfen]** sind aus Suchergebnissen abgeleitet und müssen vor dem Einsatz selbst getestet werden – der Entwicklungsrechner kommt derzeit an viele Domains nicht heran.

## Die kurze Antwort

**Ja, die Abdeckung reicht** – aber nicht über einen einzigen Weg, sondern über vier, die sich gegenseitig ergänzen. Zwei davon hatte ich beim ersten Durchgang übersehen und sie sind die wichtigsten.

| | Quelle | Was sie bringt | Aufwand |
|---|---|---|---|
| 1 | **EURES** (EU-Stellenportal) | Öffentliche Schnittstelle, 31 Länder, über 2 Mio. Stellen. **Enthält die Meldungen der nationalen Arbeitsverwaltungen – also die AMS-Stellen** | gering |
| 2 | **METAJob.at** | Größte Meta-Suchmaschine Österreichs, ~108.000 Stellen. Findet ausdrücklich auch Stellen, die **nirgends inseriert** sind – von KMU, NGOs, öffentlichen Stellen, direkt von Firmenwebsites | gering |
| 3 | **Adzuna AT** | Offizielle Schnittstelle, aggregiert die großen Portale | gering |
| 4 | **Job-Mails der Portale** | karriere.at, willhaben, StepStone, hokify – auf dem vom Portal vorgesehenen Weg | 10 Min. Einrichtung |

Dazu zwei Ergänzungen: von Paula eingereichte Links und die Karriereseiten beobachteter Firmen.

---

## Was sich gegenüber dem ersten Plan geändert hat

### Fund 1: EURES ist der Weg zu den AMS-Stellen

Im ersten Durchgang hatte ich das AMS als verschlossen abgeschrieben: Die Suche auf `jobs.ams.at` verlangt ein signiertes Merkmal, das nur die eigene Weboberfläche erzeugt.

**Das war der falsche Weg.** Die nationalen Arbeitsverwaltungen melden ihre Stellen an **EURES**, das europäische Stellenportal – und EURES hat eine öffentlich erreichbare Schnittstelle:

```
POST https://europa.eu/eures/api/jv-searchengine/public/jv-search/search
GET  https://europa.eu/eures/api/jv-searchengine/public/jv/id/{id}
```

Ohne Anmeldung, mit Filtern nach Stichwort, Region (NUTS-Codes), Veröffentlichungszeitraum, Arbeitszeitmodell, Berufscode (ESCO) und Sprache. Die Antwort enthält Arbeitgeber, Ort, Gehalt und Bewerbungskontakt. Pro Suche höchstens 10.000 Treffer – für Paula uninteressant, wir brauchen ein paar Dutzend pro Tag.

Es gibt eine von der Gemeinschaft gepflegte Dokumentation der Endpunkte (rorar/EURES-API-Documentation auf GitHub). Sie ist nicht offiziell, das heißt: Die Schnittstelle kann sich ändern, ohne dass es jemand ankündigt. Deshalb Testfälle und automatische Abschaltung nach drei Fehlläufen.

**[prüfen] in M4:** Wie viele österreichische Stellen liefert EURES tatsächlich, und sind AMS-Stellen wirklich enthalten? Das ist die erste Frage, die die Umsetzung beantwortet.

### Fund 2: METAJob findet, was nirgends steht

METAJob durchsucht laufend das österreichische Web nach Stellenanzeigen – nicht nur Portale, sondern auch Firmenwebsites. Die eigene Beschreibung: Man finde dort auch Stellen, die **nicht ausgeschrieben** seien, weil kleine und mittlere Betriebe, NGOs und öffentliche Einrichtungen sich die Portalgebühren sparen.

Das ist für Paula besonders wertvoll, weil genau dort die Stellen liegen, auf die sich wenige bewerben. Ein Inserat auf karriere.at bekommt 150 Bewerbungen; eine Stelle, die nur auf der Website eines Sechzig-Mann-Betriebs in Wiener Neustadt steht, bekommt vielleicht sechs.

Zugang: Job-Mail einrichten (sicher möglich) oder RSS **[prüfen]**. Eine Schnittstelle gibt es vermutlich nicht.

### Was bleibt, wie es war

**Adzuna** als offizielle Schnittstelle mit `country=at`. **Job-Mails** der großen Portale, weil das der einzige vorgesehene maschinelle Weg dorthin ist.

**Jooble** hat zwar einen kostenlosen Zugang, aber mit einem Gesamtkontingent von 500 Abfragen pro Schlüssel – nicht für Dauerbetrieb, brauchbar für einen einmaligen breiten Durchgang zu Beginn.

---

## Die realistische Einschätzung

Ein Inserat, das in Österreich ernsthaft besetzt werden soll, erscheint fast immer an mindestens einer dieser Stellen:

- **auf einem großen Portal** → Adzuna, Job-Mails, METAJob
- **beim AMS** → EURES (Meldung ist für viele Stellen ohnehin üblich)
- **nur auf der Firmenwebsite** → METAJob, Karriereseiten-Beobachtung

Die verbleibende Lücke sind Stellen, die **überhaupt nicht** veröffentlicht werden – und die sind der Gegenstand des nächsten Dokuments, `docs/13-initiativbewerbungen.md`. Für die ist keine Stellenquelle zuständig, sondern eine andere Denkweise.

**Was die Abdeckung wirklich begrenzt, ist nicht die Zahl der Quellen, sondern die Breite der Suchbegriffe.** Wer nur nach „Assistenz der Geschäftsführung" sucht, verpasst „Büroleitung", „Backoffice", „Teamassistenz", „Sekretariat", „Verwaltungsassistenz", „Sachbearbeitung Innendienst" und ein Dutzend weitere Bezeichnungen für dieselbe Arbeit. Deshalb wird das Suchprofil in Phase 1 aus ihren bisherigen Bewerbungen erarbeitet und **bewusst breiter** angesetzt – und regelmäßig erweitert, wenn im Datenstrom neue Bezeichnungen für ähnliche Rollen auftauchen.

---

## Umsetzungsreihenfolge

| Etappe | Quelle | Warum in dieser Reihenfolge |
|---|---|---|
| M4, zuerst | **Adzuna** | Offiziell, stabil, schnell gebaut – der Beweis, dass die Kette funktioniert |
| M4 | **EURES** | Zweitgrößter Zugewinn, ähnlich einfach. Vorher: Umfang prüfen |
| M4 | **Job-Mails** (karriere.at, willhaben, StepStone, METAJob, hokify) | Braucht Paula für die Einrichtung – gleich mit erledigen |
| M4 | **Eingereichte Links** | Trivial, hoher Nutzen |
| M6 | **Karriereseiten** beobachteter Firmen | Erst sinnvoll, wenn es beobachtete Firmen gibt |
| einmalig | **Jooble** | Ein Durchgang zu Beginn, um den Bestand zu füllen |

---

## Was ausdrücklich nicht gemacht wird

Kein Auslesen von karriere.at, willhaben, StepStone oder AMS gegen deren Bedingungen. Kein LinkedIn. Keine gekauften Datendienste. Für alles davon gibt es hier einen legitimen Weg, der zudem stabiler ist.

## Einstellung der Quellen

`config/settings.yaml` unter `quellen:` – jede einzeln abschaltbar, mit eigenen Suchbegriffen. Fällt eine dreimal hintereinander aus, schaltet sie sich selbst ab und meldet sich. Die Stellen, die schon in der Datenbank sind, bleiben; die anderen Quellen laufen weiter. Der Ausfall einer Quelle legt das System nie still.
