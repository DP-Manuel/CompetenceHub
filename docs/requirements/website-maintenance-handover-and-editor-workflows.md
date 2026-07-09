# Website-Wartung, Uebergabe und Redaktionsworkflows

Stand: 2026-06-17

## Ziel

Diese Datei haelt Anforderungen fest, damit die Website spaeter nicht nur technisch funktioniert, sondern auch uebergeben, dokumentiert und von anderen Personen weiterbetrieben werden kann.

Aktuelle Annahme: Manuel betreut die Website zunaechst technisch. Spaeter kann sich das aendern, wenn Manuel andere Projekte uebernimmt oder nicht mehr in der Firma ist. Die technische Basis muss deshalb so dokumentiert und strukturiert sein, dass ein anderer Informatiker sie nachvollziehen und mit allen noetigen Zugriffen weiterbetreiben kann.

## Nutzer und Rollen

### Technischer Betreuer

Aktuell: Manuel.

Aufgaben:

- Quellcode verwalten.
- Builds und Deployments ausfuehren.
- technische Fehler beheben.
- Dokumentation aktuell halten.
- Zugriff auf Hosting, Domain/Subdomain, GitHub, Build-/Deployment-Prozesse und spaetere Datenquellen sicherstellen.

### Kuenftiger technischer Nachfolger

Moeglich: interner Informatiker, EDV, externer Dienstleister oder andere technisch verantwortliche Person.

Bedarf:

- Vollstaendige Entwicklerdokumentation.
- Ueberblick ueber Architektur, Build, Deployment, Hosting, Domains/Subdomains und Abhaengigkeiten.
- klare Liste benoetigter Accounts und Berechtigungen.
- klare Anleitung fuer Updates, Rollback, lokale Entwicklung und produktive Veroeffentlichung.

### Fachliche Redakteurin

Aktuell geplant: Kollegin fuer Firmen, Coaches und Stellen.

Kenntnisstand:

- Wenig bis keine Erfahrung mit Entwicklung, GitHub oder Build-Prozessen.

Aufgaben im Live-Betrieb:

- Firmen anlegen und pflegen.
- Coaches anlegen und pflegen.
- Stellen einpflegen.
- spaeter ggf. Seminar- und Feedbackinformationen pflegen.

Konsequenz: Die Kollegin sollte langfristig nicht direkt in GitHub, Code oder Build-Prozesse arbeiten muessen.

## Redaktionsmodell

### Kurzfristig fuer Prototyp und fruehen Betrieb

- Inhalte koennen zunaechst technisch durch Manuel in Astro gepflegt werden.
- Aenderungen bleiben versioniert und kontrolliert.
- Fachliche Inhalte werden durch die Kollegin geliefert, aber technisch von Manuel eingepflegt.

### Mittelfristig fuer Live-Betrieb

Es braucht eine Entscheidung, wie nicht-technische Pflege erfolgen soll:

1. Astro bleibt statisch, Manuel bzw. technischer Betreuer pflegt Inhalte.
2. Astro wird mit einem einfachen CMS oder strukturierten Datenquellen kombiniert.
3. Die Website wird ganz oder teilweise auf ein klassisches CMS wie WordPress umgestellt.
4. Redaktionsdaten werden aus der spaeteren Webapp/API gespeist, waehrend die Website selbst statisch oder hybrid bleibt.

Die Entscheidung ist noch offen und soll vor produktiver Uebergabe getroffen werden.

## Technische Auswirkungen

Ja, die geplante Pflege durch eine nicht-technische Kollegin veraendert die technischen Anforderungen an die Live-Website. Fuer den 01.07.-Prototyp kann Astro weiterhin statisch bleiben. Fuer den produktiven Betrieb braucht die Website oder das spaetere System aber einen Redaktionsweg, der Firmen, Coaches und Stellen ohne Code- und GitHub-Kenntnisse pflegbar macht.

### Konsequenzen fuer die Architektur

- Die Website darf nicht dauerhaft nur von lokalem Rechnerwissen, Manuels Firmen-GitHub oder manuellen Einzelablaeufen abhaengen.
- Die oeffentliche Website braucht eine dokumentierte Build- und Deployment-Kette, die ein anderer Informatiker uebernehmen kann.
- Redaktionelle Inhalte wie Firmen, Coaches und Stellen sollten mittelfristig in strukturierter Form gepflegt werden, z.B. CMS, Datenbank/API der spaeteren Webapp oder ein anderes formularbasiertes Backend.
- Wenn Astro bleibt, sollte es entweder klar developer-maintained bleiben oder an ein CMS/API angebunden werden.
- Wenn WordPress oder ein anderes CMS gewaehlt wird, muessen Betrieb, Updates, Rollen, Datenschutz und Plugin-/Theme-Wartung als eigene Anforderungen behandelt werden.
- Die Coach-Unterseite sollte technisch so vorbereitet werden, dass sie spaeter nicht nur harte HTML-Karten enthaelt, sondern aus strukturierten Coach-Daten gespeist werden kann.

### Konsequenzen fuer Dokumentation und Zugriff

- Es braucht eine technische Betriebsdokumentation fuer lokale Entwicklung, Build, Deployment, Hosting, Subdomain, Abhaengigkeiten, Updates und Rollback.
- Es braucht eine Zugriffsliste mit Systemen und Rollen, aber ohne Passwoerter oder geheime Zugangsdaten im Repository.
- Es braucht einen Redaktionsleitfaden fuer die Kollegin, sobald sie Firmen, Coaches und Stellen selbst pflegt.
- GitHub, Hosting und Deployment duerfen nicht dauerhaft nur an Manuels persoenlichen Arbeitskontext gebunden bleiben; vor Live-Betrieb braucht es eine Eigentums- und Zugriffsentscheidung.

### Entscheidungspunkt

Vor dem Live-Betrieb muss eine Technologieentscheidung dokumentiert werden:

1. Astro bleibt statisch und wird durch einen technischen Betreuer gepflegt.
2. Astro bleibt Frontend und bekommt CMS-/API-gestuetzte Inhalte.
3. WordPress oder ein anderes klassisches CMS uebernimmt die Website.
4. Die spaetere Webapp wird fuehrendes System fuer Firmen, Coaches und Stellen und spielt Inhalte an die Website aus.

## Neue Inhaltsanforderung: Coach-Unterseite

Es soll eine kleine Subpage entstehen, auf der sich Coaches vorstellen koennen.

### Zweck

- Unternehmen und interne Stakeholder sehen, welche fachlichen Personen hinter Schulungen stehen koennen.
- Coaches erhalten eine professionelle Praesenz im Kontext des Angebots.
- Die Seite kann spaeter mit Coach-Profilen aus einem CMS oder der Webapp verbunden werden.

### Erste Inhalte je Coach

- Name
- Foto oder Platzhalterbild
- Rolle, z.B. Coach, Dozent, Trainer
- Themenschwerpunkte
- Kurzprofil
- Qualifikationen oder Erfahrung
- Einsatzregion oder Format, z.B. Raum Wuerzburg, Inhouse, online
- Kontakt- oder Anfragebezug, ohne private Kontaktdaten oeffentlich zu machen, solange das nicht freigegeben ist

### Offene Fragen

- Duerfen echte Coach-Namen und Fotos im Prototyp verwendet werden?
- Braucht jedes Profil eine interne Freigabe?
- Werden Coaches redaktionell von der Kollegin gepflegt oder spaeter aus dem System ausgespielt?
- Soll die Seite bereits zur 01.07.-Praesentation sichtbar sein oder erst danach?

## Datenobjekte fuer spaetere Pflege

### Firma

Mindestfelder spaeter zu klaeren:

- Firmenname
- Branche
- Ort/Region
- Ansprechpartner
- Kontaktinformationen
- offene Bedarfe
- Seminarinteresse
- Stellenanzeigen
- Feedbackhistorie

### Coach

Mindestfelder spaeter zu klaeren:

- Name
- Rolle
- Themenschwerpunkte
- Qualifikationen
- Verfuegbarkeit
- Einsatzregion
- Kurzprofil
- Profilbild
- Freigabestatus fuer oeffentliche Darstellung

### Stelle

Mindestfelder aus bisherigem Briefing:

- Firma
- Ort
- Arbeitszeit
- Qualifikation
- Hard Skills
- Soft Skills
- Beginn

## Funktionale Anforderungen

- FR-WH-001: Die Website soll so dokumentiert werden, dass ein anderer Informatiker sie lokal starten, bauen, pruefen und deployen kann.
- FR-WH-002: Die Projektdokumentation soll alle benoetigten technischen Zugriffe benennen, ohne Zugangsdaten selbst in das Repository zu schreiben.
- FR-WH-003: Die Dokumentation soll den Unterschied zwischen Prototyp, Live-Website und spaeterer Webapp klar erklaeren.
- FR-WH-004: Die Pflege von Firmen, Coaches und Stellen soll langfristig ohne GitHub- oder Code-Kenntnisse moeglich sein.
- FR-WH-005: Bis ein Redaktionssystem existiert, soll klar dokumentiert sein, dass fachliche Inhalte von der Kollegin geliefert und technisch durch Manuel bzw. den technischen Betreuer eingepflegt werden.
- FR-WH-006: Die Website soll eine Coach-Unterseite vorsehen, auf der Coaches professionell vorgestellt werden koennen.
- FR-WH-007: Oeffentliche Coach-Profile sollen erst mit Freigabe von Name, Bild, Text und Rolle veroeffentlicht werden.
- FR-WH-008: Vor dem Live-Betrieb soll entschieden werden, ob Astro statisch bleibt, mit einem CMS ergaenzt wird, auf WordPress umgestellt wird oder Inhalte aus der spaeteren Webapp/API bezieht.

## Nichtfunktionale Anforderungen

- NFR-WH-001: Die technische Dokumentation soll fuer einen allgemeinen Informatiker verstaendlich sein, der das Projekt nicht aus der Entstehung kennt.
- NFR-WH-002: Build- und Deployment-Schritte sollen reproduzierbar und nicht nur an Manuels Rechnerwissen gebunden sein.
- NFR-WH-003: Abhaengigkeiten, Node-Version, Astro-Version und Update-Risiken sollen dokumentiert werden.
- NFR-WH-004: Es soll eine Uebergabeliste fuer GitHub, Hosting, Domain/Subdomain, Deployment, rechtliche Seiten und spaetere Datenquellen geben.
- NFR-WH-005: Redaktionsworkflows fuer nicht-technische Kolleginnen sollen moeglichst fehlerarm, formularbasiert und ohne direkten Codekontakt gestaltet werden.
- NFR-WH-006: Personenbezogene oder profilbezogene Daten duerfen erst nach Freigabe, Datenschutzklaerung und klarer Zustandsverantwortung produktiv verarbeitet werden.

## Akzeptanzkriterien

- AC-WH-001 deckt FR-WH-001 und NFR-WH-001 ab: Ein fachfremder Informatiker kann anhand der Dokumentation Repository, Struktur, lokale Entwicklung, Build und Deployment nachvollziehen.
- AC-WH-002 deckt FR-WH-002 und NFR-WH-004 ab: Es gibt eine Zugriffsliste, die Systeme und Rollen nennt, aber keine Passwoerter oder geheimen Zugangsdaten enthaelt.
- AC-WH-003 deckt FR-WH-004 und NFR-WH-005 ab: Fuer die Kollegin existiert vor Live-Betrieb ein Workflow, mit dem Firmen, Coaches und Stellen ohne Code- oder GitHub-Arbeit gepflegt werden koennen.
- AC-WH-004 deckt FR-WH-006 und FR-WH-007 ab: Eine Coach-Unterseite existiert oder ist als geplanter Inhaltsschnitt dokumentiert; echte Profile werden nur mit Freigabestatus veroeffentlicht.
- AC-WH-005 deckt FR-WH-008 ab: Vor produktiver Uebergabe liegt eine dokumentierte Entscheidung zu Astro statisch, Astro plus CMS/API, WordPress oder anderer CMS-Loesung vor.

## Risiken

- Wenn alle Inhalte dauerhaft ueber Manuel laufen, entsteht ein Bus-Factor-Risiko.
- Wenn die Kollegin ohne Redaktionssystem Inhalte pflegen soll, entstehen Fehler- und Abhaengigkeitsrisiken.
- Wenn zu frueh echte Personenprofile, Firmen oder Stellen produktiv verarbeitet werden, entstehen Datenschutz- und Freigaberisiken.
- Wenn die Technologieentscheidung nicht dokumentiert wird, kann Astro spaeter als Spezialloesung wirken, obwohl die Architektur bewusst gewaehlt wurde.

## Naechste Entscheidungen

- Soll die Coach-Unterseite schon in den 01.07.-Prototyp aufgenommen werden?
- Welche Informationen duerfen bei Coaches oeffentlich gezeigt werden?
- Soll die spaetere Redaktion ueber ein CMS, ueber die Webapp oder weiter ueber technische Pflege laufen?
- Wer soll langfristig technischer Owner von GitHub, Hosting und Deployment sein?
- Welche Dokumentation braucht die EDV oder ein externer Dienstleister fuer die Uebergabe?
