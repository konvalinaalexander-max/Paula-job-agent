# 00 – Vision, Ziele, Prinzipien

> **Version 2** (13.09.2026). Geändert nach den Antworten des Auftraggebers: Land = Österreich; kein automatischer Mailversand mehr; Telegram ersetzt durch ein Web-Dashboard; das Profil wird aus der Mailbox erarbeitet statt vorab abgefragt.

## Das Ziel in einem Satz

Paula soll jeden Morgen eine Website öffnen können, auf der fertig vorbereitete Bewerbungen liegen – Text, angepasster Lebenslauf, Empfängeradresse – die sie nur noch kopieren und aus ihrem eigenen Mailprogramm abschicken muss, ohne je doppelt zu bewerben und ohne den Überblick zu verlieren.

## Der entscheidende Unterschied zu Version 1

**Das System verschickt nichts.** Es bereitet vor. Paula sendet selbst, aus ihrem eigenen Gmail, mit ihrer eigenen Hand. Das ist nicht bloß eine Vereinfachung, sondern macht drei Probleme auf einmal verschwinden:

- **Mail-Reputation:** Kein Programm schickt Serienmails über ihr Konto. Kein Spam-Risiko.
- **Recht und Ehrlichkeit:** Jede Bewerbung geht von ihr aus. Kein Vollmacht-Graubereich.
- **Technik:** Kein Versand-Layer mit zehn Sicherheitsprüfungen, kein Sendefenster, keine Rate-Limits. Gmail wird **nur gelesen**, nie beschrieben.

Der Preis: Paula muss pro Bewerbung dreimal klicken statt einmal. Das ist es wert.

## Die vier Phasen

```
PHASE 0  Mailbox-Archäologie        (einmalig, nur lesen)
         Wer ist Paula? Was kann sie? Wie schreibt sie?
         Wo hat sie sich schon beworben? Was kam zurück?
              ▼
PHASE 1  Profil bauen               (einmalig, von Paula bestätigt)
         Faktenblock · Stilprofil · Suchprofil · Bewerbungshistorie
              ▼
PHASE 2  Laufender Betrieb          (3× täglich)
         Stellen finden · bewerten · Bewerbung vorbereiten
         → erscheint im Dashboard
              ▼
PHASE 3  Rückkanal                  (3× täglich)
         Hat sie gesendet? → Status wechselt automatisch
         Kam eine Antwort? → einordnen, Reaktion vorbereiten
```

Phase 0 ist der Kern der Idee und die eigentliche Neuerung: **Paulas Mailbox enthält bereits alles.** Dutzende Lebenslauf-Versionen, Motivationsschreiben, an wen sie sich beworben hat, in welchem Ton sie schreibt, was funktioniert hat und was nicht. Niemand muss ein Formular ausfüllen – die Antworten liegen schon da.

## Was das System ist

Eine **Vorbereitungs-Maschine mit Dashboard**. Software sammelt, filtert und protokolliert; Claude versteht und formuliert; ein Mensch entscheidet und sendet.

## Was das System **nicht** ist (Nicht-Ziele)

| Nicht-Ziel | Warum |
|---|---|
| Mails verschicken | Siehe oben. Gmail-Zugriff ist **nur lesend** (`gmail.readonly`). Es gibt keinen Sende-Code, kein Sende-Recht, keinen Sende-Knopf |
| Auto-Apply über Web-Formulare | Fragil, AGB-Verstoß, kein Kontrollpunkt. Stattdessen: Dashboard liefert Text zum Kopieren + Link zum Formular |
| "Ganz Österreich anschreiben" | Das System **scannt** breit, **bereitet** gezielt vor. Qualität vor Menge – siehe unten |
| Ein Chatbot | Das Dashboard hat definierte Zustände und Aktionen, keinen Freitext-Dialog |
| Multi-User / SaaS | Genau eine Nutzerin |
| Alle E-Mails analysieren | Ausdrückliche Auflage des Auftraggebers. Zweistufig: breiter Blick nur auf Absender/Betreff, tiefer Blick **nur** bei Bewerbungsbezug. Alles andere wird nicht gespeichert und nicht gelesen |

## Prinzipien (bei Konflikt gewinnt das obere)

1. **Paulas Hand am letzten Schritt.** Das System bereitet vor. Sie sendet.
2. **Wahrheit vor Überzeugungskraft.** Kein Satz über Paula, der nicht in ihren eigenen Unterlagen steht.
3. **Datensparsamkeit.** Was nicht bewerbungsbezogen ist, wird nicht angefasst.
4. **Qualität vor Menge.** Zehn recherchierte Bewerbungen schlagen hundert generische.
5. **Nachvollziehbarkeit.** Jeder Vorschlag erklärt sich selbst in zwei Sätzen.
6. **Einfachheit.** Die einfachste Lösung, die reicht.

## Rollen

| Rolle | Person | Zugang |
|---|---|---|
| Betreiber | Alexander | Claude-Session, Repo, Zugangsdaten, Dashboard (Admin) |
| Nutzerin | Paula | Nur das Dashboard. Kein Repo, keine Konsole, kein Claude-Chat |
| Ausführende KI | Claude (in Sessions, per Routine gestartet) | Repo, Gmail (lesend), Job-Quellen, Dashboard-Datenbank |

## Paulas Lage (wichtig für alle Entscheidungen)

Sie braucht dringend einen Job und ist offen für vieles. Das heißt für das System:

- **Breiter suchen als eng.** Lieber einen Vorschlag zu viel als eine Chance verpasst. Schwellwert eher niedrig ansetzen und nachjustieren.
- **Tempo zählt.** Vorbereitete Bewerbungen sollen am selben Tag im Dashboard liegen, an dem das Inserat erscheint.
- **Keine Bevormundung.** Das System sortiert nicht aus, was es für "unter ihrem Niveau" hält. Es zeigt die Einschätzung und lässt sie entscheiden.
- **Das Dashboard darf nicht überfordern.** Wenn 15 Vorschläge warten, sieht sie 15 – aber sortiert, mit dem besten oben, und jeder in 30 Sekunden erfassbar.

## Erfolgskriterien nach 8 Wochen

- **0** Doppelbewerbungen bei derselben Firma innerhalb der Sperrfrist
- **0** von Paula beanstandete erfundene Angaben
- Paula braucht **< 3 Minuten** pro Bewerbung (lesen, kopieren, senden)
- Das Dashboard zeigt den Status **ohne dass sie etwas eintippen muss** – gesendete Bewerbungen erkennt das System selbst
- Sie öffnet das Dashboard **freiwillig** mehrmals pro Woche
- Messbare Antwortquote im Dashboard sichtbar
