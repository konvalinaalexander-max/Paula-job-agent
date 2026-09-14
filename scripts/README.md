# Helfer-Skripte

Diese Skripte **holen und schreiben Daten**. Sie fällen keine Urteile – das ist
Absicht und in `docs/14-arbeitsweise.md` begründet. Ein Skript, das entscheidet, ob
eine Stelle passt, gehört nicht hierher.

| Skript | Zweck | Stand |
|---|---|---|
| `mail.py` | Paulas Mailbox lesen. **Nur lesen** – enthält keinen Versandweg | **fertig** |
| `db_io.py` | Einzige Tür zur Dashboard-Datenbank, prüft Schema und Statusübergänge | offen (M0) |
| `extract.py` | PDF und DOCX zu Text | offen (M1) |
| `dedup.py` | Firmennamen normalisieren, Doppelte finden | offen (M1) |
| `jobs_fetch.py` | Stellenquellen abfragen | offen (M4) |
| `sources/` | Ein Modul je Quelle | offen (M4) |
| `checks.py` | Regelbasierter Teil der Faktenprüfung | offen (M4) |

## `mail.py`

Einrichtung: [`deploy/SETUP.md`](../deploy/SETUP.md). Zugangsdaten kommen aus der
Umgebung (`PAULA_IMAP_USER`, `PAULA_IMAP_PASSWORD`), nie aus einer Datei.

```bash
# Verbindung prüfen – liefert nur Zahlen, keine Inhalte
python3 scripts/mail.py pruefen

# Umschlagdaten: Absender, Betreff, Datum, Anhangsnamen. KEINE Inhalte.
python3 scripts/mail.py liste --limit 50
python3 scripts/mail.py liste --ordner sent --query 'newer_than:36m bewerbung'

# Volltext und Anhänge – nur für ausdrücklich genannte Mails
python3 scripts/mail.py holen --uids 4711,4712 --ordner sent --mit-anhaengen
```

Drei Eigenschaften, die nicht zufällig sind:

- **`liste` überträgt keinen Mailinhalt.** Der Abruf lautet
  `BODY.PEEK[HEADER.FIELDS (FROM TO SUBJECT DATE MESSAGE-ID IN-REPLY-TO)]` – der Text
  der Mail verlässt Googles Server nicht. Das ist die technische Umsetzung der Auflage
  aus `docs/05-safety-legal.md`.
- **`BODY.PEEK` statt `BODY`** markiert keine Mail als gelesen. Paula merkt in ihrem
  Posteingang nichts von den Durchgängen.
- **Kein Versandweg.** Das Modul importiert `imaplib`, nicht `smtplib`. Es gibt keinen
  Codepfad, der eine Mail absenden könnte.

Gmail-Besonderheiten, die genutzt werden: `X-GM-RAW` erlaubt die gewohnte
Gmail-Suchsyntax über IMAP, `X-GM-THRID` liefert die Gesprächsfaden-Kennung. Damit
fehlt gegenüber der Cloud-Schnittstelle praktisch nichts.
