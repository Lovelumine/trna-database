export type ThemeMode = 'system' | 'light' | 'dark';

const STORAGE_KEY = 'theme-mode';
const media = window.matchMedia('(prefers-color-scheme: dark)');

export const getThemeMode = (): ThemeMode => {
  const stored = window.localStorage.getItem(STORAGE_KEY);
  if (stored === 'light' || stored === 'dark' || stored === 'system') {
    return stored;
  }
  return 'system';
};

export const applyThemeMode = (mode: ThemeMode) => {
  const root = document.documentElement;
  const isDark = mode === 'dark' || (mode === 'system' && media.matches);
  root.classList.toggle('dark', isDark);
  if (mode === 'system') {
    root.removeAttribute('data-theme');
    root.style.colorScheme = media.matches ? 'dark' : 'light';
    return;
  }
  root.setAttribute('data-theme', mode);
  root.style.colorScheme = mode;
};

export const setThemeMode = (mode: ThemeMode) => {
  window.localStorage.setItem(STORAGE_KEY, mode);
  applyThemeMode(mode);
};

export const nextThemeMode = (mode: ThemeMode): ThemeMode => {
  if (mode === 'system') return 'dark';
  if (mode === 'dark') return 'light';
  return 'system';
};

export const initTheme = () => {
  const mode = getThemeMode();
  applyThemeMode(mode);
  const handler = () => {
    if (getThemeMode() === 'system') {
      applyThemeMode('system');
    }
  };
  if ('addEventListener' in media) {
    media.addEventListener('change', handler);
  } else if ('addListener' in media) {
    media.addListener(handler);
  }
};
