// slide-writer zoo — CeTZ gadgets (optional, requires @preview/cetz)
// ====================================================================
// Small drawing helpers for the diagrams that recur in scientific slides:
// tensor-network nodes, finite-automaton states, boxes, and connectors.
// Each is called *inside* a `canvas{ … }` block where CeTZ coordinates apply.
//
//   #import "@preview/cetz:0.4.2": canvas
//   #import "zoo/gadgets_cetz.typ": make
//   #let D = make(palette)
//   #canvas(length: 0.6cm, {
//     import "@preview/cetz:0.4.2": draw
//     D.tensor((0,0), "A", [$A$])
//     D.tensor((3,0), "B", [$B$])
//     D.edge("A", "B")
//   })

#import "@preview/cetz:0.4.2": draw

#let make(pal) = (
  // Tensor-network node: small filled circle + label at its centre.
  "tensor": (loc, name, label, radius: 12pt) => {
    draw.circle(loc, radius: radius, name: name,
      fill: pal.primary.lighten(85%), stroke: pal.primary)
    draw.content(name, text(fill: pal.ink)[#label])
  },

  // Automaton state. Accept states get a double ring.
  "automaton-state": (loc, name, label, accept: false, radius: 16pt) => {
    draw.circle(loc, radius: radius, name: name,
      fill: pal.paper, stroke: pal.primary + 1pt)
    if accept {
      draw.circle(loc, radius: radius - 3pt, stroke: pal.primary + 0.8pt)
    }
    draw.content(name, text(fill: pal.ink)[#label])
  },

  // Connector between two named anchors, with an optional arrow head.
  "edge": (from, to, mark: (end: ">")) => {
    draw.line(from, to, mark: mark, stroke: pal.text_soft)
  },

  // Boxed node for flowcharts / architecture diagrams (auto-sized to its label).
  "flowbox": (loc, name, label) => {
    draw.content(loc, text(fill: pal.ink)[#label], name: name,
      frame: "rect", fill: pal.primary.lighten(90%), stroke: pal.primary,
      padding: (left: 8pt, right: 8pt, top: 4pt, bottom: 4pt))
  },
)
