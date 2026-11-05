// Approved short scope, 29.10 review closure. No protected workshop detail or prices.
export const guelcanOfferFamilies = [
  {
    key: "family/business-balance",
    title: "Business & Balance",
    audience: "Für Unternehmerinnen, die Struktur, Klarheit und Energie im beruflichen Alltag verbinden möchten.",
    formats: [
      { key: "business-balance/day", title: "Tagesworkshop", detail: "Rahmen und Durchführung nach Abstimmung." },
      { key: "business-balance/six-weeks", title: "6-Wochen-Vertiefungsprogramm", detail: "Eine Einheit pro Woche, jeweils 60 Minuten." },
    ],
    options: ["Optionale Community zwischen den Einheiten"],
    boundary: "Coaching und Training, keine Therapie, ärztliche oder psychotherapeutische Behandlung, Rechts- oder Steuerberatung.",
  },
  {
    key: "family/gesundheit-im-unternehmensalltag",
    title: "Gesundheit im Unternehmensalltag",
    audience: "Für Teams: Bewegung, Ernährung, Stressregulation und mentale Gesundheit im Arbeitsalltag einordnen.",
    formats: [
      { key: "gesundheit/half-day", title: "Halbtagsworkshop", detail: "Vier Stunden, im Unternehmen oder an einem externen Veranstaltungsort." },
    ],
    options: ["Ganztagsvariante", "Vertiefende Übungen", "Follow-up", "Ergonomie-Begehung"],
    boundary: "Gesundheitsförderung und Training, keine ärztliche Behandlung, Psychotherapie, Heilbehandlung, Diagnostik oder individuelle Ernährungstherapie.",
  },
  {
    key: "family/konfliktklaerung-teamreflexion",
    title: "Konfliktklärung & Teamreflexion",
    audience: "Für Teams, die ein Konfliktthema klären oder ihre Zusammenarbeit gemeinsam reflektieren möchten.",
    formats: [
      { key: "konfliktklaerung/day", title: "Konfliktklärung im Team – Ein Tag der Klärung", detail: "Tagesworkshop, angepasst an das Team und sein Anliegen." },
      { key: "teamreflexion/series", title: "Reflexionsreihe", detail: "Dauer, Rhythmus und Rahmen werden persönlich abgestimmt." },
    ],
    options: [],
    boundary: "Coaching und Moderation, keine Mediation im Sinne des Mediationsgesetzes, ausgebildete Supervision, Rechtsberatung oder rechtsverbindliche Streitbeilegung.",
  },
] as const;
