# FIN-01 Rechnungsmanagement

Stand: 24.09.2026

Status: Produkt-Backlog; fachliche Abstimmung mit der Buchhaltung offen; keine
Implementierung freigegeben.

## Ziel

Ein späteres, eigenständiges Modul soll die nachvollziehbare Bearbeitung von
Ausgangsrechnungen an Unternehmen und Eingangsrechnungen von Coaches
unterstützen. Es ist kein Teil des aktuellen Website-, Messe- oder CAL-1-Scope.

## Vorläufiger Umfang

- Ausgangsrechnungen zu bestätigten Leistungen oder Aufträgen vorbereiten,
  prüfen, im Vier-Augen-Prinzip freigeben, versenden und ihren Fälligkeits-
  sowie Zahlungsstatus nachvollziehen.
- Eingangsrechnungen von Coaches erfassen, einem Auftrag zuordnen, sachlich
  prüfen, freigeben und an die Buchhaltung übergeben.
- Belege, Korrekturen und Statusänderungen revisionsnah dokumentieren.
- Korrekturen, Gutschriften und Stornierungen nachvollziehbar behandeln.
- Ablage und Aufbewahrung sowie später gegebenenfalls E-Rechnungsformate wie
  XRechnung oder ZUGFeRD berücksichtigen.
- Rollen und Sichtbarkeit für Vertrieb, Administration, fachliche Prüfung und
  Buchhaltung trennen.
- Exporte oder Integrationen erst nach Auswahl des führenden
  Buchhaltungssystems festlegen; DATEV ist lediglich eine mögliche Option.

## Nicht enthalten

- Keine Rechnungsdatenbank, Nummernlogik oder Zahlungsfunktion im aktuellen
  Projektinkrement.
- Kein automatischer E-Mail-Versand, Mahnlauf oder Bankabgleich.
- Keine erfundenen Steuer-, Aufbewahrungs- oder Freigaberegeln.
- Keine produktiven Rechnungs- oder Zahlungsdaten vor Datenschutz-,
  Sicherheits- und Betriebsfreigabe.

## Offene Fachfragen

1. Welche Gesellschaft ist tatsächlich Rechnungsstellerin?
2. Welches Buchhaltungs- oder ERP-System ist führend und welche Schnittstellen
   stehen zur Verfügung?
3. Liegt die führende Rechnungsnummern- und Belegverwaltung im Hub oder im
   Buchhaltungssystem?
4. Wer erstellt, prüft, korrigiert, storniert und gibt Ausgangsrechnungen frei?
5. Wie werden Ausgangsrechnungen versendet und Coach-Rechnungen empfangen?
6. Wer prüft Coach-Rechnungen sachlich und wer gibt sie kaufmännisch frei?
7. Welche Nummernkreise, Steuersachverhalte, Pflichtangaben und Währungen sind
   tatsächlich relevant?
8. Welche Belegformate, XRechnung-/ZUGFeRD-Anforderungen,
   Aufbewahrungsfristen und GoBD-Anforderungen bestätigt
   die Buchhaltung beziehungsweise Steuerberatung?
9. Welche Auftrags-, Firmen-, Coach- und Leistungsdaten dürfen übernommen
   werden und welches System besitzt jeweils die Datenhoheit?
10. Werden Zahlungsstatus, Teilzahlungen, Gutschriften, Storno und Mahnwesen im
   Hub oder ausschließlich im Buchhaltungssystem geführt?
11. Wer dokumentiert und bestätigt Zahlungen?
12. Welche Rollen dürfen Belege, Bankdaten, Honorare und interne Prüfhinweise
   sehen oder exportieren?
13. Welche Audit-, Backup-, Lösch-, Export- und Incident-Regeln gelten?
14. Welche Benachrichtigungen und späteren Automatisierungen sind fachlich
    erwünscht und rechtlich zulässig?

## Discovery-Gate

FIN-01 darf erst in Anforderungen und Architektur übergehen, wenn Buchhaltung,
Product Owner, Datenschutz und technischer Betrieb die offenen Fragen
gemeinsam beantwortet haben. Ein späterer MVP benötigt mindestens Rollen- und
Rechtematrix, Datenfluss, Integrationsentscheidung, Aufbewahrungskonzept,
Auditregeln und testbare Abnahmekriterien.
