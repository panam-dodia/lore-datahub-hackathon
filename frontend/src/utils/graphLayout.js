import dagre from "dagre";

const MIN_WIDTH = 160;
const MAX_WIDTH = 340;
const HORIZONTAL_PADDING = 28; // node's own left+right padding, plus a little breathing room
const NODE_HEIGHT = 60;
const LABEL_FONT = "500 14px sans-serif"; // must match the node's actual rendered font

let measureCtx;

function measureTextWidth(text) {
  if (!measureCtx) {
    measureCtx = document.createElement("canvas").getContext("2d");
  }
  measureCtx.font = LABEL_FONT;
  return measureCtx.measureText(text).width;
}

function widthForLabel(label) {
  const longestLine = Math.max(...label.split("\n").map(measureTextWidth));
  return Math.min(MAX_WIDTH, Math.max(MIN_WIDTH, longestLine + HORIZONTAL_PADDING));
}

export function layoutGraph(nodes, edges) {
  const g = new dagre.graphlib.Graph();
  g.setGraph({ rankdir: "LR", nodesep: 32, ranksep: 90 });
  g.setDefaultEdgeLabel(() => ({}));

  const widths = new Map();
  nodes.forEach((node) => {
    const width = widthForLabel(node.data.label);
    widths.set(node.id, width);
    g.setNode(node.id, { width, height: NODE_HEIGHT });
  });
  edges.forEach((edge) => {
    g.setEdge(edge.source, edge.target);
  });

  dagre.layout(g);

  return nodes.map((node) => {
    const { x, y } = g.node(node.id);
    const width = widths.get(node.id);
    return {
      ...node,
      position: { x: x - width / 2, y: y - NODE_HEIGHT / 2 },
      style: { ...node.style, width },
    };
  });
}
