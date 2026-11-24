import { fitsHub, hubEdgePath, moveHubDisc, type Disc, type Point, type Stage } from "./hub-geometry";

const desktop = "(min-width: 64rem) and (any-hover: hover) and (any-pointer: fine)";
const dragThreshold = 7;

interface HubNode {
  id: string;
  link: HTMLAnchorElement;
  position: HTMLElement;
  home: Point;
  center: Point;
  radius: number;
}

interface Gesture {
  node: HubNode;
  pointer: number;
  first: Point;
  last: Point;
  origin: Point;
  moved: boolean;
}

export function enableHubDrag(graph: HTMLElement) {
  const tools = graph.parentElement?.querySelector<HTMLElement>("[data-hub-tools]");
  const reset = tools?.querySelector<HTMLButtonElement>("[data-hub-reset]");
  const core = graph.querySelector<HTMLElement>('[data-node="core"]');
  const paths = [...graph.querySelectorAll<SVGPathElement>("[data-edge]")];
  const nodes = [...graph.querySelectorAll<HTMLAnchorElement>("a[data-grab-node]")].flatMap((link) => {
    const position = link.parentElement;
    const id = link.dataset.node;
    if (!position || !id) return [];
    const home = { x: Number(position.dataset.homeX) / 100, y: Number(position.dataset.homeY) / 100 };
    return [{ id, link, position, home, center: home, radius: 0 }];
  });
  if (!tools || !reset || !core || !nodes.length || nodes.some(({ home }) => !Number.isFinite(home.x + home.y))) return;

  const media = matchMedia(desktop);
  let size: Stage = { width: 0, height: 0 };
  let coreRadius = 0;
  let gesture: Gesture | undefined;
  let blockClick = false;
  let frame = 0;
  const pixel = (p: Point): Point => ({ x: p.x * size.width, y: p.y * size.height });
  const normalized = (p: Point): Point => ({ x: p.x / size.width, y: p.y / size.height });
  const obstaclesFor = (id: string): Disc[] => [
    { x: size.width / 2, y: size.height / 2, radius: coreRadius },
    ...nodes.filter((node) => node.id !== id).map((node) => ({ ...pixel(node.center), radius: node.radius })),
  ];
  const highlight = (id?: string) => {
    if (id) graph.dataset.dragging = id;
    else delete graph.dataset.dragging;
    nodes.forEach(({ id: nodeId, link }) => link.toggleAttribute("data-dragged", nodeId === id));
    paths.forEach((edge) => edge.toggleAttribute("data-drag-edge",
      Boolean(id && (edge.dataset.from === id || edge.dataset.to === id))));
  };

  function render() {
    const points = new Map<string, Point>([["core", { x: 600, y: 380 }]]);
    for (const node of nodes) {
      node.position.style.setProperty("--drag-x", `${node.center.x * 100}%`);
      node.position.style.setProperty("--drag-y", `${node.center.y * 100}%`);
      points.set(node.id, { x: node.center.x * 1200, y: node.center.y * 760 });
    }
    paths.forEach((edge, index) => {
      const from = points.get(edge.dataset.from || "");
      const to = points.get(edge.dataset.to || "");
      if (from && to) edge.setAttribute("d", hubEdgePath(from, to, index));
    });
    const moved = nodes.some(({ center, home }) => center.x !== home.x || center.y !== home.y);
    // Keep reset focus even after it resets the layout.
    reset!.setAttribute("aria-disabled", String(!moved));
  }

  function finish(revert = false) {
    if (!gesture) return;
    const { node, pointer, moved, origin } = gesture;
    gesture = undefined;
    cancelAnimationFrame(frame);
    frame = 0;
    highlight();
    if (moved) blockClick = true;
    if (revert) node.center = origin;
    if (node.link.hasPointerCapture(pointer)) node.link.releasePointerCapture(pointer);
    if (moved) render();
  }

  function move() {
    frame = 0;
    if (!gesture?.moved) return;
    const { node, first, last, origin } = gesture;
    const current = pixel(node.center);
    const source = pixel(origin);
    const next = moveHubDisc({ ...current, radius: node.radius }, {
      x: source.x + last.x - first.x,
      y: source.y + last.y - first.y,
    }, size, obstaclesFor(node.id));
    if (next.x === current.x && next.y === current.y) return;
    node.center = normalized(next);
    render();
  }

  function measure() {
    tools!.hidden = !media.matches;
    graph.toggleAttribute("data-hub-draggable", media.matches);
    if (!media.matches) {
      finish();
      return;
    }
    const { width, height } = graph.getBoundingClientRect();
    if (width <= 0 || height <= 0) return;
    if (width === size.width && height === size.height) return;
    finish();
    size = { width, height };
    coreRadius = core!.offsetWidth / 2;
    for (const node of nodes) node.radius = node.link.offsetWidth / 2;
    if (nodes.some((node) => !fitsHub(pixel(node.center), node.radius, size, obstaclesFor(node.id)))) {
      for (const node of nodes) node.center = node.home;
    }
    render();
  }

  graph.addEventListener("pointerdown", () => { blockClick = false; }, { capture: true });
  graph.addEventListener("click", (event) => {
    if (!blockClick || event.detail === 0 || !(event.target instanceof Element) || !event.target.closest("a[data-node]")) return;
    event.preventDefault();
    event.stopImmediatePropagation();
  }, { capture: true });

  for (const node of nodes) {
    const link = node.link;
    link.addEventListener("dragstart", (event) => { if (media.matches) event.preventDefault(); });
    link.addEventListener("pointerdown", (event) => {
      if (!media.matches || !size.width || gesture || !event.isPrimary || event.pointerType !== "mouse"
        || event.button !== 0 || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
      const first = { x: event.clientX, y: event.clientY };
      gesture = { node, pointer: event.pointerId, first, last: first, origin: node.center, moved: false };
      link.setPointerCapture(event.pointerId);
    });
    link.addEventListener("pointermove", (event) => {
      if (!gesture || gesture.pointer !== event.pointerId) return;
      gesture.last = { x: event.clientX, y: event.clientY };
      if (!gesture.moved) {
        if (Math.hypot(event.clientX - gesture.first.x, event.clientY - gesture.first.y) < dragThreshold) return;
        gesture.moved = true;
        highlight(node.id);
      }
      if (!frame) frame = requestAnimationFrame(move);
    });
    link.addEventListener("pointerup", (event) => {
      if (gesture?.pointer !== event.pointerId) return;
      if (!gesture.moved && Math.hypot(event.clientX - gesture.first.x, event.clientY - gesture.first.y) >= dragThreshold) {
        gesture.moved = true;
      }
      if (gesture.moved) {
        gesture.last = { x: event.clientX, y: event.clientY };
        cancelAnimationFrame(frame);
        move();
      }
      finish();
    });
    for (const type of ["pointercancel", "lostpointercapture"]) {
      link.addEventListener(type, (event) => {
        if ((event as PointerEvent).pointerId === gesture?.pointer) finish();
      });
    }
  }

  graph.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && gesture) finish(true);
  });
  reset.addEventListener("click", () => {
    if (reset.getAttribute("aria-disabled") === "true") return;
    finish();
    for (const node of nodes) node.center = node.home;
    render();
  });
  new ResizeObserver(measure).observe(graph);
  media.addEventListener("change", measure);
  measure();
}
