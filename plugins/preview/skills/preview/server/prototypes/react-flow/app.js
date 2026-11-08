// Render a node/edge statechart with HTML labels, and lay it out again whenever a label's size changes.
(() => {
  const { createContext, createElement: h, memo, useContext, useEffect, useMemo, useRef, useState } = React;
  const {
    ReactFlow, ReactFlowProvider, Handle, Position, BaseEdge, EdgeLabelRenderer, Controls, ControlButton, Background,
    useNodesState, useReactFlow,
  } = window.ReactFlow;

  const SHAPES = { start: 'circle', end: 'circle', choice: 'diamond', state: 'rect' };
  const DIRECTIONS = ['TB', 'BT', 'LR', 'RL'];

  function validate(graph) {
    const fail = (message) => { throw new Error(message); };
    const text = (value) => typeof value === 'string' && value.trim() !== '';
    if (!graph || !Array.isArray(graph.nodes) || !Array.isArray(graph.edges)) fail('The diagram needs nodes and edges arrays.');
    const direction = graph.direction ?? 'TB';
    if (!DIRECTIONS.includes(direction)) fail(`Direction must be one of ${DIRECTIONS.join(', ')}.`);
    const nodes = new Map();
    for (const node of graph.nodes) {
      if (!text(node?.id) || nodes.has(node.id)) fail(`Node IDs must be unique non-empty strings: ${JSON.stringify(node?.id)}.`);
      if (!Object.hasOwn(SHAPES, node.kind)) fail(`Node ${node.id} has an unknown kind: ${JSON.stringify(node.kind)}.`);
      if (node.kind === 'state' ? !text(node.label) : node.label !== undefined) {
        fail(`Node ${node.id}: state nodes need a label; ${node.kind} nodes have none.`);
      }
      nodes.set(node.id, node);
    }
    const edges = new Set();
    for (const edge of graph.edges) {
      if (!text(edge?.id) || edges.has(edge.id)) fail(`Edge IDs must be unique non-empty strings: ${JSON.stringify(edge?.id)}.`);
      if (!nodes.has(edge.source) || !nodes.has(edge.target)) fail(`Edge ${edge.id} must connect two existing nodes.`);
      if (edge.label !== undefined && !text(edge.label)) fail(`Edge ${edge.id} has an empty or non-text label.`);
      edges.add(edge.id);
    }
    return { direction, nodes: graph.nodes, edges: graph.edges, lookup: nodes };
  }

  // Where the ray from the node's center toward a point leaves the node's visible shape.
  function boundary(kind, box, toward) {
    const dx = toward.x - box.x;
    const dy = toward.y - box.y;
    const a = box.width / 2;
    const b = box.height / 2;
    const shape = SHAPES[kind];
    const t = shape === 'circle' ? a / Math.hypot(dx, dy)
      : shape === 'diamond' ? 1 / (Math.abs(dx) / a + Math.abs(dy) / b)
        : Math.min(a / Math.abs(dx), b / Math.abs(dy));
    return { x: box.x + dx * t, y: box.y + dy * t };
  }

  // A B-spline through the route's points (d3's curveBasis), which starts and ends at the end points.
  function basisPath(points) {
    const [first, ...rest] = points;
    let d = `M${first.x},${first.y}`;
    if (rest.length === 1) return d + `L${rest[0].x},${rest[0].y}`;
    let [p0, p1] = points;
    d += `L${(5 * p0.x + p1.x) / 6},${(5 * p0.y + p1.y) / 6}`;
    for (const p of [...points.slice(2), points.at(-1)]) {
      d += `C${(2 * p0.x + p1.x) / 3},${(2 * p0.y + p1.y) / 3} ${(p0.x + 2 * p1.x) / 3},${(p0.y + 2 * p1.y) / 3} `
        + `${(p0.x + 4 * p1.x + p.x) / 6},${(p0.y + 4 * p1.y + p.y) / 6}`;
      [p0, p1] = [p1, p];
    }
    return d + `L${p1.x},${p1.y}`;
  }

  function computeLayout(graph, sizes) {
    const g = new dagre.graphlib.Graph({ multigraph: true });
    g.setGraph({ rankdir: graph.direction, nodesep: 48, ranksep: 36, edgesep: 24, marginx: 24, marginy: 24 });
    for (const node of graph.nodes) g.setNode(node.id, { ...sizes.get('node:' + node.id) });
    for (const edge of graph.edges) {
      const label = edge.label === undefined ? { width: 0, height: 0 } : sizes.get('edge:' + edge.id);
      g.setEdge(edge.source, edge.target, { ...label, labelpos: 'c' }, edge.id);
    }
    dagre.layout(g);
    // Round node corners to whole pixels for crisp text, and route edges against the rounded boxes.
    const positions = new Map();
    const boxes = new Map();
    for (const node of graph.nodes) {
      const { x, y, width, height } = g.node(node.id);
      const position = { x: Math.round(x - width / 2), y: Math.round(y - height / 2) };
      positions.set(node.id, position);
      boxes.set(node.id, { x: position.x + width / 2, y: position.y + height / 2, width, height });
    }
    const routes = new Map();
    for (const edge of graph.edges) {
      const { points, x, y } = g.edge({ v: edge.source, w: edge.target, name: edge.id });
      const source = boxes.get(edge.source);
      const target = boxes.get(edge.target);
      const inner = points.slice(1, -1);
      const route = [
        boundary(graph.lookup.get(edge.source).kind, source, inner[0] ?? target),
        ...inner,
        boundary(graph.lookup.get(edge.target).kind, target, inner.at(-1) ?? source),
      ];
      routes.set(edge.id, { path: basisPath(route), label: { x, y } });
    }
    const { width, height } = g.graph();
    return { positions, routes, width, height };
  }

  const Measure = createContext(null);

  const ShapeNode = memo(function ShapeNode({ data }) {
    const measure = useContext(Measure);
    const label = data.kind === 'state' && data.label.split('\n').map((line, index) => h('p', { key: index }, line));
    return h('div', {
      ref: measure('node:' + data.id),
      className: `node ${data.kind}` + (label ? ' nopan' : ''),
      'data-node-id': data.id,
    },
    label,
    h(Handle, { type: 'target', position: Position.Top, isConnectable: false }),
    h(Handle, { type: 'source', position: Position.Bottom, isConnectable: false }));
  });

  function RoutedEdge({ id, source, target, data }) {
    const measure = useContext(Measure);
    const { label, route } = data;
    const center = route?.label ?? { x: 0, y: 0 };
    return h(React.Fragment, null,
      route && h(BaseEdge, { id, path: route.path, markerEnd: 'url(#arrow)', interactionWidth: 0 }),
      label !== undefined && h(EdgeLabelRenderer, null, h('div', {
        ref: measure('edge:' + id),
        className: 'edge-label nopan',
        'data-edge-id': id,
        'data-source': source,
        'data-target': target,
        style: { transform: `translate(-50%, -50%) translate(${center.x}px, ${center.y}px)` },
      }, label)));
  }

  const nodeTypes = { shape: ShapeNode };
  // React Flow's own fit-view icon, which its Controls do not export.
  const FIT_ICON = 'M3.692 4.63c0-.53.4-.938.939-.938h5.215V0H4.708C2.13 0 0 2.054 0 4.63v5.216h3.692V4.631zM27.354 0h-5.2v3.692h5.17c.53 0 .984.4.984.939v5.215H32V4.631A4.624 4.624 0 0027.354 0zm.954 24.83c0 .532-.4.94-.939.94h-5.215v3.768h5.215c2.577 0 4.631-2.13 4.631-4.707v-5.139h-3.692v5.139zm-23.677.94c-.531 0-.939-.4-.939-.94v-5.138H0v5.139c0 2.577 2.13 4.707 4.708 4.707h5.138V25.77H4.631z';
  const edgeTypes = { routed: RoutedEdge };

  // Show the layout at up to natural size in a canvas that fills the window and grows with the layout,
  // so longer labels lengthen the page instead of shrinking the text.
  function defaultView(layout) {
    const main = document.getElementById('diagram');
    const zoom = Math.min(1, main.clientWidth / layout.width);
    const free = window.innerHeight - (main.getBoundingClientRect().top + window.scrollY);
    const height = Math.max(Math.ceil(layout.height * zoom), free);
    const viewport = { x: (main.clientWidth - layout.width * zoom) / 2, y: (height - layout.height * zoom) / 2, zoom };
    return { viewport, height };
  }

  function Diagram({ graph }) {
    const flow = useReactFlow();
    const [layout, setLayout] = useState(null);
    const [nodes, setNodes, onNodesChange] = useNodesState(useMemo(() => graph.nodes.map((node) => ({
      id: node.id, type: 'shape', position: { x: 0, y: 0 }, data: node,
    })), [graph]));
    const [height, setHeight] = useState(null);
    const userMoved = useRef(false);

    // One observer measures every label; a layout runs only after a measured size actually changes.
    const [measure] = useState(() => {
      const sizes = new Map();
      const keys = new Map();
      const refs = new Map();
      const required = [
        ...graph.nodes.map((node) => 'node:' + node.id),
        ...graph.edges.filter((edge) => edge.label !== undefined).map((edge) => 'edge:' + edge.id),
      ];
      let version = 0;
      const observer = new ResizeObserver((entries) => {
        let changed = false;
        for (const entry of entries) {
          const key = keys.get(entry.target);
          const [box] = entry.borderBoxSize;
          const previous = sizes.get(key);
          if (previous?.width === box.inlineSize && previous?.height === box.blockSize) continue;
          sizes.set(key, { width: box.inlineSize, height: box.blockSize });
          changed = true;
        }
        if (!changed || !required.every((key) => sizes.has(key))) return;
        const next = { ...computeLayout(graph, sizes), version: ++version };
        setLayout(next);
        setNodes((current) => current.map((node) => ({ ...node, position: next.positions.get(node.id) })));
      });
      return (key) => {
        if (!refs.has(key)) {
          let current = null;
          refs.set(key, (element) => {
            if (current) {
              observer.unobserve(current);
              keys.delete(current);
            }
            current = element;
            if (element) {
              keys.set(element, key);
              observer.observe(element, { box: 'border-box' });
            }
          });
        }
        return refs.get(key);
      };
    });

    const edges = useMemo(() => graph.edges.map((edge) => ({
      id: edge.id, source: edge.source, target: edge.target, type: 'routed',
      data: { label: edge.label, route: layout?.routes.get(edge.id) },
    })), [graph, layout]);

    // Show each new layout in full until the viewer pans or zooms; the fit-view control resumes that.
    const showAll = (moved) => {
      const view = defaultView(layout);
      setHeight(view.height);
      if (!moved) flow.setViewport(view.viewport);
    };
    useEffect(() => {
      if (layout) showAll(userMoved.current);
    }, [layout]);
    const moved = () => { userMoved.current = true; };

    return h(Measure.Provider, { value: measure },
      h('div', {
        className: height === null ? 'flow pending' : 'flow',
        'data-layouts': layout?.version ?? 0,
        style: { height: height ?? '80vh' },
      },
      h(ReactFlow, {
        nodes, edges, nodeTypes, edgeTypes, onNodesChange,
        nodesDraggable: false, nodesConnectable: false, elementsSelectable: false,
        nodesFocusable: false, edgesFocusable: false,
        // The wheel scrolls the page; pinch, Ctrl+wheel and the controls zoom.
        zoomOnScroll: false, preventScrolling: false,
        minZoom: 0.2, maxZoom: 4,
        onMoveStart: (event) => { if (event) moved(); },
      },
      h(Background, { gap: 24, size: 1.5 }),
      layout && h(Controls, { position: 'top-left', showInteractive: false, showFitView: false, onZoomIn: moved, onZoomOut: moved },
        h(ControlButton, {
          className: 'react-flow__controls-fitview', title: 'fit view', 'aria-label': 'fit view',
          onClick: () => { userMoved.current = false; showAll(false); },
        }, h('svg', { viewBox: '0 0 32 30' }, h('path', { d: FIT_ICON })))))));
  }

  const main = document.getElementById('diagram');
  fetch('infg-statechart.json')
    .then((response) => {
      if (!response.ok) throw new Error(`infg-statechart.json returned HTTP ${response.status}.`);
      return response.json();
    })
    .then((graph) => {
      ReactDOM.createRoot(main).render(h(ReactFlowProvider, null, h(Diagram, { graph: validate(graph) })));
    })
    .catch((error) => {
      const message = document.createElement('p');
      message.className = 'error';
      message.setAttribute('role', 'alert');
      message.textContent = 'Diagram could not be rendered: ' + error.message;
      main.replaceChildren(message);
    });
})();
