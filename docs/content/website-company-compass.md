# Unternehmens-Kompass

Der Einstieg unter [Für Unternehmen](https://dp-manuel.github.io/CompetenceHub/unternehmen/) ist nach sechs Anliegen geordnet. Jedes Anliegen führt ausschließlich in bestehende Leistungsbereiche oder zu einem passenden Abschnitt auf derselben Seite. Die Themenwahl lädt keine Daten nach: Mit JavaScript sind es Tabs, ohne JavaScript Sprunglinks zu sechs lesbaren Abschnitten. Die Inhalte teilen sich bei aktiven Tabs denselben Platz, damit der nachfolgende Abschnitt beim Wechsel nicht springt.

Darunter stehen die drei Leistungswelten, der Ablauf und der Kontakt zu Frau Rappelt. Das Assessment Center behält unter `#assessment-center` seine beiden Leistungsstufen und die freigegebenen Preise. Concept Clean bleibt die einzige Kundenstimme. Der zweite Praxisweg bleibt ausdrücklich als illustratives Beispiel gekennzeichnet. Beide Fallbeispiele und alle FAQ-Antworten sind weiterhin verfügbar.

## Prüfung Und Veröffentlichung

- Gezielter Browsertest: [run-company-compass-browser.py](../../apps/website/scripts/run-company-compass-browser.py), mit `--base`, `--screenshots` und `--browser firefox|edge`. Prüft alle sechs Themen, Texte und Links, mobile Bedienung, Tastatur und Fokus, Reduced Motion, JavaScript-freien Zugang sowie nativen Firefox-Zoom.
- Separat: Preview-Verträge, Astro und Dist-Linkprüfung für Preview und Production; bestehender Browsercheck für Homepage-Hub, Angebotsfinder und Profilfreigaben.
- Ausschließlich der bestehende manuelle Pages-Workflow veröffentlicht die Vorschau. Dort bleiben Christian Galvano und Manuela Rodríguez, M.A., sichtbar. Keine weiteren Coachprofile oder Demoprofile, keine Portal-Anbindung und kein IONOS-Release. Der Production-Build dient lediglich der lokalen und CI-Verifikation.
- Aus den Browserprüfungen übernommen: Bei geringer Viewporthöhe darf der Header auf dieser Seite mitscrollen; die Prüfung auf Textüberlauf misst gerenderte Textfragmente, nicht nur die Breite der Seite.
- Kontrastregression: Die Farbfläche des alten Fallbeispiels darf nicht auf das neue `details` übergehen. Der Concept-Clean-Titel verwendet gekoppelte Vorder- und Hintergrundfarben; der aufgeklappte Inhalt hat einen eigenen hellen Hintergrund. Der [visuelle Regressionstest](../../apps/website/scripts/run-visual-recovery-browser.py) misst gerenderte Farbpaare in Normal-, Hover-, Fokus- und Offen-Zustand.
