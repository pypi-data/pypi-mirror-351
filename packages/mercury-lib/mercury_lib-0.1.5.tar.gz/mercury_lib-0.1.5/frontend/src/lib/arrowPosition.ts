import { Node } from "../types/node";

export function computeEdgeGeometry(
  source: Node,
  target: Node,
  hasReverse: boolean,
  strength = 0.3,
): {
  start: [number, number];
  end: [number, number];
  control?: [number, number];
  control2?: [number, number]; // <-- second control for cubic
} {
  const x1 = source.x!,
    y1 = source.y!;
  const x2 = target.x!,
    y2 = target.y!;

  const start: [number, number] = [x1, y1];
  const end: [number, number] = [x2, y2];

  if (!hasReverse) {
    return { start, end };
  }

  if (x1 === x2 && y1 === y2) {
    const radius = 80;
    const angle = Math.PI / 2; // downward
    const spread = Math.PI / 2; // wide curve

    const angle1 = angle - spread / 2;
    const angle2 = angle + spread / 2;

    const control: [number, number] = [
      x1 + radius * Math.cos(angle1),
      y1 + radius * Math.sin(angle1),
    ];

    const control2: [number, number] = [
      x1 + radius * Math.cos(angle2),
      y1 + radius * Math.sin(angle2),
    ];

    return { start, end, control, control2 };
  }

  const dx = x2 - x1;
  const dy = y2 - y1;
  const distance = Math.sqrt(dx * dx + dy * dy);
  const offset = strength * distance;

  const perpX = -dy / distance;
  const perpY = dx / distance;

  const cx = (x1 + x2) / 2 + perpX * offset;
  const cy = (y1 + y2) / 2 + perpY * offset;
  const control: [number, number] = [cx, cy];

  return { start, end, control };
}

export function calculateCurvedPath(
  source: Node,
  target: Node,
  hasReverse: boolean,
): string {
  const { start, end, control, control2 } = computeEdgeGeometry(
    source,
    target,
    hasReverse,
  );

  if (control2) {
    // Self-loop using cubic Bézier
    return `M${start[0]},${start[1]} C${control![0]},${control![1]} ${control2[0]},${control2[1]} ${end[0]},${end[1]}`;
  }

  if (control) {
    return `M${start[0]},${start[1]} Q${control[0]},${control[1]} ${end[0]},${end[1]}`;
  }

  return `M${start[0]},${start[1]} L${end[0]},${end[1]}`;
}

export function calculateLinkLabelPosition(
  source: Node,
  target: Node,
  hasReverse: boolean,
): [number, number] {
  const { start, end, control, control2 } = computeEdgeGeometry(
    source,
    target,
    hasReverse,
  );

  if (control2) {
    // For self-loop: average all 4 points (including start/end)
    const avgX = (start[0] + control![0] + control2[0] + end[0]) / 4;
    const avgY = (start[1] + control![1] + control2[1] + end[1]) / 4;
    return [avgX, avgY];
  }

  if (control) {
    return control;
  }

  return [(start[0] + end[0]) / 2, (start[1] + end[1]) / 2];
}
