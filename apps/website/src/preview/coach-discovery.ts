import { publicElisabethOfferGroups } from "./elisabeth-offers";
import { guelcanOfferFamilies } from "./guelcan-offers";
import { goranOffer } from "./goran-offers";
import { workshops } from "./susanne-klemm";

// Only approved active public offering copy; no provisional source candidates.
const publicOfferings: Record<string, readonly string[]> = {
  "coaches/elisabeth-schwabauer": publicElisabethOfferGroups.flatMap((group) => group.offers),
  "coaches/susanne-klemm": workshops,
  "coaches/goran-celic": [goranOffer.title, ...goranOffer.formats.map((format) => format.title)],
  "coaches/guelcan-elmas-brandes": guelcanOfferFamilies.flatMap((family) =>
    [family.title, ...family.formats.map((format) => format.title), ...family.options]),
};

export function publicOfferKeywords(profilePath: string): readonly string[] {
  return publicOfferings[profilePath] ?? [];
}
