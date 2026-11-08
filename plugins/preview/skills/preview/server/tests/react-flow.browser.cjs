// Run with an existing Playwright installation and a PREVIEW_TEST_TMPDIR outside the checkout.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const net = require('node:net');
const path = require('node:path');
const { spawn, spawnSync } = require('node:child_process');
const { chromium } = require(process.env.PREVIEW_PLAYWRIGHT_MODULE || 'playwright');

// Issue #64's Mermaid fixture: node kinds and state labels, and transitions keyed by edge ID.
const NODES = {
  begin: ['start'],
  Form: ['choice'],
  Prefix: ['state', 'Pass 1 on prompt tokens 1 … P−1'],
  Start: ['state', 'Decode-form on prompt token P\nInject the previous representation\nRead mixed KV; update carry'],
  All: ['state', 'Pass 1 on all prompt tokens 1 … P\nWrite mixed KV\nCarry = final pass-1 representation'],
  Sample: ['state', 'Sample and emit a token'],
  Stop: ['choice'],
  Decode: ['state', 'Decode-form on the emitted token\nUpdate KV and carry'],
  finish: ['end'],
};
const EDGES = {
  'begin-Form': ['begin', 'Form'],
  'Form-Prefix': ['Form', 'Prefix', 'prefill-1'],
  'Form-All': ['Form', 'All', 'prefill-1-nofuse-start'],
  'Prefix-Start': ['Prefix', 'Start', 'Write mixed prefix KV'],
  'Start-Sample': ['Start', 'Sample', 'First token: decode-form logits'],
  'All-Sample': ['All', 'Sample', 'First token: pass-1 logits'],
  'Sample-Stop': ['Sample', 'Stop'],
  'Stop-finish': ['Stop', 'finish', 'EOS / stop / length limit'],
  'Stop-Decode': ['Stop', 'Decode', 'Continue'],
  'Decode-Sample': ['Decode', 'Sample', 'Next-token logits'],
};
const TOLERANCE = 1.5;

// Geometry in flow coordinates, read from the rendered DOM.
function readDiagram() {
  const root = document.querySelector('.react-flow').getBoundingClientRect();
  const [, tx, ty, k] = document.querySelector('.react-flow__viewport').style.transform
    .match(/translate\(([-\d.]+)px, ([-\d.]+)px\) scale\(([-\d.]+)\)/).map(Number);
  const box = (rect) => ({
    x: (rect.left - root.left - tx) / k, y: (rect.top - root.top - ty) / k, width: rect.width / k, height: rect.height / k,
  });
  const overflow = (element) => {
    const outer = element.getBoundingClientRect();
    const walker = document.createTreeWalker(element, NodeFilter.SHOW_TEXT);
    const range = document.createRange();
    while (walker.nextNode()) {
      range.selectNodeContents(walker.currentNode);
      for (const rect of range.getClientRects()) {
        if (rect.left < outer.left - 1 || rect.right > outer.right + 1
          || rect.top < outer.top - 1 || rect.bottom > outer.bottom + 1) return true;
      }
    }
    return element.scrollWidth > element.clientWidth + 1 || element.scrollHeight > element.clientHeight + 1;
  };
  const nodes = Object.fromEntries(Array.from(document.querySelectorAll('.node'), (element) => [
    element.dataset.nodeId, {
      kind: ['start', 'end', 'choice', 'state'].find((kind) => element.classList.contains(kind)),
      lines: Array.from(element.querySelectorAll('p'), (line) => line.textContent),
      box: box(element.getBoundingClientRect()),
      overflow: overflow(element),
      userSelect: getComputedStyle(element).userSelect,
      background: getComputedStyle(element).backgroundColor,
    }]));
  const labels = Object.fromEntries(Array.from(document.querySelectorAll('.edge-label'), (element) => [
    element.dataset.edgeId, {
      text: element.textContent,
      source: element.dataset.source,
      target: element.dataset.target,
      box: box(element.getBoundingClientRect()),
      overflow: overflow(element),
      userSelect: getComputedStyle(element).userSelect,
    }]));
  const edges = Object.fromEntries(Array.from(document.querySelectorAll('.react-flow__edge'), (element) => {
    const route = element.querySelector('path.react-flow__edge-path');
    const numbers = route.getAttribute('d').match(/-?[\d.]+(?:e-?\d+)?/g).map(Number);
    const samples = Array.from({ length: 201 }, (_, index) =>
      route.getPointAtLength(route.getTotalLength() * index / 200)).map(({ x, y }) => ({ x, y }));
    return [element.dataset.id, { start: { x: numbers[0], y: numbers[1] }, end: { x: numbers.at(-2), y: numbers.at(-1) }, samples }];
  }));
  const textOutsideSVG = [];
  const walker = document.createTreeWalker(document.querySelector('.react-flow__viewport'), NodeFilter.SHOW_TEXT);
  while (walker.nextNode()) {
    if (walker.currentNode.nodeValue.trim()) textOutsideSVG.push(!walker.currentNode.parentElement.closest('svg'));
  }
  return {
    nodes, labels, edges, textOutsideSVG,
    svgText: document.querySelectorAll('.react-flow svg text, .react-flow svg foreignObject').length,
    layouts: Number(document.querySelector('.flow').dataset.layouts),
    viewport: { tx, ty, k },
    canvas: { width: root.width / k, height: root.height / k, x: -tx / k, y: -ty / k },
  };
}

function onShape(node, point) {
  const { x, y, width, height } = node.box;
  const dx = point.x - (x + width / 2);
  const dy = point.y - (y + height / 2);
  if (node.kind === 'start' || node.kind === 'end') return Math.abs(Math.hypot(dx, dy) - width / 2) <= TOLERANCE;
  if (node.kind === 'choice') return Math.abs((Math.abs(dx) + Math.abs(dy)) - width / 2) <= TOLERANCE;
  const outside = Math.max(Math.abs(dx) - width / 2, Math.abs(dy) - height / 2);
  return Math.abs(outside) <= TOLERANCE;
}

function overlaps(a, b) {
  return Math.min(a.x + a.width, b.x + b.width) - Math.max(a.x, b.x) > 0.5
    && Math.min(a.y + a.height, b.y + b.height) - Math.max(a.y, b.y) > 0.5;
}

function inside(inner, outer) {
  return inner.x >= outer.x - TOLERANCE && inner.y >= outer.y - TOLERANCE
    && inner.x + inner.width <= outer.x + outer.width + TOLERANCE
    && inner.y + inner.height <= outer.y + outer.height + TOLERANCE;
}

// The fixture's graph, readable labels, no overlap or clipping, and edges attached to their own nodes and labels.
function checkDiagram(diagram, stage) {
  const at = (message) => `${stage}: ${message}`;
  assert.deepEqual(Object.keys(diagram.nodes).sort(), Object.keys(NODES).sort(), at('nodes'));
  assert.deepEqual(Object.keys(diagram.edges).sort(), Object.keys(EDGES).sort(), at('edges'));
  assert.deepEqual(Object.keys(diagram.labels).sort(),
    Object.keys(EDGES).filter((id) => EDGES[id][2]).sort(), at('edge labels'));
  for (const [id, [kind]] of Object.entries(NODES)) assert.equal(diagram.nodes[id].kind, kind, at(`${id} kind`));
  assert.ok(diagram.textOutsideSVG.length > 0 && diagram.textOutsideSVG.every(Boolean), at('text outside SVG'));
  assert.equal(diagram.svgText, 0, at('SVG text'));
  const obstacles = [
    ...Object.entries(diagram.nodes).map(([id, node]) => [`node ${id}`, node]),
    ...Object.entries(diagram.labels).map(([id, label]) => [`label ${id}`, label]),
  ];
  for (const [name, item] of obstacles.filter(([, item]) => item.kind === undefined || item.kind === 'state')) {
    assert.equal(item.overflow, false, at(`${name} is clipped or overflows`));
    assert.equal(item.userSelect, 'text', at(`${name} is not selectable`));
  }
  for (let i = 0; i < obstacles.length; i += 1) {
    for (let j = i + 1; j < obstacles.length; j += 1) {
      assert.ok(!overlaps(obstacles[i][1].box, obstacles[j][1].box), at(`${obstacles[i][0]} overlaps ${obstacles[j][0]}`));
    }
  }
  for (const [id, [source, target]] of Object.entries(EDGES)) {
    const edge = diagram.edges[id];
    assert.ok(onShape(diagram.nodes[source], edge.start), at(`${id} starts off ${source}: ${JSON.stringify(edge.start)}`));
    assert.ok(onShape(diagram.nodes[target], edge.end), at(`${id} ends off ${target}: ${JSON.stringify(edge.end)}`));
    const label = diagram.labels[id];
    if (!label) continue;
    assert.deepEqual([label.source, label.target], [source, target], at(`${id} label endpoints`));
    assert.ok(edge.samples.some((point) => inside({ ...point, width: 0, height: 0 }, label.box)),
      at(`${id} label is off its edge`));
  }
}

function labelTexts(diagram) {
  return {
    nodes: Object.fromEntries(Object.entries(diagram.nodes).map(([id, node]) => [id, node.lines])),
    labels: Object.fromEntries(Object.entries(diagram.labels).map(([id, label]) => [id, label.text])),
  };
}

// Change label text in the DOM outside React, as a translation extension does: replace it with a longer
// translation, or restore it and add a translation below it.
function translate(mode) {
  const suffix = ' – längere übersetzte Beschriftung';
  const targets = document.querySelectorAll('.node.state p, .edge-label');
  for (const element of targets) {
    if (mode === 'longer') {
      element.firstChild.nodeValue += suffix;
    } else {
      element.firstChild.nodeValue = element.firstChild.nodeValue.replace(suffix, '');
      const translation = document.createElement('font');
      translation.className = 'simulated-translation';
      translation.append(document.createElement('br'), '双语译文：' + '较长的中文翻译文本'.repeat(2));
      element.append(translation);
    }
  }
  return targets.length;
}

async function main() {
  const scratch = fs.mkdtempSync(path.join(process.env.PREVIEW_TEST_TMPDIR, 'react-flow-'));
  const socket = net.createServer();
  await new Promise((resolve) => socket.listen(0, '127.0.0.1', resolve));
  const port = socket.address().port;
  await new Promise((resolve) => socket.close(resolve));
  const base = `http://127.0.0.1:${port}`;
  const log = fs.openSync(path.join(scratch, 'server.log'), 'w');
  const server = spawn('python3', ['-B', path.join(__dirname, '../server.py'),
    '--directory', path.join(__dirname, '../prototypes/react-flow'), '--bind', '127.0.0.1', '--port', String(port)],
  { stdio: ['ignore', log, log] });
  const exited = new Promise((resolve) => server.once('exit', resolve));
  let browser;
  let page;
  try {
    for (let attempt = 0; ; attempt += 1) {
      try { if ((await fetch(base)).ok) break; } catch {}
      if (attempt > 50 || server.exitCode !== null) throw new Error('Preview server did not start');
      await new Promise((resolve) => setTimeout(resolve, 100));
    }
    browser = await chromium.launch({ headless: true, args: ['--no-sandbox', '--disable-gpu'] });
    const context = await browser.newContext({ viewport: { width: 1440, height: 900 }, colorScheme: 'light' });
    const external = [];
    const errors = [];
    await context.route('**/*', (route) => {
      if (new URL(route.request().url()).origin !== base) {
        external.push(route.request().url());
        return route.abort();
      }
      return route.continue();
    });
    page = await context.newPage();
    page.on('pageerror', (error) => errors.push(error.message));
    page.on('console', (message) => {
      if (['error', 'warning'].includes(message.type())) errors.push(`${message.type()}: ${message.text()}`);
    });
    const diagram = () => page.evaluate(readDiagram);
    const settle = async (layouts) => {
      await page.waitForFunction((expected) => {
        const flow = document.querySelector('.flow:not(.pending)');
        return flow && Number(flow.dataset.layouts) === expected;
      }, layouts);
      await page.waitForTimeout(600);
      const result = await diagram();
      assert.equal(result.layouts, layouts, 'layout repeated without a size change');
      return result;
    };
    // The default view shows the whole layout at natural size inside a canvas as tall as the layout.
    const shownInFull = (result, stage) => {
      assert.equal(result.viewport.k, 1, `${stage}: text is scaled`);
      for (const [id, item] of [...Object.entries(result.nodes), ...Object.entries(result.labels)]) {
        assert.ok(inside(item.box, result.canvas), `${stage}: ${id} is outside the canvas`);
      }
    };
    const theme = async (value) => {
      await page.selectOption('#theme-select', value);
      await page.waitForFunction((expected) => document.documentElement.dataset.theme === expected, value);
    };
    const shot = (name) => page.screenshot({ path: path.join(scratch, `${name}.png`), fullPage: true });

    await page.goto(base + '/index.html');
    const initial = await settle(1);
    checkDiagram(initial, 'initial');
    shownInFull(initial, 'initial');
    for (const [id, [, label]] of Object.entries(NODES)) {
      if (label) assert.deepEqual(initial.nodes[id].lines, label.split('\n'), `${id} label`);
    }
    for (const [id, [, , label]] of Object.entries(EDGES)) {
      if (label) assert.equal(initial.labels[id].text, label, `${id} label`);
    }
    await shot('light-before');
    await theme('dark');
    const dark = await diagram();
    assert.notEqual(dark.nodes.Sample.background, initial.nodes.Sample.background, 'dark theme not applied');
    assert.equal(dark.layouts, 1, 'theme change caused a layout');
    await shot('dark-before');
    await theme('light');

    // Dragging across a label selects its text instead of panning the view.
    for (const selector of ['[data-node-id="Sample"] p', '[data-edge-id="Stop-Decode"]']) {
      const rect = await page.locator(selector).evaluate((element) => {
        const range = document.createRange();
        range.selectNodeContents(element);
        const { left, right, top, height } = range.getBoundingClientRect();
        return { left, right, y: top + height / 2 };
      });
      await page.mouse.move(rect.left + 1, rect.y);
      await page.mouse.down();
      await page.mouse.move(rect.right - 1, rect.y, { steps: 8 });
      await page.mouse.up();
      const selected = await page.evaluate(() => window.getSelection().toString());
      assert.equal(selected.trim(), (await page.locator(selector).textContent()).trim(), `${selector} selection`);
      assert.deepEqual((await diagram()).viewport, initial.viewport, `${selector} selection moved the view`);
      await page.evaluate(() => window.getSelection().removeAllRanges());
    }

    assert.equal(await page.evaluate(translate, 'longer'), 18);
    const longer = await settle(2);
    checkDiagram(longer, 'longer');
    shownInFull(longer, 'longer');
    assert.ok(longer.nodes.Start.box.height > initial.nodes.Start.box.height, 'longer node labels did not wrap');
    assert.ok(longer.labels['Start-Sample'].box.height > initial.labels['Start-Sample'].box.height,
      'longer edge labels did not wrap');

    await page.evaluate(translate, 'bilingual');
    const bilingual = await settle(3);
    checkDiagram(bilingual, 'bilingual');
    shownInFull(bilingual, 'bilingual');
    assert.ok(bilingual.nodes.Start.box.height > initial.nodes.Start.box.height, 'bilingual node labels missing');
    assert.ok(bilingual.canvas.height > initial.canvas.height, 'canvas did not grow with the layout');
    const translated = labelTexts(bilingual);
    assert.match(translated.nodes.Sample[0], /^Sample and emit a token双语译文/);
    assert.match(translated.labels['Stop-Decode'], /^Continue双语译文/);
    await shot('light-after');
    await theme('dark');
    await shot('dark-after');

    // The wheel scrolls the page; the diagram keeps its view, layout and text.
    const canvasTop = (await page.locator('.react-flow').boundingBox()).y;
    await page.mouse.move(720, 450);
    await page.mouse.wheel(0, 300);
    await page.waitForFunction(() => window.scrollY > 0);
    const scrolled = await diagram();
    assert.deepEqual(scrolled.viewport, bilingual.viewport, 'the wheel moved the diagram');
    assert.deepEqual(labelTexts(scrolled), translated, 'scrolling lost translated text');
    await page.evaluate(() => window.scrollTo(0, 0));
    await page.waitForFunction((top) => document.querySelector('.react-flow').getBoundingClientRect().y === top, canvasTop);

    // Viewing changes move or scale the diagram without another layout or any text loss.
    const viewed = ['wheel scroll'];
    const expectView = async (name, action, check) => {
      const before = await diagram();
      const previous = await page.locator('.react-flow__viewport').evaluate((element) => element.style.transform);
      await action();
      await page.waitForFunction((value) =>
        document.querySelector('.react-flow__viewport').style.transform !== value, previous);
      await page.waitForTimeout(400);
      const after = await diagram();
      assert.equal(after.layouts, 3, `${name} caused a layout`);
      assert.deepEqual(labelTexts(after), translated, `${name} lost translated text`);
      checkDiagram(after, name);
      for (const id of Object.keys(NODES)) {
        assert.ok(Math.abs(after.nodes[id].box.x - before.nodes[id].box.x) < 0.5
          && Math.abs(after.nodes[id].box.y - before.nodes[id].box.y) < 0.5, `${name} moved node ${id}`);
      }
      check(before.viewport, after.viewport, after);
      viewed.push(name);
    };
    const canvas = await page.locator('.react-flow').boundingBox();
    await expectView('pan', async () => {
      await page.mouse.move(canvas.x + 30, canvas.y + 30);
      await page.mouse.down();
      await page.mouse.move(canvas.x + 150, canvas.y + 110, { steps: 8 });
      await page.mouse.up();
    }, (before, after) => assert.ok(Math.abs(after.tx - before.tx - 120) < 2 && Math.abs(after.ty - before.ty - 80) < 2));
    await expectView('ctrl+wheel zoom', async () => {
      await page.mouse.move(canvas.x + canvas.width / 2, canvas.y + 300);
      await page.keyboard.down('Control');
      await page.mouse.wheel(0, -200);
      await page.keyboard.up('Control');
    }, (before, after) => assert.ok(after.k > before.k));
    await expectView('zoom out', () => page.click('.react-flow__controls-zoomout'),
      (before, after) => assert.ok(after.k < before.k));
    await expectView('fit view', () => page.click('.react-flow__controls-fitview'), (before, after, result) => {
      assert.deepEqual(after, bilingual.viewport);
      shownInFull(result, 'fit view');
    });
    await theme('light');
    const final = await diagram();
    assert.equal(final.layouts, 3, 'theme change caused a layout');
    assert.deepEqual(labelTexts(final), translated, 'theme change lost translated text');

    // Invalid input is reported at the model boundary instead of rendering a partial diagram.
    const invalid = await context.newPage();
    invalid.on('pageerror', (error) => errors.push(error.message));
    await invalid.route('**/infg-statechart.json', (route) => route.fulfill({
      contentType: 'application/json',
      body: JSON.stringify({ nodes: [{ id: 'a', kind: 'start' }], edges: [{ id: 'a-b', source: 'a', target: 'b' }] }),
    }));
    await invalid.goto(base + '/index.html');
    assert.match(await invalid.locator('[role="alert"]').textContent(), /Edge a-b must connect two existing nodes/);
    assert.equal(await invalid.locator('.react-flow').count(), 0);

    assert.deepEqual(external, []);
    assert.deepEqual(errors, []);
    console.log(JSON.stringify({
      status: 'passed', scratch, externalRequests: external.length, layouts: final.layouts, viewed,
      screenshots: ['light-before', 'dark-before', 'light-after', 'dark-after'].map((name) => `${name}.png`),
      browser: browser.version(), commit: spawnSync('git', ['rev-parse', 'HEAD'], { encoding: 'utf8' }).stdout.trim(),
    }));
  } catch (error) {
    if (page) await page.screenshot({ path: path.join(scratch, 'failure.png') }).catch(() => {});
    throw error;
  } finally {
    if (browser) await browser.close();
    server.kill('SIGTERM');
    await exited;
    fs.closeSync(log);
  }
}

main().catch((error) => { console.error(error); process.exitCode = 1; });
