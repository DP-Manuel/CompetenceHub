/** @typedef {"workshop" | "seminar" | "meeting" | "lecture"} Format */
/** @typedef {{ id: string, height: number, alt: string, title: string, setup: string }} Photo */
/** @typedef {{ id: string, title: string, formats: readonly Format[], photos: readonly Photo[] }} Room */
/** @typedef {{ id: string, name: string, rooms: readonly Room[] }} Venue */
/** @typedef {{ id: string, name: string, publication: "preview" | "draft", venues: readonly Venue[],
 * unassignedRooms: readonly Room[], lead: string, preview: readonly string[], featured: readonly string[] }} City */

export const roomWidths = [480, 960, 1800];
export const venuePath = "veranstaltungsorte/";

/** @type {readonly City[]} */
const cities = [{
  id: "wuerzburg", name: "Würzburg", publication: "preview", venues: [],
  lead: "workshop-island",
  preview: ["workshop-island", "small-table", "open-u"],
  featured: ["shared-table", "seminar-side", "small-table", "chair-rows"],
  unassignedRooms: [
    { id: "table-island", title: "Raum mit Tischinsel", formats: ["workshop"], photos: [
      { id: "workshop-island", height: 1201, title: "Workshop an der Tischinsel", setup: "Tischinsel",
        alt: "Heller Raum mit breiter Tischinsel und Stühlen an mehreren Seiten" },
    ] },
    { id: "meeting-large", title: "Besprechungsansicht", formats: ["meeting", "workshop"], photos: [
      { id: "shared-table", height: 1200, title: "Austausch am gemeinsamen Tisch", setup: "Tischanordnung mit offener Mitte",
        alt: "Weiße Tische mit offener Mitte und Stühlen entlang der gegenüberliegenden Seiten" },
    ] },
    { id: "seminar-window", title: "Seminarraum mit Fensterfront", formats: ["seminar"], photos: [
      { id: "seminar-side", height: 1201, title: "Seminar mit Tischreihen", setup: "Tischreihen",
        alt: "Seitlicher Blick auf Tischreihen und eine lange Fensterfront" },
      { id: "seminar-front", height: 1201, title: "Derselbe Raum von vorn", setup: "Tischreihen",
        alt: "Frontaler Blick über dieselben Tischreihen zur Fensterfront" },
    ] },
    { id: "meeting-small", title: "Besprechungsraum im kleinen Kreis", formats: ["meeting"], photos: [
      { id: "small-table", height: 1201, title: "Gespräch im kleinen Kreis", setup: "Besprechungstisch",
        alt: "Ein einzelner Besprechungstisch mit Stühlen in einem kompakten Raum" },
    ] },
    { id: "lecture", title: "Vortragsansicht", formats: ["lecture"], photos: [
      { id: "chair-rows", height: 1110, title: "Vortrag mit Stuhlreihen", setup: "Stuhlreihen",
        alt: "Mehrere nach vorn ausgerichtete Stuhlreihen ohne Tische, seitlich eine Säule" },
    ] },
    { id: "seminar-light", title: "Seminaransicht mit Tischreihen", formats: ["seminar"], photos: [
      { id: "seminar-rows", height: 1201, title: "Seminar mit Arbeitsflächen", setup: "Tischreihen",
        alt: "Heller Raum mit geraden Tischreihen vor einer hellen Stirnwand" },
    ] },
    { id: "window-u", title: "Raumansicht mit U-Form", formats: ["workshop", "meeting"], photos: [
      { id: "open-u", height: 1200, title: "Austausch in U-Form", setup: "U-Form",
        alt: "U-förmig angeordnete Tische in einem Raum mit langer Fensterfront" },
    ] },
    { id: "window-rows", title: "Seminaransicht am Fenster", formats: ["seminar"], photos: [
      { id: "window-rows", height: 1201, title: "Tischreihen entlang der Fenster", setup: "Tischreihen",
        alt: "Schräger Blick von hinten auf helle Tischreihen neben hohen Fenstern" },
    ] },
    { id: "seminar-length", title: "Blick entlang der Tischreihen", formats: ["seminar"], photos: [
      { id: "long-rows", height: 1201, title: "Tischreihen aus seitlicher Perspektive", setup: "Tischreihen",
        alt: "Lange weiße Tischreihen mit dunklen Stühlen unter länglichen Deckenleuchten" },
    ] },
    { id: "seminar-window-wall", title: "Seminaransicht mit Blick nach vorn", formats: ["seminar"], photos: [
      { id: "angled-rows", height: 1201, title: "Tischreihen in einem langgezogenen Raum", setup: "Tischreihen",
        alt: "Weiße Tischreihen vor einer Fensterwand, von der Seite fotografiert" },
    ] },
    { id: "panorama", title: "Panorama der Tischordnung", formats: ["seminar"], photos: [
      { id: "wide-angle", height: 591, title: "Weiter Blick auf die Tischordnung", setup: "Tischreihen",
        alt: "Panorama eines Raums mit weißen Tischreihen und Stühlen" },
    ] },
  ],
}];

export const previewCities = cities.filter(({ publication }) => publication === "preview");

/** @param {City} city */
export const roomsFor = (city) => [...city.venues.flatMap(({ rooms }) => rooms), ...city.unassignedRooms];

/** @param {City} city @param {string} id */
export function photoFor(city, id) {
  const photo = roomsFor(city).flatMap(({ photos }) => photos).find((item) => item.id === id);
  if (!photo) throw new Error(`Venue photo is not in the city dataset: ${city.id}/${id}`);
  return photo;
}
