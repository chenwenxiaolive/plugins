// Keep the original fences available if the library or an individual diagram fails.
(() => {
  const mermaid = window.mermaid;
  if (!mermaid) return;
  const blocks = Array.from(document.querySelectorAll('pre > code.language-mermaid'), (code) => {
    const pre = code.parentElement;
    const wrapper = document.createElement('div');
    wrapper.className = 'mermaid-block';
    const diagram = document.createElement('div');
    diagram.className = 'mermaid-diagram';
    const details = document.createElement('details');
    const summary = document.createElement('summary');
    summary.textContent = 'Diagram source';
    details.append(summary);
    pre.replaceWith(wrapper);
    details.append(pre);
    wrapper.append(diagram, details);
    return { source: code.textContent, diagram, details, rendered: false };
  });
  if (!blocks.length) return;

  let requested = 0;
  let rendering = false;
  let nextId = 0;
  // Serialize theme changes: Mermaid configuration is shared by every render.
  async function renderAll() {
    requested += 1;
    if (rendering) return;
    rendering = true;
    try {
      let completed;
      do {
        completed = requested;
        mermaid.initialize({
          startOnLoad: false,
          securityLevel: 'strict',
          suppressErrorRendering: true,
          theme: document.documentElement.dataset.theme === 'dark' ? 'dark' : 'default',
        });
        for (const block of blocks) {
          try {
            const { svg } = await mermaid.render(`preview-mermaid-${nextId++}`, block.source);
            block.diagram.innerHTML = svg;
            if (!block.rendered) block.details.open = false;
            block.rendered = true;
          } catch {
            const error = document.createElement('p');
            error.className = 'mermaid-error';
            error.textContent = 'Diagram could not be rendered. Check the Mermaid source below.';
            error.setAttribute('role', 'alert');
            block.diagram.replaceChildren(error);
            block.details.open = true;
          }
        }
      } while (completed !== requested);
    } finally {
      rendering = false;
    }
  }

  new MutationObserver(renderAll).observe(document.documentElement, {
    attributes: true, attributeFilter: ['data-theme'],
  });
  renderAll();
})();
