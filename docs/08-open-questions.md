# 08 – Offene Fragen an den Auftraggeber

Mit **[BLOCKIEREND]** markierte Fragen müssen beantwortet sein, bevor die genannte Etappe beginnt. Alle anderen haben eine Default-Annahme, mit der die ausführende KI weiterarbeitet, bis eine Antwort kommt. Antworten bitte direkt hier eintragen (Abschnitt "Antwort").

---

### Q1 [BLOCKIEREND für M0] – Land und Region
In welchem Land / welcher Region sucht Paula? (Entscheidet Jobquellen, Firmenregister, Sprache, Rechtsformen, Schreibweise.)
**Vermutung aus dem Sprachgebrauch ("Spontanbewerbung", "gutheissen"):** Schweiz, Deutschschweiz.
**Default:** CH, `locale: de-CH`, Radius 40 km um einen noch zu nennenden Ort.
**Antwort:** _

### Q2 [BLOCKIEREND für M0] – Beruf, Zielrollen, Rahmen
Was macht Paula beruflich, welche Rollen sucht sie, welches Pensum, welche Branchen, was auf keinen Fall? Gibt es ihren Lebenslauf als PDF?
**Default:** keiner möglich – ohne das kann `profile.yaml` nicht gefüllt werden.
**Antwort:** _

### Q3 [BLOCKIEREND für M1] – Mailanbieter
Ist Paulas Bewerbungs-Mailadresse bei Gmail/Google? Wenn nicht: welcher Anbieter (Bluewin, GMX, Outlook, eigene Domain)? Nutzt sie **eine** Adresse für Bewerbungen oder mehrere?
**Default:** Gmail. Sonst IMAP-Fallback (4.2), was M1 um ~2 Tage verlängert.
**Antwort:** _

### Q4 [BLOCKIEREND für M1] – Einwilligung
Ist Paula grundsätzlich einverstanden, dass ein System ihre Mailbox liest und in ihrem Namen (nach Freigabe) sendet? Hat sie Telegram oder wäre sie bereit, es zu installieren?
**Default:** keiner. Ohne Ja gibt es kein Projekt.
**Antwort:** _

### Q5 – Budget
Was darf das monatlich kosten? Erwartung: ~5 € VPS + 20–45 $ LLM.
**Default:** `llm_budget_usd_per_day: 3`.
**Antwort:** _

### Q6 – Hosting
VPS (Hetzner o. ä., Betreiber bestellt) oder vorhandene Hardware (Raspberry Pi, Heimserver)? Wer bezahlt?
**Default:** Hetzner CX22, Standort Nürnberg.
**Antwort:** _

### Q7 – Welche Portale nutzt Paula heute?
Wo hat sie Konten / Suchagenten (jobs.ch, jobup.ch, job-room.ch, Indeed, LinkedIn, karriere.at, StepStone, …)? Dort richten wir E-Mail-Suchagenten ein (4.4.6).
**Default:** jobs.ch + job-room.ch Suchagenten einrichten; Adzuna CH als API-Quelle.
**Antwort:** _

### Q8 – Inoffizielles Scraping (Indeed/Google Jobs via JobSpy)
Diese Quellen verstoßen gegen AGB der Portale; Praxisrisiko für Privatnutzer gering, aber vorhanden. Sollen sie genutzt werden?
**Default:** Nein. Nur offizielle APIs, E-Mail-Alerts, Karriereseiten.
**Antwort:** _

### Q9 – Wer ist Admin?
Alexander allein? Zweite Person als Backup-Admin?
**Default:** nur Alexander.
**Antwort:** _

### Q10 – Anrede im Bot
Du oder Sie? Sprache Deutsch? Name des Bots?
**Default:** Du, Deutsch, "Paula Bewerbungshilfe".
**Antwort:** _

### Q11 – Sperrfrist und Nachfassen
Nach wie vielen Monaten darf dieselbe Firma wieder angeschrieben werden? Soll bei Funkstille nachgefasst werden, und nach wie vielen Wochen?
**Default:** 6 Monate; Nachfass-Vorschlag nach 4 Wochen (nur Vorschlag, Paula entscheidet).
**Antwort:** _

### Q12 – Off-Site-Backup
Wohin verschlüsselte Wochen-Backups? (Hetzner Storage Box ~4 €/Monat, eigener Rechner per rclone, gar nicht.)
**Default:** nur lokal auf dem VPS, 14 Tage. Off-Site in M8 nachrüsten.
**Antwort:** _

### Q13 – Sprachen der Bewerbungen
Nur Deutsch? Auch Französisch/Englisch, wenn das Inserat so ist? Wie gut spricht Paula diese Sprachen (steht im Faktenblock, aber die Regel "Bewerbung in Inseratssprache" braucht ein Minimum-Niveau)?
**Default:** Deutsch immer; FR/EN nur, wenn Faktenblock ≥ B2 ausweist; sonst Inserat trotzdem vorschlagen mit Hinweis "auf Französisch – willst du das?".
**Antwort:** _

### Q14 – Anhänge
Welche Dokumente gehen mit? (CV, Zeugnisse, Diplome, Foto?) Als ein PDF oder mehrere? Maximalgröße?
**Default:** `Lebenslauf.pdf` + `Zeugnisse.pdf`, gesamt ≤ 8 MB.
**Antwort:** _

### Q15 – Paulas Zeitfenster
Wann will Paula Vorschläge bekommen (nicht nachts, nicht am Wochenende)? Wie viele pro Tag maximal?
**Default:** Karten nur 08:00–20:00 Mo–Sa; max 3/Tag.
**Antwort:** _

### Q16 – Umgang mit Personalvermittlern
Bewerbungen über Adecco/Randstad/Manpower & Co. zulassen?
**Default:** Ja, mit Kennzeichnung in der Karte.
**Antwort:** _

---

## Vorschläge der ausführenden KI (Feature-Ideen außerhalb des Plans)

*(Hier einträgen statt bauen. Der Auftraggeber entscheidet.)*
