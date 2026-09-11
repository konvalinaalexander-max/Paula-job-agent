# Tests

Siehe `docs/11-testing.md`. Struktur, die die ausführende KI anlegt:

```
tests/
├── conftest.py              In-Memory-DB, Settings-Fixture, Fake-Mailclient, Fake-Telegram
├── fixtures/
│   ├── mails/               *.eml + expected.yaml (synthetisch!)
│   ├── jobs/                *.json (RawJob) + expected.yaml
│   ├── companies/           CompanyResearch-JSONs
│   ├── profile/             facts.test.md, style_profile.test.md, profile.test.yaml
│   ├── adzuna/              aufgezeichnete API-Antworten
│   └── telegram/            Update-JSONs
├── tools/seed_mailbox.py    Fixture-Mails in Sandbox-Konto senden
├── llm_results/             Ergebnisse der Golden-Tests (in Git)
├── test_config.py test_db.py test_state.py test_dedup.py test_parse.py
├── test_send_guard.py       Pflicht vor M5
├── test_injection.py        -m llm
├── test_factcheck.py
├── test_llm_golden.py       -m llm
└── test_telegram_handlers.py test_render.py test_sources_adzuna.py ...
```

Alle Fixtures sind erfunden. Keine echten Namen, Adressen oder Mails.
