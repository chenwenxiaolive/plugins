// Exercise theme state across page loads using the browser APIs it consumes.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');
const vm = require('node:vm');

const source = fs.readFileSync(path.join(__dirname, '../assets/theme.js'), 'utf8');

function loadPage({ dark = false, saved = null, blocked = false } = {}) {
  const values = new Map(saved === null ? [] : [['preview-theme', saved]]);
  const documentEvents = {};
  const selectEvents = {};
  const mediaEvents = {};
  const root = { dataset: {} };
  const select = {
    value: 'system',
    hidden: true,
    addEventListener: (name, callback) => { selectEvents[name] = callback; },
  };
  const media = {
    matches: dark,
    addEventListener: (name, callback) => { mediaEvents[name] = callback; },
  };
  vm.runInNewContext(source, {
    document: {
      documentElement: root,
      getElementById: (id) => id === 'theme-select' ? select : null,
      addEventListener: (name, callback) => { documentEvents[name] = callback; },
    },
    window: {
      matchMedia: (query) => {
        assert.equal(query, '(prefers-color-scheme: dark)');
        return media;
      },
      get localStorage() {
        if (blocked) throw new Error('Storage is unavailable');
        return {
          getItem: (key) => values.get(key) ?? null,
          setItem: (key, value) => values.set(key, value),
          removeItem: (key) => values.delete(key),
        };
      },
    },
  });
  const initialTheme = root.dataset.theme;
  documentEvents.DOMContentLoaded();
  return {
    root, select, values, initialTheme,
    choose(value) { select.value = value; selectEvents.change(); },
    system(dark) { media.matches = dark; mediaEvents.change(media); },
  };
}

test('system preference applies before page content and follows changes', () => {
  for (const dark of [false, true]) {
    const page = loadPage({ dark });
    assert.equal(page.initialTheme, dark ? 'dark' : 'light');
    assert.equal(page.select.value, 'system');
    page.system(!dark);
    assert.equal(page.root.dataset.theme, dark ? 'light' : 'dark');
    assert.equal(page.values.size, 0);
  }
});

test('saved choices override the system and survive another page load', () => {
  for (const saved of ['light', 'dark']) {
    const page = loadPage({ dark: saved === 'light', saved });
    assert.equal(page.initialTheme, saved);
    assert.equal(page.select.value, saved);
    page.system(saved === 'light');
    assert.equal(page.root.dataset.theme, saved);
    const next = saved === 'light' ? 'dark' : 'light';
    page.choose(next);
    assert.equal(page.root.dataset.theme, next);
    assert.equal(page.values.get('preview-theme'), next);
    assert.equal(loadPage({ saved: page.values.get('preview-theme') }).initialTheme, next);
  }
});

test('returning to System clears the override and resumes live changes', () => {
  const page = loadPage({ dark: true, saved: 'light' });
  page.choose('system');
  assert.equal(page.root.dataset.theme, 'dark');
  assert.equal(page.values.has('preview-theme'), false);
  page.system(false);
  assert.equal(page.root.dataset.theme, 'light');
});

test('unavailable storage still permits manual selection', () => {
  const page = loadPage({ dark: true, blocked: true });
  assert.equal(page.initialTheme, 'dark');
  page.choose('light');
  assert.equal(page.root.dataset.theme, 'light');
  page.system(true);
  assert.equal(page.root.dataset.theme, 'light');
  page.choose('system');
  assert.equal(page.root.dataset.theme, 'dark');
});

test('an unknown saved preference falls back to System', () => {
  const page = loadPage({ dark: true, saved: 'unexpected' });
  assert.equal(page.initialTheme, 'dark');
  assert.equal(page.select.value, 'system');
});
