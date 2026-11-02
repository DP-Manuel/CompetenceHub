export interface Boundary { text: string; excluded_services: string[] }
export interface Duration {
  label?: string; clock_start?: string; clock_end?: string; minutes?: number;
  weeks?: number; sessions_per_week?: number; session_minutes?: number;
}
export interface Variant { kind: "variant" | "add_on" | "option"; title: string; description: string | null; duration: Duration | null }
export interface Offering {
  title: string; type: string; description: string | null; ordering: number;
  service_domains?: string[]; bookable?: boolean; duration?: Duration | null;
  delivery_mode?: string; delivery_label?: string | null; target_groups?: string[];
  target_focus?: string[]; program_modules?: string[]; boundaries?: Boundary[]; variants?: Variant[];
}
export interface Family {
  title: string; description: string | null; target_groups: string[]; target_focus: string[];
  service_domains: string[]; boundaries: Boundary[]; variants: Variant[]; formats: Offering[];
}
export interface ProjectedCoach {
  slug: string; route: string; initials: string;
  display_name: string; academic_suffix: string | null; short_intro: string;
  description: string | null; professional_background: string | null; profile_path: string;
  competencies: string[]; target_groups: string[];
  topics: { name: string; categories: string[] }[];
  assets: { type: "portrait"; reference: string; sha256: string; alt_text: string }[];
  offerings: Offering[]; roles?: { code: string; label: string }[];
  qualifications?: { label: string; issuer: string | null; type: string | null }[];
  boundaries?: Boundary[]; offering_families?: Family[];
  presentation?: {
    teaser: string | null; focus_labels: string[]; background_labels: string[]; languages: string[];
    sections: { kind: string; headings: string[]; paragraphs: string[] }[];
    topic_cards: { title: string; text: string }[]; quote: string | null;
    external_links: { label: string; url: string }[]; initials: string | null;
    portrait_width: number | null; portrait_height: number | null;
  };
}
