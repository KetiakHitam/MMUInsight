// Theme Management
class ThemeManager {
  constructor() {
    this.THEME_KEY = 'mmuinsight-theme';
    this.DARK_CLASS = 'dark-mode';
    this.init();
  }

  init() {
    // Enable transitions after page load
    document.body.classList.add('loaded');

    // Listen for system preference changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
      if (!localStorage.getItem(this.THEME_KEY)) {
        this.setTheme(e.matches ? 'dark' : 'light');
      }
    });
  }

  setTheme(theme) {
    const root = document.documentElement;
    
    if (theme === 'dark') {
      root.classList.add(this.DARK_CLASS);
      localStorage.setItem(this.THEME_KEY, 'dark');
      this.updateToggleButton('dark');
    } else {
      root.classList.remove(this.DARK_CLASS);
      localStorage.setItem(this.THEME_KEY, 'light');
      this.updateToggleButton('light');
    }
  }

  toggleTheme() {
    const root = document.documentElement;
    const isDark = root.classList.contains(this.DARK_CLASS);
    this.setTheme(isDark ? 'light' : 'dark');
  }

  updateToggleButton(theme) {
    const btn = document.querySelector('[data-theme-toggle]');
    if (!btn) return;

    if (theme === 'dark') {
      // Show sun icon (to switch to light)
      btn.innerHTML = `
        <svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" focusable="false">
          <path fill="currentColor" d="M12 18a6 6 0 1 1 0-12 6 6 0 0 1 0 12Zm0-14a1 1 0 0 1 1 1v1a1 1 0 1 1-2 0V5a1 1 0 0 1 1-1Zm0 16a1 1 0 0 1 1 1v1a1 1 0 1 1-2 0v-1a1 1 0 0 1 1-1Zm8-8a1 1 0 0 1-1 1h-1a1 1 0 1 1 0-2h1a1 1 0 0 1 1 1ZM7 12a1 1 0 0 1-1 1H5a1 1 0 1 1 0-2h1a1 1 0 0 1 1 1Zm10.66-5.66a1 1 0 0 1 0 1.41l-.71.71a1 1 0 1 1-1.41-1.41l.71-.71a1 1 0 0 1 1.41 0ZM8.46 15.54a1 1 0 0 1 0 1.41l-.71.71a1 1 0 1 1-1.41-1.41l.71-.71a1 1 0 0 1 1.41 0Zm9.2 1.41a1 1 0 0 1-1.41 0l-.71-.71a1 1 0 1 1 1.41-1.41l.71.71a1 1 0 0 1 0 1.41ZM8.46 8.46a1 1 0 0 1-1.41 0l-.71-.71a1 1 0 1 1 1.41-1.41l.71.71a1 1 0 0 1 0 1.41Z"/>
        </svg>
      `;
    } else {
      // Show moon icon (to switch to dark)
      btn.innerHTML = `
        <svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" focusable="false">
          <path fill="currentColor" d="M21 14.5A8.5 8.5 0 0 1 9.5 3a1 1 0 0 0-1.14 1.31A7 7 0 1 0 19.7 15.64 1 1 0 0 0 21 14.5Z"/>
        </svg>
      `;
    }
  }
}

// Initialize on DOM ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    window.themeManager = new ThemeManager();
  });
} else {
  window.themeManager = new ThemeManager();
}

// Export for use in other scripts
window.toggleTheme = () => {
  if (window.themeManager) {
    window.themeManager.toggleTheme();
  }
};
