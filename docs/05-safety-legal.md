# 05 – Sicherheit, Recht, Datenschutz

> **Version 2.** Durch den Wegfall des Versands ist dieses Kapitel deutlich kürzer geworden. Was übrig bleibt, ist umso wichtiger.

## 5.1 Was der Wegfall des Versands löst

| Problem in Version 1 | Status jetzt |
|---|---|
| Mail-Reputation, Spam-Verdacht, Blacklists | **Weg.** Paula sendet selbst, im menschlichen Tempo, aus ihrem Programm |
| Versehentlicher Versand durch Programmfehler | **Unmöglich.** Es gibt keinen Sendeweg. Gmail ist nur lesend angebunden |
| Rechtliche Frage „darf Software in ihrem Namen Erklärungen abgeben" | **Entfällt.** Jede Mail geht von ihrer Hand aus |
| Sendefenster, Tageslimits, Mindestabstände | **Entfallen.** Sie entscheidet, wann und wie viel |
| Zehn Sicherheitsprüfungen vor jedem Versand | **Entfallen.** |

Übrig bleiben drei Themen: Paulas Einwilligung, der sparsame Umgang mit ihrer Mailbox, und die Wahrheit in den Texten.

## 5.2 Einwilligung (Voraussetzung für Phase 0)

Der Auftraggeber hat bestätigt, dass Paula Bescheid weiß. Das reicht für den Start, sollte aber schriftlich festgehalten werden – nicht aus Formalismus, sondern weil sie wissen soll, was genau passiert. `docs/einwilligung.md` (in M0 zu erstellen) deckt ab:

1. **Was gelesen wird:** E-Mails der letzten 36 Monate. Beim ersten Durchgang **nur Absender, Betreff, Datum und Anhangsnamen** – keine Inhalte. Inhalte nur bei Mails, die erkennbar mit Bewerbungen zu tun haben.
2. **Was gespeichert wird:** Auszüge bewerbungsbezogener Mails, ihre Lebenslauf-Dateien, die daraus gewonnenen Profile, Firmen und Bewerbungen. Von allem anderen bleibt nur eine Kennnummer, damit es nicht erneut geprüft wird.
3. **Was nie passiert:** Es wird nichts in ihrem Namen verschickt. Die Zugriffsberechtigung erlaubt technisch nur Lesen.
4. **Wer es sieht:** Alexander als Betreiber. Die Verarbeitung läuft über Claude (Anthropic) – Mailauszüge, Inserate und ihr Lebenslauf werden dort verarbeitet.
5. **Ihre Kontrolle:** Sie kann den Zugriff jederzeit im Google-Konto entziehen (Sicherheit → Drittanbieter-Apps). Dann steht das System still. Auf Wunsch: vollständige Auskunft oder Löschung.
6. **Daten Dritter:** In ihrer Mailbox stehen Namen von Personalverantwortlichen. Diese werden nur im Bewerbungszusammenhang gespeichert und nicht anderweitig genutzt.

Technisch: `state/consent` muss gesetzt sein, sonst startet Phase 0 nicht.

## 5.3 Datensparsamkeit – die Auflage des Auftraggebers

„Schau, dass du ihre E-Mails ansonsten in Ruhe lässt – nichts speicherst, nichts analysierst."

So wird das umgesetzt:

| Schritt | Was gesehen wird | Was gespeichert wird |
|---|---|---|
| Erster Durchgang | Absender, Betreff, Datum, Anhangsnamen (`format=metadata` – der Inhalt wird gar nicht erst übertragen) | nur die Kennnummer in `seen` |
| Zweiter Durchgang, nur bei Bewerbungsbezug | Volltext, Anhänge | Auszug (max. 8.000 Zeichen), Lebenslauf-Dateien |
| Alles andere | nichts | nichts |

Zusätzlich: keine Roh-HTML-Fassungen, keine fremden Anhänge, keine Mailtexte in Protokollen. Protokolleinträge enthalten Kennnummern, keine Inhalte.

## 5.4 Wahrheit in den Texten

Die einzige verbliebene ernste Gefahr: dass eine Bewerbung eine Angabe enthält, die nicht stimmt. Das fällt auf Paula zurück, nicht auf die Software.

Drei Schichten:

1. **Der Faktenblock ist die einzige Quelle.** Er entsteht aus ihren eigenen, tatsächlich verschickten Lebensläufen – und Widersprüche zwischen den Fassungen werden ihr vorgelegt, statt aufgelöst zu raten.
2. **Getrennte Prüfung** jedes Textes gegen den Faktenblock (U9), regelbasiert plus urteilend. Erfundene Angaben blockieren die Karte.
3. **Paula liest jeden Text**, bevor sie ihn abschickt. Sie ist die letzte und beste Prüfung.

Neue Fakten, die sie im Änderungswunsch erwähnt, werden nie stillschweigend übernommen, sondern ausdrücklich nachgefragt.

## 5.5 Nutzungsbedingungen der Portale

| Quelle | Beurteilung |
|---|---|
| Adzuna-Schnittstelle | Offiziell vorgesehen |
| Job-Mails der Portale | Vom Portal selbst angeboten. Es sind **Paulas** Mails |
| Karriereseiten von Firmen | Öffentlich. `robots.txt` beachten, höchstens ein Abruf pro Sekunde je Domain, Kennung im User-Agent |
| AMS, karriere.at, willhaben direkt auslesen | Gegen die Bedingungen bzw. technisch abgesichert. **Nicht**, außer der Auftraggeber entscheidet ausdrücklich anders (Q8) |
| LinkedIn | **Nicht.** In keiner Form |

## 5.6 Fremde Inhalte als Angriffsfläche

Inserate und Mails können Anweisungen enthalten, die sich an die lesende KI richten. Schutz:

1. Fremdtext wird in der Session klar als Datenmaterial gekennzeichnet und nie als Anweisung behandelt; Auffälligkeiten kommen in `concerns`.
2. **Die Session kann ohnehin nichts Gefährliches tun:** kein Versand, keine Schreibrechte in Gmail, kein Geldausgeben. Der größte mögliche Schaden ist ein falsch bewertetes Inserat – und das sieht Paula.
3. Empfängeradressen werden gegen die Firmendomain geprüft. Eine Adresse, die nicht zur Firma passt, wird verworfen.
4. Testfälle mit eingebauten Anweisungen sind Pflicht.

## 5.7 Zugangsdaten

Gmail-Token, Adzuna-Schlüssel und Dashboard-Zugang liegen als Geheimnisse in der Umgebung, in der die Routine läuft – nie im Repo, nie in Protokollen, nie im Dashboard. Vor jedem Commit wird geprüft, dass nichts davon versehentlich erfasst wurde.

## 5.8 Notbremse

- **Paula:** entzieht dem Projekt im Google-Konto den Zugriff. Sofortige Wirkung, ohne dass jemand etwas tun muss.
- **Alexander:** schaltet die Routine ab. Oder setzt `state/phase.paused = true` – dann laufen die Sessions zwar, tun aber nichts.
- **Im Dashboard:** ein Schalter „Pause" für Paula. Bereits vorbereitete Bewerbungen bleiben sichtbar, es kommen keine neuen dazu.

Weil nichts verschickt wird, gibt es keinen Fall, den man nicht mehr rückgängig machen kann.
