// Render standard Markdown and tables without depending on a browser or CDN.
const fs = require('node:fs');
const MarkdownIt = require('./assets/markdown-it.min.cjs');
const markdown = new MarkdownIt({ html: false, linkify: true });
const headings = new Map();
markdown.renderer.rules.heading_open = (tokens, index, options, env, self) => {
  const title = tokens[index + 1].content;
  const base = title.toLowerCase().replace(/[^\p{L}\p{N}\s_-]/gu, '').trim().replace(/\s+/g, '-') || 'section';
  const count = headings.get(base) || 0;
  headings.set(base, count + 1);
  tokens[index].attrSet('id', count ? `${base}-${count}` : base);
  return self.renderToken(tokens, index, options);
};
process.stdout.write(markdown.render(fs.readFileSync(0, 'utf8')));
