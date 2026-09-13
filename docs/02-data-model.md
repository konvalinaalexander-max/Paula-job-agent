# 02 – Datenmodell

> **Version 2.** Kein SQLite mehr. Die Daten liegen in der Dashboard-Datenbank: ein Dokumentspeicher mit JSON-Dokumenten unter Pfaden. Zugriff aus der Claude-Session über `read_db` / `write_db`, aus der Website über die eingebaute Datenbank-Schnittstelle.

## Grundregeln des Speichers

- Pfade sind `sammlung/dokument`, tiefer `sammlung/dokument/untersammlung/dokument`.
- Ein Dokument ist ein JSON-Objekt, **max. 256 KiB**. Bewerbungstexte passen mühelos; Mail-Volltexte werden auf 8.000 Zeichen gekürzt.
- Kein SQL, keine Joins. Verknüpfungen laufen über gespeicherte IDs.
- Kein Schema-Zwang seitens der Datenbank – die Struktur wird von `scripts/db_io.py` vor jedem Schreiben geprüft. Verstoß = Abbruch, nicht "schreib halt trotzdem".
- Letzter Schreiber gewinnt. Weil immer nur eine Session läuft und Paula nur Status-Felder ändert, ist das unkritisch.

## Sammlungen im Überblick

| Pfad | Inhalt | Anzahl (Erwartung) |
|---|---|---|
| `profile/facts` | Faktenblock – die einzige Wahrheitsquelle über Paula | 1 |
| `profile/style` | Stilprofil – wie sie schreibt | 1 |
| `profile/search` | Suchprofil – wonach gesucht wird | 1 |
| `profile/documents` | Verzeichnis ihrer Lebenslauf-Dateien | 1 |
| `companies/<id>` | Firmen | 100 – 5.000 |
| `jobs/<id>` | Inserate | 500 – 20.000 |
| `applications/<id>` | Bewerbungen (vorbereitet, gesendet, abgeschlossen) | 50 – 500 |
| `messages/<id>` | Bewerbungsbezogene Mails | 200 – 2.000 |
| `seen/<chunk>` | Geprüfte, aber nicht relevante Mail-IDs (gebündelt) | 10 – 100 |
| `state/<key>` | Fortschritt der Läufe | ~10 |
| `events/<id>` | Protokoll | wächst |
| `data/users/<id>/ui` | Paulas persönliche Ansichtseinstellungen | 1–2 |

## `profile/facts` – der Faktenblock

Das wichtigste Dokument des Systems. **Jede** Aussage über Paula in einem Bewerbungstext muss hier belegt sein.

```json
{
  "version": 3,
  "confirmed_by_user_at": "2026-09-20T10:12:00Z",
  "full_name": "…",
  "contact": { "email": "…", "phone": "…", "city": "…", "country": "AT" },
  "languages": [ { "language": "Deutsch", "level": "Muttersprache", "source_cv": "CV_2025-11.pdf" } ],
  "education": [ { "degree": "…", "institution": "…", "from": "2014-09", "to": "2018-06",
                   "seen_in_versions": 14, "conflicting": false } ],
  "experience": [ { "title": "…", "employer": "…", "from": "2019-03", "to": "2024-11",
                    "responsibilities": ["…"], "achievements": ["…"],
                    "seen_in_versions": 12, "conflicting": false, "notes": "…" } ],
  "skills": [ { "skill": "…", "seen_in_versions": 9 } ],
  "certifications": ["…"],
  "availability": "…",
  "salary_expectation": null,
  "preferences_note": "Von Paula selbst ergänzt: was ihr wichtig ist, was sie nicht mehr will",
  "open_questions": [ { "question": "In CV A steht 2019, in CV B 2020 – was stimmt?",
                        "status": "offen", "answer": null } ],
  "source_documents": ["CV_2025-11.pdf", "CV_2024-03.docx", "…"]
}
```

Die Felder `seen_in_versions` und `conflicting` sind der Trick aus Phase 0: Wenn eine Angabe in vierzehn von fünfzehn verschickten Lebensläufen steht, ist sie sicher. Steht sie nur einmal drin oder widersprechen sich zwei Fassungen, landet sie in `open_questions` und Paula klärt es im Dashboard. Nichts Ungeklärtes wird je in einen Bewerbungstext geschrieben.

## `profile/style` – das Stilprofil

```json
{
  "version": 2,
  "confirmed_by_user_at": "…",
  "built_from_n_letters": 17,
  "greeting_patterns": [ { "text": "Sehr geehrte Frau …", "count": 11 } ],
  "closing_patterns": [ { "text": "Mit freundlichen Grüßen", "count": 15 } ],
  "formality": "formal",
  "sentence_length": "medium",
  "typical_structure": ["Bezug auf Inserat", "Motivation", "Erfahrung", "Verfügbarkeit", "Gruß"],
  "recurring_phrases": ["…"],
  "phrases_to_avoid": ["Ausrufezeichen", "…"],
  "self_description_style": "…",
  "language_notes": "Österreichisches Deutsch: Jänner, Bewerbungsunterlagen, ß wird verwendet",
  "example_paragraphs": ["…", "…", "…"],
  "confidence_notes": "…"
}
```

## `profile/search` – das Suchprofil

Wird in Phase 1 **vorgeschlagen** (aus den Jobtiteln, auf die sie sich bisher beworben hat) und von Paula bestätigt oder korrigiert.

```json
{
  "version": 1, "confirmed_by_user_at": "…",
  "target_roles": ["…"],
  "search_terms": { "adzuna": ["…"], "note": "was an die Quellen geschickt wird" },
  "locations": { "home": "Wien", "radius_km": 30, "extra_cities": ["…"], "remote_ok": true },
  "workload": { "min_percent": 50, "max_percent": 100 },
  "employment_types": ["permanent", "temporary"],
  "languages_ok": ["de", "en"],
  "target_industries": ["…"],
  "exclude_keywords": ["…"],
  "openness_note": "Paula braucht dringend etwas und ist offen – Schwellwert bewusst niedrig"
}
```

## `profile/documents` – ihre Dateien

Die in Phase 0 gefundenen Lebenslauf- und Zeugnisdateien werden im Dateispeicher des Dashboards abgelegt (damit Paula sie herunterladen kann) und hier verzeichnet:

```json
{
  "documents": [
    { "asset_id": "…", "filename": "Lebenslauf_Paula_2025-11.pdf", "kind": "cv",
      "date_guess": "2025-11", "is_current": true, "found_in_mail": "…",
      "pages": 2, "notes": "neueste gefundene Fassung" },
    { "asset_id": "…", "filename": "Zeugnisse.pdf", "kind": "references", "is_current": true }
  ],
  "current_cv_asset_id": "…"
}
```

## `companies/<id>`

```json
{
  "id": "c_0042",
  "canonical_name": "Muster GmbH",
  "normalized_name": "muster",
  "domain": "muster.at",
  "aliases": ["Muster Ges.m.b.H.", "MUSTER"],
  "known_domains": ["muster.at", "recruiting.muster.at"],
  "city": "Wien", "state": "Wien", "country": "AT",
  "industry": "…", "size_hint": "medium",
  "website": "…", "careers_url": "…", "application_email": "…", "application_url": "…",
  "contact_person": null,
  "research": { "what_they_do": "…", "tone": "…", "hooks": ["…"],
                "accepts_spontaneous": "yes", "open_positions": ["…"],
                "sources": ["https://…"], "researched_at": "…", "confidence": 0.9 },
  "status": "researched",
  "blocked": false, "blocked_reason": null,
  "reject_count": 0,
  "last_contact_at": "2026-03-14T…",
  "priority_score": 72,
  "source": "adzuna"
}
```

`status` ∈ `discovered · prioritized · researched · no_contact · suggested · applied · blocked`

## `jobs/<id>`

```json
{
  "id": "j_1337",
  "fingerprint": "sha256:…",
  "source": "adzuna", "source_id": "…", "source_url": "https://…",
  "company_id": "c_0042", "company_name_raw": "Muster GmbH",
  "title": "…", "location": "Wien", "workload_min": 38, "workload_max": 38,
  "employment_type": "permanent",
  "salary_min": 2800, "salary_max": null, "salary_currency": "EUR",
  "description": "… (Volltext, gekürzt auf 20.000 Zeichen)",
  "description_truncated": false,
  "posted_at": "…", "fetched_at": "…",
  "prefilter": "pass",
  "score": 78,
  "score_detail": { "fit_summary": "…", "concerns": ["…"], "hard_blockers": [],
                    "matched": ["…"], "unmatched": ["…"], "hook": "…", "language": "de" },
  "status": "proposed"
}
```

`status` ∈ `new · prefiltered_out · scored · below_threshold · proposed · applied · expired`

## `applications/<id>` – das Herzstück des Dashboards

```json
{
  "id": "a_0117",
  "company_id": "c_0042", "job_id": "j_1337",
  "kind": "portal",
  "status": "ready",
  "urgency": "normal",

  "display": {
    "company_name": "Muster GmbH",
    "job_title": "…",
    "location": "Wien",
    "source_url": "https://…",
    "score": 78,
    "why": "Zwei Sätze, warum das passt – für Paula lesbar",
    "concerns": ["…"],
    "posted_at": "…"
  },

  "draft": {
    "version": 2,
    "to_email": "bewerbung@muster.at",
    "to_name": "Frau Muster",
    "subject": "…",
    "body_text": "Der vollständige Text zum Kopieren",
    "attachments": [ { "asset_id": "…", "filename": "Lebenslauf_Paula_2025-11.pdf" } ],
    "claims": ["…"],
    "factcheck": { "passed": true, "warnings": [], "checked_at": "…" },
    "generated_at": "…"
  },
  "draft_history": [ { "version": 1, "body_text": "…", "feedback": "…", "at": "…" } ],

  "sent": { "detected_at": "…", "method": "gmail_sent_folder",
            "gmail_message_id": "…", "gmail_thread_id": "…", "sent_at": "…" },

  "reply": { "kind": "rejection", "received_at": "…", "summary": "…",
             "message_id": "m_0231", "requires_action": false,
             "proposed_dates": [], "action_summary": null },

  "reply_draft": { "kind": "thank_rejection", "subject": "Re: …", "body_text": "…",
                   "to_email": "…", "generated_at": "…", "open_questions": [] },

  "outcome": "rejected",
  "created_at": "…", "updated_at": "…", "closed_at": "…"
}
```

### Status-Maschine

```
                ┌──────────┐
                │ drafting │   Claude arbeitet daran
                └────┬─────┘
          ┌──────────┼──────────┐
          ▼          ▼          ▼
     ┌────────┐ ┌─────────┐ ┌──────────────┐
     │ ready  │ │ blocked │ │ draft_failed │
     └───┬────┘ │ (Fakten │ └──────────────┘
         │      │  fehlen)│
         │      └─────────┘
         │
    ┌────┴────────────────────────┐
    │                             │
    ▼ Paula sendet                ▼ Paula verwirft
┌────────┐                   ┌──────────┐
│  sent  │                   │ discarded│
└───┬────┘                   └──────────┘
    │
    ├──▶ acknowledged      Eingangsbestätigung (bleibt im Block "unterwegs")
    ├──▶ rejected          → Block 3, Dankestext wird vorbereitet
    ├──▶ interview         → Block 0, dringend
    ├──▶ question          → Block 0, dringend
    ├──▶ offer             → Block 0, gefeiert
    └──▶ no_reply          nach 42 Tagen → Nachfass-Vorschlag
                 │
                 ▼
             ┌────────┐
             │ closed │   von Paula geschlossen oder 90 Tage inaktiv
             └────────┘
```

Alle Übergänge laufen über `db_io.py:transition()`. Die Tabelle der erlaubten Übergänge steht dort und nirgends sonst. Ein Statuswechsel schreibt immer auch ein `events`-Dokument.

### Welcher Status in welchem Dashboard-Block

| Block | Status |
|---|---|
| 0 · Dringend | `interview`, `question`, `offer` |
| 1 · Bereit zum Senden | `ready` |
| 2 · Unterwegs | `sent`, `acknowledged`, `no_reply` |
| 3 · Absage – Dankestext bereit | `rejected` mit `reply_draft`, noch nicht beantwortet |
| 4 · Erledigt | `closed`, `discarded`, `rejected` (beantwortet) |

## `messages/<id>` – bewerbungsbezogene Mails

```json
{
  "id": "m_0231",
  "gmail_message_id": "…", "gmail_thread_id": "…",
  "direction": "in",
  "from_email": "…", "from_name": "…", "to_email": "…",
  "subject": "…", "date": "…",
  "body_text": "bereinigt, ohne Zitate und Signatur, max 8000 Zeichen",
  "application_id": "a_0117", "company_id": "c_0042",
  "kind": "rejection",
  "confidence": 0.94,
  "needs_human": false,
  "attachments_meta": [ { "filename": "…", "mime": "…", "size": 123456 } ]
}
```

`kind` ∈ `application_sent · ack · rejection · interview · question · offer · followup · other`

Mails ohne Bewerbungsbezug kommen **nicht** hierher. Von ihnen bleibt nur die ID in `seen`.

## `seen/<chunk>` – was schon geprüft wurde

Damit derselbe Lauf nicht zweimal dieselbe Mail anfasst, ohne für jede irrelevante Mail ein Dokument anzulegen:

```json
{ "chunk": "0007", "ids": ["18f2a…", "18f2b…", "…"], "count": 500, "updated_at": "…" }
```

500 IDs pro Dokument. Enthält **nur** IDs, keine Betreffzeilen, keine Absender.

## `state/<key>` – Fortschritt

| Schlüssel | Inhalt |
|---|---|
| `state/gmail` | `history_id`, `initial_scan_done`, `initial_scan_cursor`, `last_run_at` |
| `state/sources` | pro Quelle: `last_run_at`, `fail_count`, `enabled` |
| `state/phase` | `current_phase` (0–3), `phase0_done_at`, `profile_confirmed_at` |
| `state/counters` | `applications_this_week`, `proposals_today`, Datum |
| `state/consent` | `confirmed_at`, `confirmed_how` – Phase 0 startet nicht ohne |

## `events/<id>` – Protokoll

`{ id, ts, kind, actor, entity, payload }`. Jeder Statuswechsel, jeder Lauf, jeder Fehler. Keine Mailtexte im Payload. Dient dem Wochenbericht und der Fehlersuche.

## Firmen-Erkennung: wann ist es dieselbe Firma?

Reihenfolge, erster Treffer gewinnt:

1. **Domain** identisch (ohne `www.`, klein geschrieben) oder in `known_domains`
2. **Normalisierter Name** identisch oder in `aliases`
3. **Ähnlichkeit ≥ 92** (`rapidfuzz.token_set_ratio`) **und** gleiche Stadt → Treffer, Alias merken
4. **Ähnlichkeit 80–91** → Claude entscheidet mit Kontext (Ort, Branche, Website). Ergebnis wird als Alias gespeichert, damit dieselbe Frage nie zweimal gestellt wird
5. sonst: neue Firma

**Normalisierung** (`scripts/dedup.py`): klein schreiben → Umlaute ersetzen (ä→ae, ö→oe, ü→ue, ß→ss) → österreichische Rechtsformen entfernen (`gmbh`, `ges.m.b.h.`, `ag`, `og`, `kg`, `e.u.`, `gesmbh`, `& co kg`, `privatstiftung`, `gen`) → Satzzeichen weg → Leerzeichen normalisieren.

## Doppelbewerbungs-Schutz

Vor jedem neuen Entwurf:

1. Firma gesperrt (`blocked`) → Stopp
2. Letzter Kontakt jünger als **180 Tage** → Stopp, Grund `cooldown`
3. Dieses Inserat (gleicher `fingerprint`) schon beworben → Stopp
4. Laufende Bewerbung bei dieser Firma (`ready`/`sent`/`acknowledged`/`interview`/`question`) → Stopp
5. Historische Bewerbung mit `confidence < 0.6` → **kein** Stopp, aber Warnhinweis auf der Karte: „Du hattest dich hier vermutlich im März 2025 beworben – bin nicht ganz sicher."

Ausnahme: Personalvermittler (Liste in `config/staffing_agencies.txt`) – bei ihnen greift nur Regel 3, weil man sich bei derselben Agentur auf verschiedene Stellen bewirbt.

## Sicherung

Die Dashboard-Datenbank liegt beim Anbieter. Zusätzlich schreibt der Wochenlauf eine vollständige Ausfuhr nach `exports/` – als JSON-Dateien, verschlüsselt, in Alexanders Ablage (**offene Frage Q12**). Personenbezogene Daten kommen dabei **nicht** ins Repo.
