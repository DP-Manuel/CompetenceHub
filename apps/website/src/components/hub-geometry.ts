export type Point = { x: number; y: number };
export type Disc = Point & { radius: number };
export type Stage = { width: number; height: number };

const edgeClearance = 10;
const discClearance = 12;
const clamp = (value: number, min: number, max: number) =>
  Math.max(min, Math.min(max, value));

export function fitsHub(point: Point, radius: number, stage: Stage, obstacles: readonly Disc[]) {
  const margin = radius + edgeClearance;
  return point.x >= margin && point.y >= margin
    && point.x <= stage.width - margin && point.y <= stage.height - margin
    && obstacles.every((other) => Math.hypot(point.x - other.x, point.y - other.y)
      >= radius + other.radius + discClearance);
}

export function moveHubDisc(current: Disc, wanted: Point, stage: Stage, obstacles: readonly Disc[]): Point {
  const margin = current.radius + edgeClearance;
  const target = {
    x: clamp(wanted.x, margin, stage.width - margin),
    y: clamp(wanted.y, margin, stage.height - margin),
  };
  const dx = target.x - current.x;
  const dy = target.y - current.y;
  // Sweep even a coalesced pointer move; let a blocked disc slide along neighbors.
  const steps = Math.max(1, Math.ceil(Math.hypot(dx, dy) / 4));
  let point: Point = current;
  for (let i = 1; i <= steps; i += 1) {
    const to = { x: current.x + dx * i / steps, y: current.y + dy * i / steps };
    const candidates = [to, { x: to.x, y: point.y }, { x: point.x, y: to.y }];
    const next = candidates.find((option) =>
      Math.hypot(option.x - point.x, option.y - point.y) <= 4.01
      && fitsHub(option, current.radius, stage, obstacles)
    );
    if (next) point = next;
  }
  return point;
}

export function hubEdgePath(from: Point, to: Point, index: number) {
  const dx = to.x - from.x;
  const dy = to.y - from.y;
  const length = Math.max(Math.hypot(dx, dy), 1);
  const bend = (index % 2 === 0 ? 1 : -1) * Math.min(27, length * 0.055);
  return `M${from.x.toFixed(2)} ${from.y.toFixed(2)} Q${((from.x + to.x) / 2 - dy / length * bend).toFixed(2)} ${((from.y + to.y) / 2 + dx / length * bend).toFixed(2)} ${to.x.toFixed(2)} ${to.y.toFixed(2)}`;
}
