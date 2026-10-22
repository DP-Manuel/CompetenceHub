# PRIV-ANALYTICS-01: Cookie / Tracking / Consent Decision

Stand: 21.10.2026. Status: ENTWURF / OFFEN.
Entscheidungstraeger: Manuel fuer Produkt und Betrieb, zustaendige Datenschutz-/Rechtsstelle fuer rechtliche Bewertung.
Technischer Entwurf: [ANALYTICS-01](../requirements/analytics-01-discovery-2026-10-21.md).
Dies ist keine abschliessende Rechtsentscheidung und keine Aktivierungsfreigabe.

## Zweck Und Vorgesehene Loesung

Statistisch verstehen, welche oeffentlichen Seiten, Themen, Coachprofile und Kontaktwege genutzt werden.
Bevorzugter Vorschlag: eigene first-party Aggregation im vorhandenen Serverstack, keine Personenueberwachung.
Matomo/Plausible wurden verglichen; cookieloser Betrieb allein belegt nicht das strengere Ziel ohne Besucherkennungen.
Toolauswahl und Retention sind noch nicht akzeptiert. Aktuell ist weder in Produktion noch in Preview Analytics aktiv.

## Technische Entscheidungsmatrix Fuer Den Vorschlag

| Frage | Vorgeschlagenes Level 1 | Offener Pruefpunkt |
| --- | --- | --- |
| Analytics-Cookies | NEIN | Browser-/Netzwerk-/Proxy-Test vor Aktivierung |
| LocalStorage | NEIN | Collector und Abhaengigkeiten pruefen |
| SessionStorage / IndexedDB / persistente Cache-IDs | NEIN | Kein Ersatz-Identifier ueber andere Speicher |
| Besucher-/Session-/Event-Identifier | NEIN | Keine taeglichen IP-/UA-Hashes und keine versteckten Korrelationen |
| Fingerprinting / Werbeprofile / Cross-Site | NEIN | Kein Browsermerkmal-Buendel, keine Drittanbietertracker |
| Endgeraete lesen | DOM-Ereignis und erlaubte Route/Target-ID | Auch cookieloser Endgeraetezugriff ist fachlich/rechtlich zu bewerten |
| Optionale Endgeraetedaten | Grobe Viewport-/Referrergruppe vorerst AUS | Erst nach expliziter Minimierungs-/Privacy-Freigabe |
| Im Browser speichern | Nur kurzlebiger Zustand im Dokument-Arbeitsspeicher, keine dauerhafte Mess-ID | Definition beim POC nachweisen |
| Drittanbieter / Daten verlassen Infrastruktur | Kein Analytics-SaaS, keine fremden Tracker; kontrollierter VPS als Ziel | Hosting-/Zugriffs-/Auftragsverarbeitungsverhaeltnisse bestaetigen |
| IP-Verarbeitung | Netzwerk/Ingress technisch transient; keine IP in Analytics-DB | Proxy-/Hosterlogs, Security-Limits, Zugriff und Retention separat pruefen |
| Roh-Events | Keine dauerhafte Speicherung | Request-/Fehlerlogs und Debugpfade ausschliessen |
| Aggregate | Eventzaehler mit festen Dimensionen, vorgeschlagen 90 Tage | Frist, Mindestmengen, Loeschung und Backups freigeben |
| Authentifizierung Admin | Bestehende Portal-Session getrennt von Besuchermessung | Admin-Cookies nicht fuer oeffentliche Analytics verwenden |
| Datenschutzhinweis | Muss vor neuem Erhebungszweck geprueft/gegebenenfalls aktualisiert werden | Zentraler D+P-Verweis ist keine pauschale Abdeckung neuer Verarbeitung |
| Consent erforderlich | OFFEN | Zustaendige Datenschutz-/Rechtspruefung ausstehend |

Das technische Ziel ohne Cookies/Storage ist kein Nachweis einer Einwilligungsfreiheit.
Rechtsgrundlage, Informationspflichten, Endgeraetezugriff, Verantwortlichkeiten und Auftragsverarbeitung sind vor Aktivierung zu pruefen.
Die Vendor-Aussage, ein Produkt brauche keinen Banner, ersetzt diese Projektpruefung nicht.

## Ausgeschlossen

Klarnamen unbekannter Besucher, Roh-IP-Dashboard, dauerhafte Geraeteprofile, individuelle Besucherlisten, Formulardaten, Maus-/Tastatur-/Bildschirmaufzeichnung und Session Replay.
Kein Versand von Portal-IDs, Auth-Tokens, privaten URL-Parametern, Freitext oder Gesundheits-/Anfrageinhalten.
Preview-Traffic wird nicht mit Produktion vermischt; bevorzugt kein Collector in Preview und serverseitige Ablehnung dieser Origin.
Heatmaps, Sessions, wiederkehrende Besucher, Funnels und Replay sind Level 2 mit neuem Privacy-/Consent-Gate.

## Gate Vor Aktivierung

Product Owner akzeptiert Umfang/Messgrenzen; Datenschutz/Legal dokumentiert Consent JA/NEIN mit Begruendung und freigegebenem Hinweis.
Betrieb bestaetigt IP-/Logpfade, Speicherfristen, Loeschung, Backup/Restore, Ressourcen, Zugriff und Incidentverfahren.
Security prueft Ingestion/Manipulation/Abuse und serverseitiges Admin-RBAC.
Der synthetische technische Nachweis muss Cookies/Storage/Identifier und Datenlecks ueber Request, Fehlerlog und Export ausschliessen.

Wenn Consent JA: Collector bis zur Einwilligung technisch blockiert, gleichwertiger Widerruf und Nachweis-/Konfigurationsstrategie; CMP als eigener freizugebender Block.
Wenn Consent NEIN: dokumentierte fachlich/rechtliche Begruendung plus technische Konfiguration und Notice bleiben erforderlich.
Solange OFFEN: keine produktive Messung. Es wurde kein Cookiebanner eingebaut.

## Nachweisstand

Am 21.10.2026: Vergleich und Architekturentwurf vorhanden; keine Analyticsinstallation, Migration, API, Messereignisse, Auth-Erweiterung oder Datenverarbeitung freigegeben/ausgefuehrt.
Primaerquellen fuer Tool-Eigenschaften stehen im verlinkten Discovery-Dokument; keine Rechtsfreigabe wird aus Anbieterwerbung abgeleitet.
