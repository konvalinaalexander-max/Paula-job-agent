# 10 – Telegram: Der komplette Dialog mit Paula

Paula sieht **nur** das hier. Jede Nachricht, die das System ihr schickt, und jede Eingabe, die es versteht, ist in diesem Dokument. Wenn etwas hier nicht steht, existiert es für sie nicht.

Tonfall: freundlich, kurz, Du-Form (offene Frage Q10 – Default Du), keine Technik-Wörter (kein "Score", "LLM", "Pipeline", "Approval"). Emojis sparsam und immer dieselben (Legende unten).

## Emoji-Legende (konsistent verwenden)

📬 neue Stelle · ✉️ Spontanbewerbung · 💬 Antwort einer Firma · 🎉 Einladung/Zusage · 😔 Absage · ❓ Rückfrage · ✅ gesendet · ✏️ ändern · ❌ verworfen · ⏸ pausiert · ⚠️ prüfen · 📊 Status

## Befehle (bei BotFather registrieren)

```
start   – Bot starten / verbinden
status  – Was läuft gerade, was wartet auf dich
list    – Offene Bewerbungen (gesendet, ohne Antwort)
pause   – Vorschläge pausieren (du kannst jederzeit weitermachen)
resume  – Weiter geht's
block   – Eine Firma dauerhaft ausschließen
add     – Eine Stelle einreichen (Link oder Text)
report  – Deine Wochenübersicht
settings – Wie viele Vorschläge pro Tag u. ä.
help    – Diese Liste
stop    – Alles beenden (nur Alexander kann wieder einschalten)
```

Admin-Befehle (nur Alexander, nicht in der öffentlichen Liste): `/kill`, `/unkill`, `/costs`, `/errors`, `/run scan|portals|companies|replies`, `/debug <application_id>`.

## Flow 0 – Erster Kontakt

Paula: `/start`

Bot (chat_id noch nicht konfiguriert):
> Hallo! Ich bin die Bewerbungshilfe, die Alexander für dich eingerichtet hat. Ich hab deine Kennung notiert (`123456789`) – Alexander muss sie noch freischalten, dann melde ich mich.

Bot (nach Freischaltung, beim nächsten `/start` oder proaktiv):
> Hallo Paula 👋 Ich bin jetzt für dich da.
>
> So funktioniert's: Ich schaue mehrmals täglich nach Stellen, die zu dir passen, und schreibe dir einen Entwurf für die Bewerbung – in deinem Stil, nur mit dem, was in deinem Lebenslauf steht. **Ich schicke nie etwas ab, ohne dass du auf ✅ drückst.**
>
> Wenn eine Firma antwortet, sag ich dir Bescheid und schlage eine Antwort vor.
>
> Du kannst jederzeit /pause schreiben, dann bin ich still. Mit /help siehst du alles, was ich kann.
>
> Soll ich loslegen? [🚀 Ja, los] [Erst mal /status zeigen]

## Flow 1 – Vorschlag Portal-Stelle (Karte A)

Nachricht 1 (Kontext):
> 📬 **Neue Stelle – passt gut zu dir**
> **Projektassistenz 60–80 %**
> Muster AG, Winterthur · veröffentlicht vor 1 Tag
> Quelle: jobs.ch → [Inserat öffnen](url)
>
> **Warum ich das vorschlage:** Du hast drei Jahre Assistenzerfahrung im Bau, die Stelle verlangt genau das, und Winterthur ist in deinem Radius.
>
> **Bedenken:** Sie wünschen Französisch B2 – in deinem Lebenslauf steht B1.
>
> ⚠️ Du hattest dich vermutlich im März 2025 bei Muster AG beworben (bin nicht ganz sicher).  ← nur wenn zutreffend

Nachricht 2 (Entwurf + Buttons):
> **Betreff:** Bewerbung als Projektassistentin
>
> Sehr geehrte Frau Beispiel
>
> [voller Text, exakt so, wie er rausgeht]
>
> Freundliche Grüsse
> Paula Muster
>
> 📎 Lebenslauf_Paula_Muster.pdf, Zeugnisse.pdf
> An: bewerbung@muster.ch
>
> [✅ So senden] [✏️ Ändern] [❌ Nein danke]
> [💤 Später] [🚫 Firma nie wieder]

Buttons → Callbacks:
- ✅ `a:<id>:ok` → Bot: "✅ Wird gesendet…" → nach Versand Karte editiert: "✅ Gesendet um 09:14 an bewerbung@muster.ch". Außerhalb Sendefenster: "✅ Freigegeben – geht morgen um 8:00 raus."
- ✏️ `a:<id>:rev` → Flow 2
- ❌ `a:<id>:no` → Karte editiert "❌ Verworfen". Wenn `reject_count` der Firma jetzt ≥ 2: Zusatzfrage "Soll ich Muster AG in Zukunft ganz weglassen? [Ja] [Nein]"
- 💤 `a:<id>:snz` → "Ok, ich erinnere dich in 2 Tagen." (`approvals.expires_at` +2d, `reminder_sent_at` zurücksetzen)
- 🚫 `a:<id>:blk` → "Muster AG kommt nicht mehr vor. Rückgängig mit /block." + Karte editiert.

Erinnerung nach 3 Tagen ohne Reaktion:
> ⏰ Der Vorschlag für **Projektassistenz bei Muster AG** wartet noch auf dich. Das Inserat ist noch online. [Nochmal zeigen] [❌ Weg damit]

Nach 7 Tagen: automatisch `expired`, Karte editiert "⌛ Abgelaufen", keine weitere Nachricht.

## Flow 2 – Ändern

Bot (nach ✏️):
> Was soll ich ändern? Schreib's einfach, z. B. "kürzer", "weniger förmlich", "erwähn meine Zeit bei Firma X".
> (Oder schick mir den Text gleich fertig, dann nehm ich deinen.)

Paula: "kürzer und nicht so steif, und lass den Satz mit Französisch weg"

Bot: "✏️ Mach ich…" → T11 → T8 → neue Karte (nur Nachricht 2, mit Zeile oben: "**Version 2** – Gekürzt, lockerer, Französisch-Satz entfernt.") + dieselben Buttons.

Wenn Paulas Feedback einen neuen Fakt enthält:
> Du erwähnst "2 Jahre in Wien" – das steht nicht in deinen Unterlagen. Ich lass es in diesem Entwurf weg, damit nichts Falsches rausgeht. Soll Alexander es in deine Fakten aufnehmen? [Ja, bitte] [Nein]

Nach 3 Runden:
> Ich glaub, ich treff's nicht ganz. Magst du mir den Text so schicken, wie du ihn willst? Ich prüfe ihn dann nur noch auf Fakten und schick ihn dir zum Freigeben zurück.

Timeout (30 min ohne Antwort): State wird gelöscht; nächste Textnachricht von Paula wird als normales Kommando behandelt. Karte bleibt mit Buttons.

## Flow 3 – Vorschlag Spontanbewerbung (Karte B)

Wie Karte A, aber:
> ✉️ **Spontanbewerbung – Idee**
> **Bauleitung Meier GmbH**, Frauenfeld · ~40 Mitarbeitende
> Was sie machen: Hochbau und Renovationen in der Ostschweiz, seit 1987.
>
> **Warum gerade die:** Sie haben letzten Monat eine zweite Niederlassung in Wil eröffnet und suchen laut ihrer Website "laufend" Verstärkung im Büro. Sie schreiben auf ihrer Seite ausdrücklich, dass Initiativbewerbungen willkommen sind.
>
> An: personal@meier-bauleitung.ch (von ihrer Karriereseite)
> Gefunden: [Karriereseite](url)

Buttons identisch. Zusätzlich, wenn `accepts_spontaneous=unknown`: Zeile "ℹ️ Ob sie Spontanbewerbungen mögen, steht nirgends – kann sich lohnen, muss nicht."

## Flow 4 – Antwort einer Firma

### Absage
> 😔 **Absage von Muster AG** (Projektassistenz, beworben am 3. Sept.)
> „…haben wir uns für eine andere Kandidatin entschieden…"
>
> Vorschlag für eine kurze Antwort:
> ---
> [Entwurf]
> ---
> [✅ Senden] [✏️ Ändern] [🤐 Nicht antworten]

### Einladung
> 🎉 **Einladung zum Gespräch – Muster AG!**
> Sie schlagen vor: **Di 16. Sept 14:00** oder **Do 18. Sept 10:00**, vor Ort in Winterthur.
> Kontakt: Frau Beispiel, 052 123 45 67
>
> Wenn du mir sagst, welcher Termin passt, bereite ich die Zusage vor:
> [Di 14:00] [Do 10:00] [Anderer Termin] [Ich antworte selbst]

Nach Wahl → Entwurf mit eingesetztem Termin → Karte mit ✅/✏️. Einladungen werden **sofort** geschickt, auch wenn Paula pausiert hat (Pause betrifft nur Vorschläge) und unabhängig vom Tageslimit.

### Rückfrage
> ❓ **Rückfrage von Muster AG**
> Sie fragen: „Ab wann wären Sie verfügbar, und haben Sie Erfahrung mit SAP?"
>
> Vorschlag (Verfügbarkeit hab ich aus deinen Unterlagen genommen):
> ---
> [Entwurf mit Verfügbarkeit beantwortet]
> ❓ **SAP-Erfahrung** steht nicht in deinen Unterlagen – bitte selbst ergänzen oder mir sagen.
> ---
> [✏️ Ergänzen] [Ich antworte selbst]

(Kein ✅ direkt, weil unvollständig. Erst nach Ergänzung erscheint ✅.)

### Zusage / Angebot
> 🎉🎉 **Muster AG will dich!** Sie schreiben von einem Vertragsangebot. Das besprichst du am besten selbst – ich halte mich hier raus. Hier die Mail: [Auszug]. Sag mir mit /list, wenn ich die Bewerbung als abgeschlossen markieren soll.

### Eingangsbestätigung
Keine Nachricht. Nur Status-Update (sichtbar in /list).

### Unklar (`needs_human`)
> 💬 **Mail von Muster AG** – ich bin nicht sicher, was sie wollen: „[Auszug]". Magst du reinschauen? [Ist eine Absage] [Ist eine Einladung] [Ist was anderes] [Egal, ignorieren]

## Flow 5 – /status
> 📊 **Stand heute**
> • 2 Vorschläge warten auf dich (↑ oben im Chat)
> • 7 Bewerbungen laufen (gesendet, noch keine Antwort)
> • 1 Gespräch steht an: Muster AG, Di 16.9. 14:00
> • Diese Woche: 4 gesendet, 1 Absage, 1 Einladung
> • Nächste Suche: heute 17:00

## Flow 6 – /list
Kompakte Liste, max. 15, älteste zuerst:
> **Laufend (7)**
> 1. Muster AG – Projektassistenz – gesendet 3.9. – keine Antwort (8 Tage)
> 2. …
> Tipp: Bei Nr. 1 ist es 4 Wochen her – soll ich nachfassen? [Ja] [Nein]  ← ab `no_reply_days`
>
> Zum Abschließen: `/close 1`

## Flow 7 – /pause · /resume · /stop
- `/pause` → "⏸ Ok, ich mach keine neuen Vorschläge. Antworten von Firmen zeig ich dir weiterhin. /resume wenn's weitergehen soll." (Optional: "[1 Woche] [2 Wochen] [Bis ich mich melde]")
- `/resume` → "▶️ Weiter geht's. Nächste Suche: heute 17:00."
- `/stop` → "⏹ Alles gestoppt. Ich schicke nichts mehr und suche nichts mehr. Wenn du wieder willst, sag Alexander Bescheid." → `settings_runtime.stopped=1`, Admin-Info.

## Flow 8 – /block
> Welche Firma? Schreib den Namen.
Paula: "Muster AG"
> Meinst du **Muster AG, Winterthur**? [Ja, sperren] [Andere] · Oder: aktuelle Sperrliste anzeigen [Liste]
Sperrliste zeigt Einträge mit [Entsperren]-Buttons.

## Flow 9 – /add
> Schick mir den Link zur Stelle (oder kopier den Text rein).
Paula: [URL]
> Hab's. Ich schau's mir beim nächsten Durchgang an (spätestens 17:00) und melde mich mit einem Entwurf – oder sag dir, warum's nicht passt.

Wenn Paula einfach einen Link ohne /add schickt → gleiches Verhalten.

## Flow 10 – /settings
> **Deine Einstellungen**
> • Vorschläge pro Tag: 3 [−] [+]
> • Spontanbewerbungen: an [aus]
> • Erinnerung nach: 3 Tagen
> • Ruhezeiten: nur Mo–Fr 8–18 Uhr
> • Pensum: 60–100 %  (ändern → sag's Alexander)
Nur die ersten drei sind von Paula direkt änderbar; Rest zeigt "sag's Alexander".

## Flow 11 – /report (wöchentlich automatisch Sonntagabend + auf Abruf)
> 📊 **Deine Woche (8.–14. Sept)**
> Gesendet: 5 (3 auf Inserate, 2 spontan)
> Antworten: 2 Absagen, 1 Einladung 🎉
> Laufend insgesamt: 9
> Verworfen von dir: 4 (davon 2× "zu weit weg" – soll ich den Radius kleiner machen? [Ja] [Nein])
> Seit Start: 23 gesendet, 4 Einladungen (17 %)

## Fehlerfälle, die Paula sieht

- Bot war offline, Paula hat geschrieben: Beim Neustart werden ungelesene Updates verarbeitet (Long-Polling holt sie nach). Keine gesonderte Nachricht.
- Versand fehlgeschlagen (Gmail-Fehler): "⚠️ Das Senden hat gerade nicht geklappt – ich versuch's in einer Stunde nochmal. Du musst nichts tun." Nach 3 Fehlversuchen → Admin, Paula: "Alexander schaut sich das an."
- Anhang fehlt: Kommt nicht vor – wird vor Karten-Erstellung geprüft (`send.py`-Prüfung 8 läuft auch vorab).

## Was Paula **nie** sieht

Modellnamen, Scores als Zahl, Token, Kosten, Fehlermeldungen mit Stacktrace, andere Firmen-Kandidaten, die unter dem Schwellwert lagen, Recherche-Rohdaten.
