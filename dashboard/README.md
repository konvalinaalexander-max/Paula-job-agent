# Dashboard

Eine einzelne Seite (`index.html`), veröffentlicht als Artifact, mit dauerhafter
Datenbank, Dateiablage und Download-Funktion.

**Gestaltung und Inhalt:** `docs/10-dashboard.md` – dort steht jeder Block, jede
Karte und jeder Knopf.

**Veröffentlichen / Aktualisieren:** aus der Claude-Session heraus, immer auf
dieselbe Adresse. Ein erneutes Veröffentlichen ersetzt die Seite; die Daten in der
Datenbank bleiben unberührt.

**Fähigkeiten, die die Seite braucht:**

| Fähigkeit | Wofür |
|---|---|
| `db` | Bewerbungen, Firmen, Profil lesen; Paulas Aktionen zurückschreiben |
| `assets` | Paulas Lebenslauf-Dateien, in Phase 0 aus den Mail-Anhängen übernommen |
| `downloads` | „Lebenslauf herunterladen" |

**Zugriffsrechte:** Paula liest alles und schreibt nur Status-Felder (abgehakt,
verworfen, Firma sperren, Änderungswunsch, eingereichter Link). Bewerbungen und
Fakten schreibt ausschließlich die Session.

**Wichtig:** Die Seite enthält **keine** fest eingebauten Daten. Alles kommt aus
der Datenbank. Ein Entwurf mit Beispieldaten dient nur der Gestaltung und wird vor
dem echten Einsatz entfernt.
