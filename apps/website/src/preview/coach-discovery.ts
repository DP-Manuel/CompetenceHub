import { offerGroups } from "./elisabeth-offers";
import { guelcanOfferFamilies } from "./guelcan-offers";
import { workshops } from "./susanne-klemm";

// Only approved active public offering copy; no provisional source candidates.
const publicOfferings: Record<string, readonly string[]> = {
  "coaches/elisabeth-schwabauer": offerGroups.flatMap((group) => [...group.offers])
    .filter((offer) => offer !== "Psychotherapie (HeilprG)"),
  "coaches/susanne-klemm": workshops,
  "coaches/guelcan-elmas-brandes": guelcanOfferFamilies.flatMap((family) =>
    [family.title, ...family.formats.map((format) => format.title), ...family.options]),
};

export function publicOfferKeywords(profilePath: string): readonly string[] {
  return publicOfferings[profilePath] ?? [];
}
