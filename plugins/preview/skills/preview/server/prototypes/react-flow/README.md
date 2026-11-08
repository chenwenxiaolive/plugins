# React Flow statechart prototype

A standalone page that renders the InfG statechart from
[issue #64](https://github.com/chenwenxiaolive/plugins/issues/64) with ordinary
HTML node and edge labels, to test whether a translation extension can translate
them and whether the diagram stays correct when translation changes label sizes.
The preview server does not use it; it is published as a static directory.

## Files

- `index.html`: the page, its theme selector (the preview pages' choices and storage key) and the script order.
- `app.js`: input validation, measurement, Dagre layout, edge routing and the React Flow components.
- `app.css`: light and dark styles.
- `infg-statechart.json`: the issue's Mermaid fixture in the input model below.
- `vendor/`: pinned third-party files with their licenses, recorded in `vendor/sources.json`.

## Input model

```json
{
  "direction": "TB",
  "nodes": [
    { "id": "Sample", "kind": "state", "label": "Sample and emit a token" },
    { "id": "Stop", "kind": "choice" }
  ],
  "edges": [
    { "id": "Sample-Stop", "source": "Sample", "target": "Stop", "label": "optional text" }
  ]
}
```

- `direction` is `TB` (default), `BT`, `LR` or `RL`.
- Node `kind` is `start`, `end`, `choice` or `state`. Only `state` nodes have a `label`, where `\n` separates lines; the others are drawn as a filled circle, a ringed circle and a diamond.
- Node and edge IDs are unique strings that never change with the text, so translation cannot change which nodes an edge joins. Edge `label` is optional.
- Input order matters: Dagre breaks cycles against it, so a loop's returning edge should come after the edges that enter the loop.
- The page validates the model before rendering and shows the first error instead of a partial diagram.

This model is not Mermaid. Mermaid's `[*]` start and end become separate `start`
and `end` nodes, `<<choice>>` states become `choice` nodes, and state aliases become
IDs.

## Behavior

- Each label is a `<p>` line in a node, or a `<div>` in React Flow's edge label layer: HTML outside SVG, which draws only edges, arrowheads and the dot grid. Dragging across a label selects its text; dragging elsewhere pans.
- One `ResizeObserver` watches every label's border box. When a measured size changes, Dagre lays the graph out again with the measured node and label sizes, and edges are routed through Dagre's points to the visible shape of each node. Pan, zoom and theme changes do not change sizes, so they never trigger a layout.
- The canvas fills the window and grows with the layout; the layout is shown at natural size (scaled down only if wider than the window), so longer labels lengthen the page instead of shrinking the text. A new layout is shown in full until the viewer pans or zooms; the fit-view control restores that view.
- The wheel scrolls the page. Ctrl+wheel, pinch and the zoom controls zoom; dragging the background pans.
- Themes change only CSS variables, so React does not render again and translated text stays in place.
- React Flow is used read-only: nodes cannot be selected, dragged or connected, and `onlyRenderVisibleElements` stays off so no label is unmounted while off screen.

## Bundled files

| Package | Version | Files |
| --- | --- | --- |
| `react`, `react-dom` | 18.3.1 | UMD production builds (React 19 ships no UMD build) |
| `@xyflow/react` | 12.12.0 | `dist/umd/index.js` (global `ReactFlow`, with its dependencies) and `dist/style.css` |
| `@dagrejs/dagre` | 3.1.3 | `dist/dagre.min.js` (global `dagre`, with graphlib) |

Each file is the npm package's file at the path in `vendor/sources.json`, which
records its jsDelivr URL, SHA-256 and size; `tests/preview/test_assets.py` checks
the hashes. To reproduce or update one, download its URL and compare the hash, or
extract the same path from the npm tarball (`npm pack <package>@<version>`). The
React Flow UMD build expects React's automatic JSX runtime as a global
`jsxRuntime`, which `index.html` defines from `React.createElement` before loading
it. Together the vendor files are about 400 KB before compression.

## Validation

Publish the directory as is under the preview root, for example
`/preview/<task>/`, and open `<task>/index.html`; all asset paths are relative and
nothing is fetched from another origin.

The browser check serves this directory with `server.py` and uses an existing
Playwright and Chromium, like the Mermaid check in [server/README.md](../../README.md#tests):

```sh
PREVIEW_TEST_TMPDIR=/path/outside/checkout \
PREVIEW_PLAYWRIGHT_MODULE=/path/to/node_modules/playwright-core \
  node plugins/preview/skills/preview/server/tests/react-flow.browser.cjs
```

At 1440×900 it checks the fixture's nodes, transitions and labels; that every
visible label is selectable HTML outside SVG; and that no label overlaps or
overflows another, every edge starts and ends on its own nodes' shapes and passes
through its label. It then replaces every label with a longer translation, and
then restores each label and adds a Chinese line below it as bilingual mode does,
each change outside React. Each must cause exactly one layout that passes the same
checks with the whole diagram shown at natural size. Wheel scrolling, panning,
zooming, fit-view and theme switching must keep the translated text without
another layout. It also checks invalid input, and fails on requests to another
origin, page errors and console errors or warnings. It saves light and dark
screenshots before and after the bilingual change in its run directory.

## Immersive Translate experiment

Text changes made by the browser check do not show that the extension translates
these labels; that needs a desktop browser with the extension:

1. Publish this directory under `/preview` and open its `index.html` through the preview URL in desktop Chrome or Edge with Immersive Translate installed.
2. Record the browser version, the extension version, the translation service, the target language, the display mode (bilingual or translation only) and any site rules or exclusions in effect.
3. Translate the page. For each state label and each edge label, record whether it was translated. Note labels the extension skips on its own rules, such as identifier-like text (`prefill-1`).
4. Check that the diagram lays itself out again without overlaps, then pan, zoom with Ctrl+wheel or the controls, use fit-view, and switch Light and Dark; record whether the translations stay.
5. Repeat in the other display mode, then compare with the Mermaid page from the issue in the same browser.

Compatibility holds only if both node and edge labels translate. Record the result
in the issue.

## Integration recommendation

The browser check shows that measured HTML labels with Dagre survive longer and
bilingual text: one layout per change, no overlap or clipping, edges still on
their nodes, and translated text kept through viewing and theme changes. Whether
the extension translates these labels is not yet recorded.

- Keep Mermaid as preview's diagram renderer, and do not integrate this renderer until the extension experiment translates both node and edge labels.
- If it does, add an opt-in fenced block in this JSON model, rendered only on pages that use it, rather than converting Mermaid: the model is not Mermaid syntax. Keep what the evidence supports: HTML labels, layout from measured sizes, CSS-only theme changes, and a canvas that grows with the layout inside the page flow.
- React Flow supplies pan, zoom, the controls and the edge label layer; measurement, layout and routing are this prototype's code. It needed workarounds: read-only nodes get no pointer events, edges need hidden handles, its UMD build needs a JSX runtime shim, and its fit-view ignores edge labels. Before integrating, compare it with a renderer without React (Dagre, HTML labels, an SVG edge layer and a small pan and zoom), which would avoid most of the 400 KB.
- If the extension skips these labels too, HTML labels do not solve the problem: record the failure, keep Mermaid, and investigate the extension's rules on this page before any integration.

## Limitations

- It renders one fixture from a hand-written node/edge model; there is no Mermaid parser.
- The layout follows label sizes, not the window: after resizing the window, use fit-view.
- Desktop only; phone layouts were not checked.
