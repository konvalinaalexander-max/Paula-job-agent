# Anweisungen für die ausführende KI

Du setzt das Projekt "Paula Job Agent" um. Der Plan liegt vollständig in `docs/`. Dieses Dokument sagt dir, **wie** du arbeitest. Der Plan sagt, **was** du baust.

> **Version 2** (13.09.2026). Grundlegend überarbeitet: Land ist Österreich, das System verschickt keine Mails mehr, Paula bekommt ein Dashboard statt Telegram, und ihr Profil wird aus ihrer Mailbox erarbeitet statt abgefragt. Wenn du etwas aus einer älteren Fassung im Kopf hast: die Docs gelten.

## Wer hier wer ist

- **Auftraggeber (Alexander):** dein Ansprechpartner. Er programmiert nicht. Erkläre kurz und ohne Fachjargon. Frag ihn bei den als *blockierend* markierten Fragen in `docs/08-open-questions.md`.
- **Nutzerin (Paula):** sucht dringend Arbeit und ist offen für vieles. Sie sieht ausschließlich das Dashboard (`docs/10-dashboard.md`). Kein Repo, keine Konsole, kein Chat.

## Die eine Regel, aus der alles folgt

**Das System verschickt nichts. Es bereitet vor.**

Gmail ist ausschließlich lesend angebunden (`gmail.readonly`). Es gibt keinen Versandweg, keinen SMTP-Zugang, keinen Sende-Knopf. Paula kopiert den Text und schickt ihn aus ihrem eigenen Mailprogramm ab.

Wenn dir je eine Aufgabe begegnet, die Versand zu verlangen scheint, ist die Aufgabe falsch verstanden. Baue keinen Versand – auch nicht "nur zum Testen", auch nicht hinter einem Schalter.

## Weitere harte Regeln

1. **Keine erfundenen Fakten.** Aussagen über Paula stammen ausschließlich aus `profile/facts`. Die Prüfung U9 läuft vor jeder Karte. Widersprüche zwischen ihren Lebenslauf-Fassungen werden **ihr vorgelegt**, nie geraten.
2. **Datensparsamkeit.** Der breite Durchgang durch die Mailbox sieht nur Absender, Betreff, Datum und Anhangsnamen (`format=metadata`). Inhalte nur bei Bewerbungsbezug. Von allem anderen bleibt nur die Kennnummer. Das ist eine ausdrückliche Auflage des Auftraggebers.
3. **Nichts Personenbezogenes ins Repo.** Keine Mails, keine Lebensläufe, keine Namen, keine Zugangsdaten. Das gehört in die Dashboard-Datenbank bzw. in die Geheimnisse der Umgebung. Vor jedem Commit `git status` prüfen.
4. **Alles durch `scripts/db_io.py`.** Es ist die einzige Tür zur Datenbank und prüft Schema und Statusübergänge. Umgehe es nicht, auch nicht "kurz".
5. **Jeder Lauf ist wiederholbar.** Fortschritt in `state/`, Abgleich über Fingerabdrücke und `seen`. Ein zweiter Lauf darf nichts verdoppeln.
6. **Portale nur auf vorgesehenen Wegen.** Offizielle Schnittstellen und E-Mail-Suchaufträge ja. Auslesen gegen die Nutzungsbedingungen nur nach ausdrücklicher Entscheidung (Q8).
7. **Der Container ist nach dem Lauf weg.** Was erhalten bleiben soll, gehört in die Datenbank. Keine lokalen Dateien als Gedächtnis.

## Aufbau

```
scripts/     Helfer: Daten holen, Daten schreiben. Keine Urteile.
runbooks/    Arbeitsanweisungen für die Sessions. Hier stehen die Abläufe.
dashboard/   Die Seite, die Paula sieht.
docs/        Der Plan.
tests/       Tests und erfundene Beispieldaten.
config/      Listen (Rechtsformen, Personalvermittler) und Einstellungen.
```

Die Trennung zwischen `scripts/` und den Urteilen ist Absicht: Skripte holen und schreiben, **du** beurteilst. Ein Skript, das entscheidet, ob eine Stelle passt, gehört nicht ins Repo. Eine Beurteilung, die eine Mail abruft, auch nicht.

## Werkzeuge

- **Python 3.12** für die Skripte. Abhängigkeiten in `pyproject.toml`. Kein Anthropic-SDK, kein Agent-Framework, keine Datenbank-Bibliothek.
- **Die Datenbank des Dashboards** über `read_db` / `write_db`.
- **Deine eigene Urteilskraft** für alles unter U1–U12 in `docs/03-llm-tasks.md`.

## Reihenfolge

`docs/07-milestones.md`, M0 bis M7, strikt nacheinander. Jede Etappe endet mit einer Abnahme durch Menschen – frag ausdrücklich danach, bevor du weitergehst.

Innerhalb einer Etappe: erst die Skripte, dann die Urteile, dann die Tests, dann die Doku.

## Arbeitsweise

- **Lies die betroffenen Docs vollständig**, bevor du eine Etappe beginnst. Sie sind ausführlich, und das ist Absicht.
- **Wo der Plan etwas offen lässt:** entscheide, trag es in `docs/01-architecture.md` unter "Entscheidungen während der Umsetzung" ein, mach weiter.
- **Wo der Plan falsch liegt** (Schnittstelle weg, Bibliothek kaputt): nach `docs/09-research-notes.md` unter "Abweichungen", nächstbeste Lösung aus dem Plan nehmen, im Etappenbericht erwähnen.
- **Kleine Commits**, ein Thema pro Commit, deutsche Commit-Nachrichten. Kein Modellname in Commits, Code oder Kommentaren.
- **Kein Feature-Creep.** Gute Ideen kommen nach `docs/08-open-questions.md` unter "Vorschläge", nicht in den Code.
- **Prüffälle durchspielen** (`docs/11-testing.md`), Ergebnis nach `tests/judgements/`.

## Etappenbericht

Nach jeder Etappe, kurz:

1. Was gebaut wurde – drei bis sechs Sätze, verständlich ohne Programmierkenntnisse
2. Wie Alexander es selbst ausprobiert – konkrete Befehle
3. Was von ihm gebraucht wird, um weiterzumachen
4. Abweichungen vom Plan und warum
5. Die Frage nach der Abnahme

## Was du nicht tust

- Keinen Versand, in keiner Form (siehe oben)
- Keine Formular-Automatik auf Bewerbungsportalen
- Keine Änderung an `profile/facts` oder `profile/style` ohne Paulas Bestätigung über das Dashboard
- Keine Erweiterung der Gmail-Berechtigung über `gmail.readonly` hinaus
- Keine Bewerbung bei Firmen mit `blocked: true`
- Keine echten Daten in `tests/`
