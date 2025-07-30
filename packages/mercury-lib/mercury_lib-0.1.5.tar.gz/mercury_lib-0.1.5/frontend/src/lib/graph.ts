import * as d3 from "d3";
import { Link } from "../types/link";
import { Node } from "../types/node";

export function createMarkers(
  svg: d3.Selection<SVGSVGElement, unknown, null, undefined>,
) {
  // Defining two markers because self loops need different offset
  svg
    .append("defs")
    .selectAll("marker")
    .data(["end"])
    .enter()
    .append("marker")
    .attr("id", (d) => d)
    .attr("viewBox", "0 -5 10 10")
    .attr("refX", 28)
    .attr("refY", 0)
    .attr("markerWidth", 6)
    .attr("markerHeight", 6)
    .attr("orient", "auto")
    .append("path")
    .attr("fill", "#aaa")
    .attr("d", "M0,-5L10,0L0,5");

  svg
    .append("defs")
    .selectAll("marker")
    .data(["loop-arrow"])
    .enter()
    .append("marker")
    .attr("id", (d) => d)
    .attr("viewBox", "0 -5 10 10")
    .attr("refX", 24)
    .attr("refY", -6)
    .attr("markerWidth", 6)
    .attr("markerHeight", 6)
    .attr("orient", "auto")
    .append("path")
    .attr("fill", "#aaa")
    .attr("d", "M0,-5L10,0L0,5");
}

export function createGlowEffect(
  svg: d3.Selection<SVGSVGElement, unknown, null, undefined>,
  color: string,
  intensity: number,
) {
  const defs = svg.append("defs");

  const filter = defs
    .append("filter")
    .attr("id", `glow-${color}`)
    .attr("x", "-50%")
    .attr("y", "-50%")
    .attr("width", "200%")
    .attr("height", "200%");

  // Add blur
  filter
    .append("feGaussianBlur")
    .attr("in", "SourceGraphic")
    .attr("stdDeviation", intensity) // ← Brighter glow by increasing blur
    .attr("result", "blur");

  // Add green color flood
  filter
    .append("feFlood")
    .attr("flood-color", color) // ← Green color
    .attr("flood-opacity", "1")
    .attr("result", "color");

  // Mask the flood over the blur
  filter
    .append("feComposite")
    .attr("in", "color")
    .attr("in2", "blur")
    .attr("operator", "in")
    .attr("result", "coloredBlur");

  // Merge with original graphic
  const merge = filter.append("feMerge");
  merge.append("feMergeNode").attr("in", "coloredBlur");
  merge.append("feMergeNode").attr("in", "SourceGraphic");
}

export function createLinks(
  svg: d3.Selection<SVGSVGElement, unknown, null, undefined>,
  links: Link[],
) {
  return svg
    .append("g")
    .attr("stroke", "#aaa")
    .selectAll("path")
    .data(links)
    .join("path")
    .attr("fill", "none")
    .attr("stroke-width", 2)
    .attr("marker-end", (d) => {
      return d.source === d.target ? "url(#loop-arrow)" : "url(#end)";
    });
}

export function createLinkLabels(
  svg: d3.Selection<SVGSVGElement, unknown, null, undefined>,
  links: Link[],
) {
  return svg
    .append("g")
    .selectAll("text")
    .data(links)
    .join("text")
    .text((d) => d.label)
    .attr("font-size", "12px")
    .attr("font-family", "sans-serif")
    .attr("fill", "#555")
    .attr("text-anchor", "middle")
    .attr("dominant-baseline", "central")
    .attr("pointer-events", "none");
}

export function createNodes(
  svg: d3.Selection<SVGSVGElement, unknown, null, undefined>,
  nodes: Node[],
  simulation: d3.Simulation<Node, undefined>,
) {
  return svg
    .append("g")
    .selectAll("circle")
    .data(nodes)
    .join("circle")
    .attr("r", 24)
    .attr("fill", "oklch(96.7% 0.003 264.542)")
    .attr("stroke", "oklch(37.3% 0.034 259.733)")
    .attr("stroke-width", 1.5)
    .call(
      d3
        .drag<SVGCircleElement, Node>()
        .on("start", (event, d) => {
          if (!event.active) simulation.alphaTarget(0.3).restart();
          d.fx = d.x;
          d.fy = d.y;
        })
        .on("drag", (event, d) => {
          d.fx = event.x;
          d.fy = event.y;
        })
        .on("end", (event, d) => {
          if (!event.active) simulation.alphaTarget(0);
          d.fx = null;
          d.fy = null;
        }) as any, // WARNING: Check up on this later
    );
}
export function createInitialFinalNodeDecorations(
  svg: d3.Selection<SVGSVGElement, unknown, null, undefined>,
  initialNode: Node,
  finalNodes: Node[],
  svgNodes: d3.Selection<
    d3.BaseType | SVGCircleElement,
    Node,
    SVGGElement,
    unknown
  >,
) {
  svg.selectAll(".final-inner-circle").remove();
  svg.selectAll(".initial-arrow").remove();

  svgNodes
    .filter((d) => finalNodes.map((node) => node.id).includes(d.id))
    .each(function (d) {
      svg
        .append<SVGCircleElement>("circle")
        .datum(d)
        .attr("class", "final-inner-circle")
        .attr("r", 20)
        .attr("fill", "none")
        .attr("stroke", "oklch(37.3% 0.034 259.733)")
        .attr("stroke-width", 1.5);
    });
  svgNodes
    .filter((d) => initialNode.id == d.id)
    .each(function (d) {
      svg
        .append<SVGPathElement>("path")
        .datum(d)
        .attr("class", "initial-arrow")
        .attr("fill", "oklch(37.3% 0.034 259.733)");
    });
}

export function createNodeLabels(
  svg: d3.Selection<SVGSVGElement, unknown, null, undefined>,
  nodes: Node[],
) {
  return svg
    .append("g")
    .selectAll("text")
    .data(nodes)
    .join("text")
    .text((d) => d.id)
    .attr("font-size", "10px")
    .attr("font-family", "sans-serif")
    .attr("text-anchor", "middle")
    .attr("dominant-baseline", "central")
    .attr("fill", "oklch(0% 0 0)")
    .attr("pointer-events", "none");
}
