// Manuel's supplied Product Addendum, 2026-10-21. Formats are not topic categories.
export const offerGroups = [
  {
    id: "vortraege", label: "Vorträge",
    offers: [
      "Psychische Gesundheit und gesund führen",
      "Positive Leadership – Mitarbeiter stärken und Potenziale entfalten",
      "Positive Psychologie im Arbeitsalltag",
    ],
  },
  {
    id: "workshops", label: "Workshops",
    offers: [
      "Belastungen frühzeitig erkennen und handeln",
      "Gesund Führen",
      "Umgang mit psychisch belasteten Mitarbeitenden",
      "Wiedereingliederung nach psychischer Erkrankung",
      "Mentale Gesundheit im Homeoffice und hybriden Arbeiten",
      "Stressmanagement und Burnout-Prävention",
      "Positive Psychologie",
    ],
  },
  {
    id: "individuell", label: "Individuelle Angebote",
    offers: [
      "Resiliente und leistungsfähige Teams entwickeln",
      "Psychische Gefährdungsbeurteilung verstehen und umsetzen",
      "Psychische Belastungen verstehen",
      "Gefährdungsbeurteilung in der Praxis",
      "Kurzanalyse im Team (KiT)",
    ],
  },
  { id: "weitere", label: "Coaching / weitere Angebote", offers: ["Coaching", "Psychotherapie (HeilprG)"] },
] as const;
