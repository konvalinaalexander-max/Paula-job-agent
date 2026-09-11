# 00 – Vision, Ziele, Prinzipien

## Das Ziel in einem Satz

Paula soll mit minimalem eigenem Aufwand **gute, persönliche, faktenwahre Bewerbungen** an **passende** Arbeitgeber schicken, **nie doppelt**, und den Überblick über den gesamten Prozess behalten – ohne je eine Konsole, ein Repo oder eine KI-Oberfläche zu sehen.

## Was das System ist

Eine **Pipeline mit Freigabe-Schleife**. Software sammelt, filtert, entwirft und protokolliert; ein Mensch (Paula) entscheidet über jeden Versand mit einem Klick in Telegram. KI wird an genau den Stellen eingesetzt, wo Sprache verstanden oder erzeugt werden muss – nirgends sonst.

## Was das System **nicht** ist (Nicht-Ziele)

| Nicht-Ziel | Warum |
|---|---|
| Vollautomatischer Versand ohne Freigabe | Rechtlich/ethisch heikel, ruiniert Mail-Reputation, produziert Serienbriefe |
| Auto-Apply über Web-Formulare (LinkedIn Easy Apply, Workday, Bewerberportale) | Fragil (Formulare ändern sich ständig), AGB-Verstoß bei den meisten Portalen, kein Freigabe-Schritt möglich. Stattdessen: das System liefert Paula einen fertigen Text + Link, sie füllt das Formular selbst |
| "Das ganze Land anschreiben" | Masse ohne Qualität. Das System **scannt** breit, **bewirbt** sich aber gezielt (max. `limits.applications_per_week`) |
| Ein Chat-Assistent, mit dem Paula über alles reden kann | Der Telegram-Bot hat definierte Befehle und Flows (`docs/10-telegram-flows.md`). Kein Freitext-Chatbot |
| Multi-User / SaaS | Genau eine Nutzerin. Keine Mandantenfähigkeit, keine Web-UI |
| Lebenslauf-Umschreiben pro Stelle | Der CV bleibt ein von Paula gepflegtes PDF. Das System schreibt Anschreiben/Mails, nicht den CV |

## Prinzipien (in dieser Reihenfolge, bei Konflikt gewinnt das obere)

1. **Sicherheit vor Automatisierung.** Im Zweifel nicht senden, sondern fragen.
2. **Wahrheit vor Überzeugungskraft.** Kein Satz über Paula, der nicht belegt ist.
3. **Qualität vor Menge.** Zehn recherchierte Bewerbungen pro Woche schlagen hundert generische.
4. **Nachvollziehbarkeit.** Jede Aktion des Systems ist in `events` protokolliert und Paula über `/status` erklärbar.
5. **Einfachheit.** Die einfachste Lösung, die die Anforderung erfüllt. Kein Framework, wenn 30 Zeilen reichen.
6. **Austauschbarkeit der Quellen.** Jobportale kommen und gehen. Jede Quelle ist ein Adapter hinter einem Interface.

## Rollen

| Rolle | Person | Zugang |
|---|---|---|
| Betreiber / Admin | Alexander | Server, Repo, `.env`, Telegram-Admin-Chat, alle Daten |
| Nutzerin | Paula | Nur Telegram. Sieht ihre Entwürfe, Status, Antworten. Kann pausieren, Firmen sperren, Stellen einreichen |
| Ausführende KI | Claude Code o. ä. | Repo; schreibt Code; hat nie Zugriff auf Paulas Live-Daten, außer der Betreiber gibt sie für Tests explizit frei |

## Erfolgskriterien

Das Projekt ist erfolgreich, wenn nach 8 Wochen Betrieb:

- **0** Doppelbewerbungen (gleiche Firma innerhalb der Sperrfrist) versendet wurden
- **0** Mails ohne Freigabe verschickt wurden
- **0** Beanstandungen von Paula wegen erfundener Fakten
- Paula pro Freigabe im Schnitt **< 3 Minuten** braucht (Entwurf lesen, ggf. eine Korrektur, klicken)
- Paula das System **nicht abgeschaltet** hat, weil es nervt (Nachrichtenfrequenz, Qualität)
- der Betreiber **keinen manuellen Eingriff pro Woche** braucht (keine abgestürzten Prozesse, keine Token-Abläufe)
- die Antwortquote (Einladung / Rückfrage pro gesendeter Bewerbung) messbar im `/report` steht

## Die Nutzerin im Blick behalten

Paula ist nicht technisch, sieht nur Telegram-Nachrichten und hat wahrscheinlich gemischte Gefühle dabei, dass "eine KI" in ihrem Namen schreibt. Deshalb:

- Jede Nachricht an sie ist kurz, freundlich, ohne Technik-Vokabular.
- Sie kann jederzeit mit `/pause` alles anhalten und mit `/stop` alles beenden (das System verschickt dann nichts mehr, bis der Betreiber es reaktiviert).
- Sie sieht **immer** den vollständigen Text, der rausgeht – keine Zusammenfassung, kein "Entwurf ok?".
- Das System erklärt in zwei Sätzen, **warum** es eine Stelle vorschlägt.
- Zu viele Vorschläge sind schlimmer als zu wenige. Startwert: max. 3 Vorschläge pro Tag, konfigurierbar.
