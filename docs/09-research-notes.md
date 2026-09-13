# 09 – Recherche-Notizen

Stand: September 2026. Einträge mit **[prüfen]** stammen aus Suchergebnissen und müssen vor der Nutzung selbst verifiziert werden.

## Stellenquellen Österreich

| Quelle | Zugang | Beurteilung |
|---|---|---|
| **Adzuna AT** | Offizielle Schnittstelle, kostenlose Kennung, Land `at` | **Primärquelle.** Österreich ist unter den unterstützten Ländern. Kontingent beim Registrieren prüfen **[prüfen]** |
| **AMS „alle jobs"** (`jobs.ams.at`) | Die Suche läuft über eine JSON-Schnittstelle, aber jede Anfrage braucht ein signiertes Merkmal, das nur die eigene Weboberfläche erzeugt. Fertige Auslese-Dienste umgehen das mit einem echten Browser | Direkter Abruf praktisch nicht möglich und rechtlich fragwürdig. **→ E-Mail-Suchauftrag** |
| **karriere.at** | Keine öffentliche Schnittstelle für Suchende gefunden. (Die AMS-„HR-API" richtet sich an Arbeitgeber) | **→ E-Mail-Suchauftrag** |
| **willhaben Jobs** | Größter Marktplatz Österreichs, über 17.000 Stellen; keine offene Schnittstelle | **→ E-Mail-Suchauftrag** |
| **StepStone AT** | Keine offene Schnittstelle | **→ E-Mail-Suchauftrag** |
| **Karriereseiten-Plattformen** | Personio (in Österreich sehr verbreitet), Greenhouse, Lever, SmartRecruiters haben offen abrufbare Stellenlisten **[Pfade prüfen]** | Lohnt sich für beobachtete Firmen |
| LinkedIn | Keine Schnittstelle, aktive Gegenwehr | Nicht. Nur über eingereichte Links |

**Der entscheidende Befund für Österreich:** Alle großen Portale sind maschinell verschlossen. Der Weg über E-Mail-Suchaufträge ist deshalb nicht ein Notbehelf, sondern die *richtige* Lösung – er ist vom Portal vorgesehen, verstößt gegen nichts, bricht nicht bei Seitenänderungen und deckt genau die Quellen ab, die sonst fehlen würden.

## Firmendaten Österreich

| Quelle | Zugang |
|---|---|
| **WKO Firmen A–Z** | Öffentliches Branchenverzeichnis, nach Branche und Bezirk. Nahezu vollständig für gewerbliche Betriebe. Bedingungen für automatisierten Abruf prüfen **[prüfen]** |
| **data.gv.at** | Offene Verwaltungsdaten, verschiedene Unternehmensdatensätze. Vor M7 sichten **[prüfen]** |
| **Firmenbuch (justiz.gv.at)**, **Wirtschafts-Compass** | Einzelabfragen, teils kostenlos. Kein Massenabruf |
| Mailbox und Inserate | Die besten Kandidaten – Firmen mit Bezug zu ihr bzw. mit Einstellungsbedarf |

## Bestehende Projekte – was sie lehren

| Projekt | Ansatz | Übernommen | Verworfen |
|---|---|---|---|
| **ApplyPilot** (AGPL) | Sechsstufige Kette: finden → anreichern → bewerten → Lebenslauf anpassen → Anschreiben → **automatisch absenden** | Die Stufenlogik; Bewertung vor teuren Schritten; Anreicherung über eingebettete Stellenbeschreibungen | Automatisches Absenden; automatisch umgebaute Lebensläufe; Lizenz |
| **AIHawk** und Abkömmlinge | Bot für Formular-Bewerbungen mit generierten Antworten | – | Alles. Zeigt, was schiefgeht: gesperrte Konten, generische Texte |
| **JobSpy** (MIT) | Auslese-Bibliothek für mehrere Portale | Die Feldstruktur für normalisierte Stellen | Nutzung selbst (Bedingungen; für Österreich ohnehin schwach) |

**Gemeinsamer Befund:** Alle öffentlichen Projekte optimieren auf Menge und haben keinen menschlichen Kontrollpunkt. Keines liest die Mailbox, um Doppelbewerbungen zu vermeiden oder Antworten zu verfolgen. Genau diese Lücken – und der bewusste Verzicht aufs Absenden – sind der Kern dieses Projekts.

## Gmail

- Zugriff über die offizielle Schnittstelle mit Anmeldung; App-Passwörter werden abgeschafft.
- `format=metadata` überträgt **nur** Kopfzeilen – der Inhalt verlässt Googles Server gar nicht. Das ist die technische Grundlage der Datensparsamkeits-Auflage.
- **Falle:** Bleibt das Projekt im Status „Testing", verfällt die Anmeldung nach sieben Tagen. Auf „In Produktion" setzen; eine Verifizierung ist unter 100 Nutzern nicht nötig.
- Der Link `https://mail.google.com/mail/?view=cm&to=…&su=…&body=…` öffnet ein vorausgefülltes Nachrichtenfenster. Länge begrenzt **[an einem langen Text prüfen]**.

## Dashboard-Plattform

- Veröffentlichte Seite mit dauerhafter Datenbank (Dokumentspeicher), Dateiablage und Download-Funktion. Von der Seite **und** aus der Claude-Session beschreibbar.
- Zugriffsrechte nach Freigabestufe steuerbar: lesen für alle Zugelassenen, schreiben nur für bestimmte Bereiche.
- **Einschränkung:** organisationsintern, nicht öffentlich teilbar. Daraus folgt Q17.
- Dokumente max. 256 KiB – für Bewerbungstexte reichlich, Mailtexte werden gekürzt.

## Verworfen

- **Eigener Server (VPS):** Mit Dashboard-Datenbank und Routinen nicht nötig. Bleibt der Plan B, falls die Zugangsfrage es erzwingt.
- **Anthropic-Schnittstelle mit eigenem Schlüssel:** Getrennte Kosten ohne Gegenwert, wenn die Arbeit ohnehin in Sessions läuft.
- **Telegram:** Durch das Dashboard ersetzt. Bliebe eine Option für Benachrichtigungen (Q21).
- **Automatischer Versand:** Vom Auftraggeber gestrichen. Die beste Entscheidung im ganzen Projekt.
- **Automatisch umgebaute Lebensläufe:** Heikel (Wahrheit, Formatierung) bei geringem Nutzen gegenüber einem guten Anschreiben.
- **SQLite:** Kein Server, der eine Datei behalten könnte.

## Abweichungen

*(Hier einträgt die ausführende KI, wo der Plan sich als falsch erwiesen hat. Format: Datum – was im Plan stand – was tatsächlich gilt – was stattdessen gemacht wurde.)*
