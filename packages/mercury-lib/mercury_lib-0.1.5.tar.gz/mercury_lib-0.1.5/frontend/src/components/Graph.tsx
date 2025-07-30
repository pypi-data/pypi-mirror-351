import { useEffect, useRef } from "react";
import * as d3 from "d3";
import { Link } from "../types/link";
import { Node } from "../types/node";
import {
  createGlowEffect,
  createInitialFinalNodeDecorations,
  createLinkLabels,
  createLinks,
  createMarkers,
  createNodeLabels,
  createNodes,
} from "../lib/graph";
import {
  calculateCurvedPath,
  calculateLinkLabelPosition,
} from "../lib/arrowPosition";

type ForceGraphProps = {
  nodes: Node[];
  links: Link[];
  initialNode: Node;
  finalNodes: Node[];
  highlightedNodes: Node[];
  highlightedErrorNodes: Node[];
  highlightedSuccessNodes: Node[];
};

// Generic type to make it easier to read
type D3Selection<T extends d3.BaseType, U> = d3.Selection<
  T | d3.BaseType,
  U,
  SVGGElement,
  unknown
>;

const VIEWBOX_WIDTH = 1920;
const VIEWBOX_HEIGHT = 1080;
const ARROW_LENGTH = 30;
const LINK_LABEL_OFFSET = { x: -15, y: 15 };

export default function Graph({
  nodes,
  links,
  initialNode,
  finalNodes,
  highlightedNodes,
  highlightedErrorNodes,
  highlightedSuccessNodes,
}: ForceGraphProps) {
  const svgRef = useRef<SVGSVGElement>(null);

  function nodeIdSet(nodes: Node[]): Set<string> {
    return new Set(nodes.map((n) => n.id));
  }

  const highlightedIds = nodeIdSet(highlightedNodes);
  const highlightedIdsErrors = nodeIdSet(highlightedErrorNodes);
  const highlightedIdsSuccess = nodeIdSet(highlightedSuccessNodes);

  function updatePositions({
    svg,
    svgNodes,
    svgLinks,
    svgNodeLabels,
    svgLinkLabels,
    links,
  }: {
    svg: d3.Selection<SVGSVGElement, unknown, null, undefined>;
    svgNodes: D3Selection<SVGCircleElement, Node>;
    svgLinks: D3Selection<SVGPathElement, Link>;
    svgNodeLabels: D3Selection<SVGTextElement, Node>;
    svgLinkLabels: D3Selection<SVGTextElement, Link>;
    links: Link[];
  }) {
    svgNodes.attr("cx", (d) => d.x!).attr("cy", (d) => d.y!);

    svgLinks.attr("d", (d) => {
      const hasReverse = links.some(
        (l) => l.source === d.target && l.target === d.source,
      );
      return calculateCurvedPath(
        d.source as Node,
        d.target as Node,
        hasReverse,
      );
    });

    svgNodeLabels.attr("x", (d) => d.x!).attr("y", (d) => d.y!);

    svgLinkLabels.each(function (d) {
      const hasReverse = links.some(
        (l) => l.source === d.target && l.target === d.source,
      );

      const [x, y] = calculateLinkLabelPosition(
        d.source as Node,
        d.target as Node,
        hasReverse,
      );

      d3.select(this)
        .attr("x", x + LINK_LABEL_OFFSET.x)
        .attr("y", y + LINK_LABEL_OFFSET.y);
    });

    svg
      .selectAll<SVGCircleElement, Node>(".final-inner-circle")
      .attr("cx", (d) => d.x ?? 0)
      .attr("cy", (d) => d.y ?? 0);

    svg.selectAll<SVGCircleElement, Node>(".initial-arrow").attr("d", (d) => {
      const x = d.x ?? 0;
      const y = d.y ?? 0;

      // Triangle head pointing left
      const tipX = x - ARROW_LENGTH;
      const tipY = y;

      return `M${tipX - 7.5},${tipY - 6} L${tipX},${tipY} L${tipX - 7.5},${tipY + 6} Z`;
    });
  }

  useEffect(() => {
    if (!svgRef.current) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove(); // Clear previous render
    svg.attr("viewBox", `0 0 ${VIEWBOX_WIDTH} ${VIEWBOX_HEIGHT}`);

    const simulation = d3
      .forceSimulation<Node>(nodes)
      .force(
        "link",
        d3
          .forceLink<Node, Link>(links)
          .id((d) => d.id)
          .distance(350),
      )
      .force("charge", d3.forceManyBody().strength(-500))
      .force("center", d3.forceCenter(VIEWBOX_WIDTH / 2, VIEWBOX_HEIGHT / 2));

    createGlowEffect(svg, "green", 10);
    createGlowEffect(svg, "crimson", 8);
    createGlowEffect(svg, "yellow", 12);

    const svgLinks = createLinks(svg, links);
    const svgNodes = createNodes(svg, nodes, simulation);

    const svgLinkLabels = createLinkLabels(svg, links);
    const svgNodeLabels = createNodeLabels(svg, nodes);

    createMarkers(svg);
    createInitialFinalNodeDecorations(svg, initialNode, finalNodes, svgNodes);

    simulation.on("tick", () => {
      updatePositions({
        svg,
        svgNodes,
        svgLinks,
        svgNodeLabels,
        svgLinkLabels,
        links,
      });
    });
  }, []);

  useEffect(() => {
    if (!svgRef.current) return;
    const svg = d3.select(svgRef.current);

    svg.selectAll<SVGCircleElement, Node>("circle").attr("filter", (d) => {
      if (highlightedIds.has(d.id)) return "url(#glow-yellow)";
      if (highlightedIdsErrors.has(d.id)) return "url(#glow-crimson)";
      if (highlightedIdsSuccess.has(d.id)) return "url(#glow-green)";
      return null;
    });
  }, [highlightedNodes, highlightedErrorNodes, highlightedSuccessNodes]);

  return <svg ref={svgRef} className="absolute inset-0 z-0 w-full h-full" />;
}
