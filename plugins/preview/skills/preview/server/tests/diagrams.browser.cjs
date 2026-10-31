// Run with an existing Playwright installation and a PREVIEW_TEST_TMPDIR outside the checkout.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const net = require('node:net');
const path = require('node:path');
const { spawn, spawnSync } = require('node:child_process');
const { chromium } = require(process.env.PREVIEW_PLAYWRIGHT_MODULE || 'playwright');

async function main() {
  const scratch = fs.mkdtempSync(path.join(process.env.PREVIEW_TEST_TMPDIR, 'browser-'));
  const root = path.join(scratch, 'files');
  fs.mkdirSync(root);
  const source = '# Mermaid preview\n\n' + [
    '```mermaid\nflowchart LR\n  A["Controller 中文"] --> B[Worker]\n```',
    '```mermaid\nthis is not a diagram\n```',
    '```mermaid\nsequenceDiagram\n  Browser->>Controller: Submit\n  Controller-->>Browser: Result\n```',
    '```python\nprint("ordinary code")\n```',
    '```mermaid\nflowchart LR\n  A["<img src=x onerror=alert(1)>"] --> B[Safe]\n  click B "javascript:alert(1)"\n```',
  ].join('\n\n');
  fs.writeFileSync(path.join(root, 'diagrams.md'), source);
  if (process.env.PREVIEW_EXAMPLE_MARKDOWN) {
    fs.copyFileSync(process.env.PREVIEW_EXAMPLE_MARKDOWN, path.join(root, 'example.md'));
  }
  const socket = net.createServer();
  await new Promise((resolve) => socket.listen(0, '127.0.0.1', resolve));
  const port = socket.address().port;
  await new Promise((resolve) => socket.close(resolve));
  const base = `http://127.0.0.1:${port}`;
  const log = fs.openSync(path.join(scratch, 'server.log'), 'w');
  const server = spawn('python3', ['-B', path.join(__dirname, '../server.py'),
    '--directory', root, '--bind', '127.0.0.1', '--port', String(port)], { stdio: ['ignore', log, log] });
  const exited = new Promise((resolve) => server.once('exit', resolve));
  let browser;
  try {
    for (let attempt = 0; ; attempt += 1) {
      try { if ((await fetch(base)).ok) break; } catch {}
      if (attempt > 50 || server.exitCode !== null) throw new Error('Preview server did not start');
      await new Promise((resolve) => setTimeout(resolve, 100));
    }
    browser = await chromium.launch({ headless: true, args: ['--no-sandbox', '--disable-gpu'] });
    const page = await browser.newPage({ colorScheme: 'light' });
    const external = [];
    const errors = [];
    const dialogs = [];
    page.on('pageerror', (error) => errors.push(error.message));
    page.on('dialog', async (dialog) => { dialogs.push(dialog.message()); await dialog.dismiss(); });
    await page.route('**/*', (route) => {
      if (new URL(route.request().url()).origin !== base) {
        external.push(route.request().url());
        return route.abort();
      }
      return route.continue();
    });
    await page.goto(base + '/diagrams.md');
    const settled = () => page.waitForFunction(() =>
      document.querySelectorAll('.mermaid-diagram svg').length === 3 &&
      document.querySelectorAll('.mermaid-error').length === 1);
    await settled();
    assert.equal(await page.locator('.mermaid-block').count(), 4);
    assert.equal(await page.locator('.mermaid-block').nth(1).locator('details').getAttribute('open'), '');
    assert.match(await page.locator('code.language-python').textContent(), /ordinary code/);
    assert.match(await page.locator('.mermaid-diagram').first().textContent(), /Controller 中文/);
    assert.equal(await page.locator('.mermaid-diagram img, .mermaid-diagram a[href^="javascript:"]').count(), 0);
    await page.locator('.mermaid-block summary').first().click();
    assert.match(await page.locator('.mermaid-block pre').first().textContent(), /flowchart LR/);
    const color = () => page.locator('.mermaid-diagram svg .node rect').first().evaluate(
      (element) => getComputedStyle(element).fill);
    const light = await color();
    const svgID = () => page.locator('.mermaid-diagram svg').first().getAttribute('id');
    const lightID = await svgID();
    await page.selectOption('#theme-select', 'dark');
    await page.waitForFunction((id) => document.querySelector('.mermaid-diagram svg')?.id !== id, lightID);
    await settled();
    assert.notEqual(await color(), light);
    assert.equal(await page.locator('.mermaid-block details').first().getAttribute('open'), '');
    await page.screenshot({ path: path.join(scratch, 'dark.png'), fullPage: true });
    await page.selectOption('#theme-select', 'system');
    await page.emulateMedia({ colorScheme: 'light' });
    await page.waitForFunction((expected) =>
      getComputedStyle(document.querySelector('.mermaid-diagram svg .node rect')).fill === expected, light);
    await settled();
    await page.screenshot({ path: path.join(scratch, 'light.png'), fullPage: true });
    assert.equal(await (await page.request.get(base + '/diagrams.md?raw=1')).text(), source);
    assert.equal(await (await page.request.get(base + '/diagrams.md?download=1')).text(), source);
    const noJS = await browser.newPage({ javaScriptEnabled: false });
    await noJS.goto(base + '/diagrams.md');
    assert.equal(await noJS.locator('pre > code.language-mermaid').count(), 4);
    await noJS.close();
    if (process.env.PREVIEW_EXAMPLE_MARKDOWN) {
      await page.goto(base + '/example.md');
      await page.waitForFunction(() => document.querySelectorAll('.mermaid-diagram svg').length === 3);
      assert.equal(await page.locator('.mermaid-error').count(), 0);
      await page.screenshot({ path: path.join(scratch, 'example.png'), fullPage: true });
    }
    assert.deepEqual(external, []);
    assert.deepEqual(errors, []);
    assert.deepEqual(dialogs, []);
    console.log(JSON.stringify({ status: 'passed', scratch, externalRequests: external.length,
      browser: browser.version(), commit: spawnSync('git', ['rev-parse', 'HEAD'], { encoding: 'utf8' }).stdout.trim() }));
  } finally {
    if (browser) await browser.close();
    server.kill('SIGTERM');
    await exited;
    fs.closeSync(log);
  }
}

main().catch((error) => { console.error(error); process.exitCode = 1; });
