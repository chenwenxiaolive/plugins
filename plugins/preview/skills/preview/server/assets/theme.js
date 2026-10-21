(() => {
  const storageKey = 'preview-theme';
  const system = window.matchMedia('(prefers-color-scheme: dark)');
  let preference = 'system';
  try {
    const saved = window.localStorage.getItem(storageKey);
    if (saved === 'light' || saved === 'dark') preference = saved;
  } catch {
    // Storage may be disabled; theme selection still works on this page.
  }

  function applyTheme() {
    document.documentElement.dataset.theme = preference === 'system'
      ? (system.matches ? 'dark' : 'light')
      : preference;
  }

  // This script runs before the stylesheet to avoid flashing the wrong theme.
  applyTheme();
  system.addEventListener('change', applyTheme);
  document.addEventListener('DOMContentLoaded', () => {
    const select = document.getElementById('theme-select');
    select.value = preference;
    select.addEventListener('change', () => {
      preference = select.value;
      applyTheme();
      try {
        if (preference === 'system') window.localStorage.removeItem(storageKey);
        else window.localStorage.setItem(storageKey, preference);
      } catch {
        // Keep the selected theme even when the browser cannot save it.
      }
    });
  });
})();
