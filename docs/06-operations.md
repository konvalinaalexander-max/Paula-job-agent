# 06 – Betrieb

> **Version 2.** Kein Server, kein Docker, kein systemd. Der Betrieb besteht aus einer geplanten Routine und einem Dashboard.

## 6.1 Wie das Ding läuft, ohne dass jemand „mach jetzt" tippt

Die Frage des Auftraggebers beantwortet: Es gibt **Routinen** – geplante Auslöser, die automatisch eine Claude-Session starten. Man richtet sie einmal ein, danach laufen sie von selbst.

| Routine | Zeitpunkt | Arbeitsanweisung | Dauer |
|---|---|---|---|
| `paula-morgen` | werktags 07:00 | `runbooks/daily-jobs.md` + `daily-replies.md` | 10–20 Min |
| `paula-mittag` | werktags 12:30 | dieselbe | 5–15 Min |
| `paula-abend` | täglich 17:30 | dieselbe | 10–20 Min |
| `paula-firmen` | nachts 02:00 | `runbooks/spontaneous.md` | 20–40 Min |
| `paula-woche` | sonntags 18:00 | `runbooks/weekly-review.md` | 10 Min |

Phase 0 und 1 laufen **nicht** als Routine, sondern von Hand aus einer Session heraus – sie sind einmalig, dauern länger und brauchen Alexanders Aufmerksamkeit.

Jeder Lauf endet mit einem kurzen Protokolleintrag. Passiert etwas Ungewöhnliches (Anmeldung abgelaufen, Quelle mehrfach ausgefallen, Faktenprüfung wiederholt fehlgeschlagen), meldet sich die Routine bei Alexander.

## 6.2 Der Unterschied zwischen den drei Wegen, Claude zu nutzen

Weil die Frage ausdrücklich gestellt wurde:

| Weg | Was es ist | Kosten | Passt hier? |
|---|---|---|---|
| **Dieser Chat** | Ein Mensch schreibt, Claude antwortet und arbeitet | Im Abo enthalten | Für Entwicklung und Phase 0/1 – ja |
| **Routine** | Ein Zeitplan startet automatisch eine Session mit einer festen Anweisung | Im Abo enthalten | **Für den laufenden Betrieb – ja, das ist die Lösung** |
| **Schnittstelle (API)** | Ein Programm ruft Claude bei jedem Bedarf einzeln auf, mit eigenem Zugangsschlüssel | Pro Nutzung, getrennte Rechnung | Wäre nötig gewesen bei eigenem Server. **Hier nicht** |

Eine *Schnittstelle* ist dabei nichts anderes als eine Steckdose für Programme: Statt dass ein Mensch auf einer Website klickt, fragt ein Programm direkt nach Daten und bekommt eine strukturierte Antwort. Adzuna und Gmail werden so angesprochen. Claude nicht – Claude **ist** hier der Arbeiter, nicht ein befragter Dienst.

## 6.3 Was es kostet

| Posten | Kosten |
|---|---|
| Claude (Entwicklung + Routinen) | Alexanders bestehendes Abo |
| Dashboard inkl. Datenbank und Dateiablage | Im Abo enthalten |
| Gmail-Zugriff | Kostenlos |
| Adzuna | Kostenlos im geplanten Umfang |
| Job-Mails der Portale | Kostenlos |
| Server, Domain, Datenbank | **Entfällt** |
| Zugang für Paula | Offen – siehe Q17 |

Erwartete laufende Kosten: **0 €** zusätzlich, solange Paulas Zugang im Abo unterkommt. Andernfalls entweder ein zusätzlicher Platz oder die Variante mit eigener Website (~0–10 €/Monat).

## 6.4 Einrichtung (Reihenfolge)

1. Google Cloud Projekt + Gmail-Berechtigung + Anmeldung durch Paula (§ 4.1)
2. Adzuna-Registrierung → Kennung und Schlüssel
3. Geheimnisse in der Umgebung hinterlegen, in der die Routinen laufen
4. Dashboard erstmals veröffentlichen, Adresse notieren
5. Phase 0 von Hand starten (dauert je nach Mailbox eine bis mehrere Stunden, in Etappen)
6. Phase 1 mit Paula durchgehen – sie bestätigt Faktenblock, Stilprofil, Suchprofil
7. Job-Suchaufträge bei karriere.at, willhaben, StepStone, AMS einrichten (zehn Minuten, mit Paula)
8. Routinen einrichten
9. Erste Woche täglich beobachten

Genaue Schritte mit allen Klicks: `deploy/SETUP.md` (entsteht in M0).

## 6.5 Beobachtung

Das Dashboard zeigt Alexander am Seitenende: letzter Lauf, geprüfte Inserate, erzeugte Karten, Fehler, Warnungen.

Meldung an ihn, wenn:
- ein Lauf abbricht oder mehr als ein Fünftel der Einzelschritte fehlschlägt
- die Gmail-Anmeldung abgelaufen ist
- eine Quelle dreimal hintereinander ausgefallen ist (wird dann abgeschaltet)
- eine Faktenprüfung zweimal fehlgeschlagen ist
- seit 24 Stunden kein Lauf stattgefunden hat
- Paula seit zehn Tagen nichts gesendet hat, obwohl Karten warten *(ein Zeichen, dass etwas nicht stimmt – Texte zu schlecht, Dashboard zu unhandlich, oder sie braucht Unterstützung)*

## 6.6 Sicherung

Der Wochenlauf schreibt eine vollständige Ausfuhr der Datenbank als JSON. Alexander legt sie ab, wo er möchte (Q12). Die Lebenslauf-Dateien liegen zusätzlich in der Dateiablage des Dashboards und ohnehin in Paulas Mailbox.

Wiederherstellung: Ausfuhr zurückspielen über `scripts/db_io.py --restore`. Einmal in M6 üben und in `deploy/RESTORE.md` festhalten.

## 6.7 Wenn etwas kaputtgeht

| Symptom | Ursache | Abhilfe |
|---|---|---|
| Keine neuen Karten mehr | Quelle abgeschaltet, Schwellwert zu hoch, oder Suchbegriffe zu eng | `state/sources` prüfen; Schwellwert senken; Suchprofil erweitern |
| Anmeldung abgelaufen | Google-Projekt steht auf „Testing" | Auf „In Produktion" umstellen, Paula meldet sich neu an |
| Doppelte Karten | Firmen-Erkennung hat zwei Schreibweisen nicht zusammengeführt | Alias von Hand ergänzen; Testfall nachziehen |
| Texte klingen falsch | Stilprofil unpassend | Mit Paula durchgehen und korrigieren – das Profil ist eine Datei, keine Blackbox |
| Paula reagiert nicht | Zu viele Karten, unklare Texte, oder etwas anderes | Nachfragen. Zahl der Vorschläge senken |
