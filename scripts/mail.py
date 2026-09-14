"""Paulas Mailbox lesen. NUR LESEN – dieses Modul kennt keinen Versandweg.

Verbindet sich über IMAP mit Gmail und nutzt dabei die Gmail-Erweiterungen
(X-GM-RAW für die gewohnte Gmail-Suchsyntax, X-GM-THRID für Gesprächsfäden).

Zwei Betriebsarten, entsprechend der Datensparsamkeits-Auflage aus
docs/05-safety-legal.md:

  --list    holt NUR Umschlagdaten: Absender, Betreff, Datum, Anhangsnamen.
            Der Inhalt der Mails wird nicht übertragen.
  --fetch   holt Volltext und Anhänge – nur für ausdrücklich genannte Mails,
            also nur für solche, die vorher als bewerbungsbezogen erkannt wurden.

Zugangsdaten kommen aus der Umgebung (nie aus einer Datei im Repo):
  PAULA_IMAP_USER      ihre Mailadresse
  PAULA_IMAP_PASSWORD  das App-Passwort aus ihrem Google-Konto
  PAULA_IMAP_HOST      optional, Vorgabe imap.gmail.com

Ausgabe ist immer JSON auf der Standardausgabe.
"""

from __future__ import annotations

import argparse
import email
import email.header
import email.utils
import imaplib
import json
import os
import re
import sys
from datetime import datetime, timezone

IMAP_HOST = os.environ.get("PAULA_IMAP_HOST", "imap.gmail.com")
IMAP_PORT = 993
MAX_BODY_CHARS = 8000

imaplib._MAXLINE = 10_000_000  # Gmail schickt bei großen Postfächern lange Zeilen


# ---------------------------------------------------------------- Verbindung

class Mailbox:
    """Dünne Hülle um imaplib. Öffnet ausschließlich eine Lese-Verbindung."""

    def __init__(self, user: str, password: str, host: str = IMAP_HOST):
        self.user, self.password, self.host = user, password, host
        self.conn: imaplib.IMAP4_SSL | None = None

    def __enter__(self) -> "Mailbox":
        self.conn = imaplib.IMAP4_SSL(self.host, IMAP_PORT)
        try:
            self.conn.login(self.user, self.password)
        except imaplib.IMAP4.error as e:
            raise SystemExit(_login_hilfe(e)) from None
        return self

    def __exit__(self, *exc):
        if self.conn:
            try:
                self.conn.logout()
            except Exception:
                pass

    def ordner(self) -> dict[str, str]:
        """Findet Posteingang und Gesendet-Ordner über ihre Sonderrollen,
        damit die Sprache der Oberfläche keine Rolle spielt."""
        gefunden = {"inbox": "INBOX", "sent": None, "all": None}
        typ, zeilen = self.conn.list()
        if typ != "OK":
            return gefunden
        for roh in zeilen:
            zeile = roh.decode(errors="replace")
            name = zeile.split(' "/" ')[-1].strip().strip('"')
            if "\\Sent" in zeile:
                gefunden["sent"] = name
            elif "\\All" in zeile:
                gefunden["all"] = name
        return gefunden

    def suchen(self, ordner: str, gmail_query: str) -> list[bytes]:
        """Sucht mit Gmail-Syntax (X-GM-RAW) und gibt UIDs zurück."""
        typ, _ = self.conn.select(f'"{ordner}"', readonly=True)
        if typ != "OK":
            return []
        typ, daten = self.conn.uid("SEARCH", "X-GM-RAW", _quote(gmail_query))
        if typ != "OK" or not daten or not daten[0]:
            return []
        return daten[0].split()


def _quote(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _login_hilfe(fehler: Exception) -> str:
    return (
        f"Anmeldung fehlgeschlagen: {fehler}\n\n"
        "Häufige Ursachen:\n"
        "  · Das App-Passwort wurde mit Leerzeichen kopiert – die gehören weg.\n"
        "  · Die Zwei-Faktor-Anmeldung ist im Google-Konto nicht aktiv. Ohne sie\n"
        "    gibt es keine App-Passwörter.\n"
        "  · Das App-Passwort wurde widerrufen oder das Kontopasswort geändert –\n"
        "    dann verfallen alle App-Passwörter und es braucht ein neues.\n"
        "  · PAULA_IMAP_USER ist nicht die vollständige Mailadresse.\n"
    )


# ------------------------------------------------------------------ Parsen

def _text(roh) -> str:
    """Dekodiert einen Kopfzeilenwert in lesbaren Text."""
    if roh is None:
        return ""
    if isinstance(roh, bytes):
        roh = roh.decode("utf-8", errors="replace")
    teile = []
    for wert, kodierung in email.header.decode_header(str(roh)):
        if isinstance(wert, bytes):
            teile.append(wert.decode(kodierung or "utf-8", errors="replace"))
        else:
            teile.append(wert)
    return "".join(teile).strip()


def _adresse(feld) -> tuple[str, str]:
    """(Name, Adresse) aus einem ENVELOPE-Adressfeld."""
    if not feld:
        return "", ""
    name, _, konto, wirt = feld[0]
    return (
        _text(name),
        f"{(konto or b'').decode(errors='replace')}@{(wirt or b'').decode(errors='replace')}".strip("@"),
    )


def _iso(datum: str | None) -> str | None:
    if not datum:
        return None
    try:
        dt = email.utils.parsedate_to_datetime(datum)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc).isoformat()
    except Exception:
        return None


ZITAT_MUSTER = [
    re.compile(r"^\s*>.*$", re.M),
    re.compile(r"^\s*Am .{5,60} schrieb .{1,80}:\s*$", re.M),
    re.compile(r"^\s*On .{5,60} wrote:\s*$", re.M),
    re.compile(r"^-{2,}\s*(Urspr[üu]ngliche Nachricht|Original Message|Weitergeleitete Nachricht)", re.M | re.I),
    re.compile(r"^_{5,}\s*$", re.M),
]


def bereinigen(text: str) -> str:
    """Entfernt Zitatketten und Signatur, kürzt auf MAX_BODY_CHARS."""
    for muster in ZITAT_MUSTER[1:]:
        treffer = muster.search(text)
        if treffer:
            text = text[: treffer.start()]
    text = ZITAT_MUSTER[0].sub("", text)
    # Signatur nach einer Zeile mit genau "--"
    sig = re.search(r"^--\s*$", text, re.M)
    if sig:
        text = text[: sig.start()]
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return text[:MAX_BODY_CHARS]


def html_zu_text(html: str) -> str:
    html = re.sub(r"(?is)<(script|style).*?</\1>", " ", html)
    html = re.sub(r"(?i)<br\s*/?>", "\n", html)
    html = re.sub(r"(?i)</(p|div|tr|li|h[1-6])>", "\n", html)
    text = re.sub(r"<[^>]+>", " ", html)
    for roh, ersatz in (("&nbsp;", " "), ("&amp;", "&"), ("&lt;", "<"),
                        ("&gt;", ">"), ("&quot;", '"'), ("&#39;", "'")):
        text = text.replace(roh, ersatz)
    return re.sub(r"[ \t]{2,}", " ", text)


# ------------------------------------------------------------------ Befehle

def befehl_pruefen(args) -> dict:
    """Verbindungstest. Verrät nur Zahlen, keine Inhalte."""
    with Mailbox(args.user, args.password) as mb:
        ordner = mb.ordner()
        ergebnis = {"verbindung": "ok", "konto": args.user, "ordner": ordner}
        probe = 'newer_than:30d (bewerbung OR application OR absage OR lebenslauf)'
        for rolle in ("inbox", "sent"):
            name = ordner.get(rolle)
            if not name:
                continue
            ergebnis[f"treffer_{rolle}_30d"] = len(mb.suchen(name, probe))
        mb.conn.select('"INBOX"', readonly=True)
        typ, daten = mb.conn.uid("SEARCH", "ALL")
        ergebnis["mails_im_posteingang"] = len(daten[0].split()) if typ == "OK" and daten[0] else 0
        return ergebnis


def befehl_liste(args) -> dict:
    """Umschlagdaten. Holt NUR die genannten Kopfzeilen und die Anhangsnamen –
    der Inhalt der Mails wird nicht übertragen. BODY.PEEK sorgt außerdem dafür,
    dass keine Mail als gelesen markiert wird."""
    felder = "(FROM TO SUBJECT DATE MESSAGE-ID IN-REPLY-TO)"
    abruf = f"(UID X-GM-MSGID X-GM-THRID BODYSTRUCTURE BODY.PEEK[HEADER.FIELDS {felder}])"

    with Mailbox(args.user, args.password) as mb:
        ordner = mb.ordner()
        ziele = []
        if args.ordner in ("beide", "inbox"):
            ziele.append(("in", ordner["inbox"]))
        if args.ordner in ("beide", "sent") and ordner["sent"]:
            ziele.append(("out", ordner["sent"]))

        gesamt, fehler = [], 0
        for richtung, name in ziele:
            uids = mb.suchen(name, args.query)
            if args.limit:
                uids = uids[-args.limit:]
            for block in _bloecke(uids, 50):
                typ, daten = mb.conn.uid("FETCH", b",".join(block), abruf)
                if typ != "OK":
                    fehler += len(block)
                    continue
                for eintrag in daten:
                    kopf = _umschlag(eintrag, richtung, name)
                    if kopf:
                        gesamt.append(kopf)

        gesamt.sort(key=lambda m: m.get("datum") or "", reverse=True)
        return {
            "anzahl": len(gesamt),
            "nicht_abrufbar": fehler,
            "abfrage": args.query,
            "durchsuchte_ordner": [n for _, n in ziele],
            "hinweis": "Nur Umschlagdaten. Kein Mailinhalt wurde übertragen.",
            "mails": gesamt,
        }


def _umschlag(eintrag, richtung: str, ordner: str) -> dict | None:
    """Wertet eine FETCH-Antwort aus: Kennungen aus dem Vorspann,
    Kopfzeilen aus dem mitgelieferten Header-Block."""
    if not isinstance(eintrag, tuple) or len(eintrag) < 2:
        return None
    vorspann = eintrag[0].decode(errors="replace") if isinstance(eintrag[0], bytes) else str(eintrag[0])
    kopfzeilen = eintrag[1] if isinstance(eintrag[1], bytes) else b""

    kopf = email.message_from_bytes(kopfzeilen)
    von_name, von = _parse_adresse(kopf.get("From"))
    an_name, an = _parse_adresse(kopf.get("To"))

    def kennung(name: str) -> str | None:
        treffer = re.search(rf"{name} (\d+)", vorspann)
        return treffer.group(1) if treffer else None

    return {
        "uid": kennung("UID"),
        "gmail_message_id": kennung("X-GM-MSGID"),
        "gmail_thread_id": kennung("X-GM-THRID"),
        "richtung": richtung,
        "ordner": ordner,
        "von": von,
        "von_name": von_name,
        "an": an,
        "an_name": an_name,
        "betreff": _text(kopf.get("Subject")),
        "datum": _iso(kopf.get("Date")),
        "message_id": (kopf.get("Message-ID") or "").strip(),
        "in_reply_to": (kopf.get("In-Reply-To") or "").strip(),
        "anhangsnamen": _anhangsnamen_aus_vorspann(vorspann),
    }


DATEINAME_MUSTER = re.compile(
    r'(?:FILENAME|NAME)"?\s+"([^"]{1,200})"', re.I)


def _anhangsnamen_aus_vorspann(vorspann: str) -> list[str]:
    """Zieht Dateinamen aus der BODYSTRUCTURE-Antwort, ohne die Dateien zu holen."""
    namen, gesehen = [], set()
    for treffer in DATEINAME_MUSTER.finditer(vorspann):
        name = _text(treffer.group(1))
        if name and name.lower() not in gesehen and not name.lower().startswith("utf-8"):
            gesehen.add(name.lower())
            namen.append(name)
    return namen


def befehl_holen(args) -> dict:
    """Volltext und Anhangsnamen – nur für ausdrücklich genannte Mails."""
    uids = [u.strip() for u in args.uids.split(",") if u.strip()]
    with Mailbox(args.user, args.password) as mb:
        ordner = mb.ordner()
        name = ordner["sent"] if args.ordner == "sent" and ordner["sent"] else ordner["inbox"]
        mb.conn.select(f'"{name}"', readonly=True)
        ergebnisse = []
        for uid in uids:
            typ, daten = mb.conn.uid("FETCH", uid, "(RFC822)")
            if typ != "OK" or not daten or not isinstance(daten[0], tuple):
                ergebnisse.append({"uid": uid, "fehler": "nicht abrufbar"})
                continue
            ergebnisse.append(_mail_auswerten(uid, daten[0][1], args.mit_anhaengen))
        return {"anzahl": len(ergebnisse), "mails": ergebnisse}


def _mail_auswerten(uid: str, roh: bytes, mit_anhaengen: bool) -> dict:
    nachricht = email.message_from_bytes(roh)
    von_name, von_adresse = _parse_adresse(nachricht.get("From"))
    an_name, an_adresse = _parse_adresse(nachricht.get("To"))

    text, html, anhaenge = "", "", []
    for teil in nachricht.walk():
        if teil.is_multipart():
            continue
        art = teil.get_content_type()
        verfuegung = str(teil.get("Content-Disposition") or "")
        dateiname = teil.get_filename()
        if dateiname or "attachment" in verfuegung:
            eintrag = {
                "dateiname": _text(dateiname) if dateiname else "(ohne Namen)",
                "typ": art,
                "groesse": len(teil.get_payload(decode=True) or b""),
            }
            if mit_anhaengen:
                import base64
                inhalt = teil.get_payload(decode=True) or b""
                eintrag["inhalt_base64"] = base64.b64encode(inhalt).decode()
            anhaenge.append(eintrag)
        elif art == "text/plain" and not text:
            text = (teil.get_payload(decode=True) or b"").decode(
                teil.get_content_charset() or "utf-8", errors="replace")
        elif art == "text/html" and not html:
            html = (teil.get_payload(decode=True) or b"").decode(
                teil.get_content_charset() or "utf-8", errors="replace")

    koerper = text if text.strip() else html_zu_text(html)
    return {
        "uid": uid,
        "message_id": (nachricht.get("Message-ID") or "").strip(),
        "in_reply_to": (nachricht.get("In-Reply-To") or "").strip(),
        "betreff": _text(nachricht.get("Subject")),
        "von_name": von_name, "von": von_adresse,
        "an_name": an_name, "an": an_adresse,
        "datum": _iso(nachricht.get("Date")),
        "text": bereinigen(koerper),
        "text_gekuerzt": len(koerper) > MAX_BODY_CHARS,
        "anhaenge": anhaenge,
    }


def _parse_adresse(feld) -> tuple[str, str]:
    if not feld:
        return "", ""
    name, adresse = email.utils.parseaddr(str(feld))
    return _text(name), adresse.lower()


def _bloecke(folge, groesse):
    for i in range(0, len(folge), groesse):
        yield folge[i:i + groesse]


# -------------------------------------------------------------------- Start

def main() -> int:
    p = argparse.ArgumentParser(description="Paulas Mailbox lesen (nur lesen).")
    p.add_argument("befehl", choices=["pruefen", "liste", "holen"])
    p.add_argument("--query", default='newer_than:36m (bewerbung OR bewerbungsunterlagen OR '
                                      '"ihre bewerbung" OR absage OR einladung OR lebenslauf OR '
                                      'motivationsschreiben OR application OR interview OR stelle)')
    p.add_argument("--ordner", choices=["beide", "inbox", "sent"], default="beide")
    p.add_argument("--limit", type=int, default=0, help="0 = ohne Begrenzung")
    p.add_argument("--uids", default="", help="Kommaliste, nur für 'holen'")
    p.add_argument("--mit-anhaengen", action="store_true")
    args = p.parse_args()

    args.user = os.environ.get("PAULA_IMAP_USER", "")
    args.password = (os.environ.get("PAULA_IMAP_PASSWORD", "") or "").replace(" ", "")
    if not args.user or not args.password:
        print(json.dumps({
            "fehler": "Zugangsdaten fehlen",
            "hinweis": "PAULA_IMAP_USER und PAULA_IMAP_PASSWORD müssen in der Umgebung stehen. "
                       "Anleitung: deploy/SETUP.md",
        }, ensure_ascii=False, indent=2))
        return 2

    funktion = {"pruefen": befehl_pruefen, "liste": befehl_liste, "holen": befehl_holen}[args.befehl]
    ergebnis = funktion(args)
    ergebnis["_zeitpunkt"] = datetime.now(timezone.utc).isoformat()
    print(json.dumps(ergebnis, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
