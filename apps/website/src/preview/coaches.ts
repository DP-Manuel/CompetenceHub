import { coaches as productionCoaches } from "../data/coaches";
import { historicalCoaches } from "./historical-coaches";
import { susanneKlemm } from "./susanne-klemm";

export const coaches = [
  ...productionCoaches.filter((coach) => coach.kind === "approved"),
  ...historicalCoaches.filter((coach) => coach.profilePath !== "coaches/christian-galvano"),
  susanneKlemm,
];
