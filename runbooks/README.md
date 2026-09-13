# Arbeitsanweisungen

Diese Dateien sind das, was eine Claude-Session zu Beginn eines Laufs liest. Sie
beschreiben Schritt für Schritt, was zu tun ist, welche Skripte aufzurufen sind und
welche Urteile (siehe `docs/03-llm-tasks.md`) dabei gefällt werden.

| Datei | Wann | Ausgelöst durch |
|---|---|---|
| `phase0-mailbox.md` | einmalig, M1 | von Hand |
| `phase1-profile.md` | einmalig, M2 | von Hand |
| `daily-jobs.md` | 3× täglich | Routine |
| `daily-replies.md` | 3× täglich | Routine |
| `spontaneous.md` | nachts | Routine |
| `weekly-review.md` | sonntags | Routine |

**Aufbau jeder Anweisung:**

1. *Voraussetzungen* – was vorher erledigt sein muss (Phase, bestätigtes Profil, …)
2. *Schritte* – nummeriert, mit konkreten Befehlen
3. *Urteile* – welche aus `docs/03-llm-tasks.md` dabei zu fällen sind
4. *Grenzen* – was dieser Lauf nicht tut, wann er abbricht
5. *Abschluss* – was in `events` und `state` geschrieben wird

**Regeln, die in jeder Anweisung gelten:**

- Jeder Lauf ist beliebig wiederholbar, ohne Doppeltes zu erzeugen.
- Bricht ein Schritt ab, wird der Fortschritt in `state/` festgehalten und der nächste Lauf macht dort weiter.
- Alles, was erhalten bleiben soll, geht in die Datenbank – der Container ist danach weg.
- Fehler bei einzelnen Elementen (eine Mail, ein Inserat) werden protokolliert und übersprungen, nicht als Abbruch behandelt. Erst wenn mehr als ein Fünftel scheitert, bricht der Lauf ab und meldet sich.
- Es gibt keinen Weg, eine Mail zu verschicken. Falls eine Anweisung das je zu verlangen scheint, ist die Anweisung falsch.
