export interface EditorialProfileCopy {
  description: string;
  byline: string;
  intro: string;
  perspective?: string;
  portraitAlt: string;
  portraitCaption: string;
  topicsHeading: string;
  audience: string;
  topics: readonly { title: string; preview: string; text: string }[];
  backgroundHeading: string;
  background: string;
  qualifications: readonly string[];
  quote?: string;
  requestLabel: string;
  contactHeading: string;
  contactText: string;
  externalLink: { label: string; href: string; reviewHref?: string };
}

// Editorial copy from the former fixed pages. This module grants no publication rights.
export const editorialProfileCopy = new Map<string, EditorialProfileCopy>([
  ["coaches/christian-galvano", {
    description: "Herr Christian Galvano begleitet Unternehmen als Dozent, Fachtrainer und Coach mit Schwerpunkten in Neuroleadership, Konfliktmanagement sowie Stress- und Burnoutprävention.",
    byline: "Dozent und Fachtrainer für Neurodidaktik und Neuroleadership, Personal- und Business Coach (IHK) sowie Trainer (IHK) in der Erwachsenenbildung.",
    intro: "Seine Angebote verbinden Erkenntnisse aus Neurowissenschaft und Psychologie mit konkreten Werkzeugen für Führung, Kommunikation, Veränderung und gesundes Arbeiten.",
    portraitAlt: "Porträt von Herrn Christian Galvano",
    portraitCaption: "Neurowissenschaften · Führung · Prävention",
    topicsHeading: "Führung, Zusammenarbeit und Prävention",
    audience: "Die Inhalte richten sich an Unternehmen, Führungskräfte und Teams, die Veränderung verstehen und verantwortungsvoll gestalten möchten.",
    topics: [
      { title: "Neuroleadership", preview: "Führen und motivieren in Veränderungsphasen", text: "Neurowissenschaftlich fundierte Impulse für Führung, Mitarbeitermotivation, Veränderung und mentale Stärke." },
      { title: "Konfliktmanagement", preview: "Konflikte klären und Zusammenarbeit stärken", text: "Praxisnahe Kommunikations- und Verhandlungsstrategien für konstruktive Konfliktklärung und Zusammenarbeit." },
      { title: "Stress- und Burnoutprävention", preview: "Stress verstehen und Ressourcen stärken", text: "Stressmechanismen verstehen, Ressourcen stärken und wirksame Methoden für einen gesunden Arbeitsalltag anwenden." },
    ],
    backgroundHeading: "Fachliche Grundlage",
    background: "Herr Christian Galvano arbeitet an der Schnittstelle von Neurowissenschaften, Erwachsenenbildung und beruflicher Entwicklung.",
    qualifications: [
      "Master in Neurowissenschaften (M.Sc. Tech)",
      "Studium der biologischen Psychologie",
      "Personal- und Business Coach (IHK)",
      "Trainer (IHK) in der Erwachsenenbildung",
      "Dozent und Fachtrainer für Neurodidaktik und Neuroleadership",
      "Buchautor",
    ],
    requestLabel: "Coaching per E-Mail anfragen",
    contactHeading: "Passendes Coaching-Format für Ihr Unternehmen anfragen",
    contactText: "Gemeinsam klären wir Zielgruppe, Ausgangslage und den passenden Schwerpunkt für Ihr Team.",
    externalLink: { label: "Eigene Website besuchen", href: "https://changes-galvano.de/" },
  }],
  ["coaches/manuela-rodriguez", {
    description: "Manuela Rodríguez verbindet KI-Kompetenz, Digitalstrategie, Didaktik, Psychoedukation und Coaching für eine menschenzentrierte Arbeitswelt.",
    byline: "Zertifizierte KI-Managerin mit Fokus auf Human Intelligence, Leitung Digitalstrategie, Dozentin, Moderatorin, Speakerin und Coach.",
    intro: "Manuela Rodríguez verbindet verantwortungsvolle KI-Transformation mit Lehre und persönlicher Entwicklung.",
    perspective: "Im Mittelpunkt steht eine Arbeitswelt, in der Technologie Menschen stärkt, statt sie zu ersetzen.",
    portraitAlt: "Porträt von Manuela Rodríguez",
    portraitCaption: "KI-Kompetenz · Didaktik · Transformation",
    topicsHeading: "KI, Lernen und Coaching",
    audience: "Die Angebote richten sich an Unternehmen und Menschen, die KI-Kompetenz aufbauen, Veränderung verantwortungsvoll gestalten und Wissen wirksam in die Praxis übertragen möchten.",
    topics: [
      { title: "KI-Kompetenz und Verantwortung", preview: "KI sicher und sinnvoll einsetzen", text: "KI-Literacy, ethische Standards und praktische Anwendung so vermitteln, dass Menschen Künstliche Intelligenz sicher und sinnvoll einsetzen können." },
      { title: "Didaktik und Psychoedukation", preview: "Komplexes verständlich und anwendbar machen", text: "Komplexe Inhalte verständlich strukturieren und Lernen mit einem klaren Blick auf menschliche Wahrnehmung, Entwicklung und Transfer gestalten." },
      { title: "Coaching und Kommunikation", preview: "Reflexion, Veränderung und klare Kommunikation", text: "NLP, Hypnotherapie und assoziatives Bildercoaching als methodische Zugänge für Reflexion, Veränderung und klare Kommunikation nutzen." },
    ],
    backgroundHeading: "KI-Management, Lehre und Coaching verbunden",
    background: "Ihr Profil verbindet geisteswissenschaftliche Perspektiven, Erwachsenenbildung, Digitalstrategie und methodische Coachingansätze.",
    qualifications: [
      "Studium der Psychoanalyse und Mediävistik an der Goethe-Universität Frankfurt",
      "Zertifizierte KI-Managerin mit Fokus auf Human Intelligence",
      "Leitung Digitalstrategie",
      "Dozentin für Psychoedukation, Didaktik und Spanisch",
      "Lehraufträge an der Friedrich-Alexander-Universität Erlangen-Nürnberg und am KIT",
      "Zertifizierte Gutachterin für Erwachsenenbildung (GRETA)",
      "Coach für NLP, Hypnotherapie und assoziatives Bildercoaching",
      "Moderatorin und Speakerin",
    ],
    quote: "Mein Ziel: Eine Arbeitswelt, die menschlich bleibt und zugleich zukunftsfähig ist. KI ist nicht dein Feind, auch nicht dein Freund – aber KI kann dein Verbündeter sein!",
    requestLabel: "Anfrage per E-Mail",
    contactHeading: "Passt die Expertise zu Ihrem Vorhaben?",
    contactText: "Frau Rappelt unterstützt bei der Einordnung und stellt den Kontakt zwischen Unternehmen und Coach her.",
    externalLink: {
      label: "D+P AI Advisory ansehen",
      href: "https://donner-partner.de/dp/fuer-unternehmen/firmenseminare/",
      reviewHref: "https://advisory.donner-partner.de/",
    },
  }],
]);
