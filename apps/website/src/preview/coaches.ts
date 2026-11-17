import { coaches as productionCoaches } from "../data/coaches";
import { historicalCoaches } from "./historical-coaches";
import { susanneKlemm } from "./susanne-klemm";

// Owner pause17.11: retain Carolin's source for a later separately approved return.
export const coaches = [
  ...productionCoaches.filter((coach) => coach.kind === "approved"),
  ...historicalCoaches.filter((coach) => coach.profilePath !== "coaches/carolin-hupp"
    && !productionCoaches.some((current) => current.kind === "approved" && current.profilePath === coach.profilePath)),
  susanneKlemm,
];
