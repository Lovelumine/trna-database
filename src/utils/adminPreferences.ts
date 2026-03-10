import { computed, ref, watch } from 'vue';

export type AdminLocale = 'zh-CN' | 'en';
export type AdminThemeMode = 'system' | 'light' | 'dark';
type ResolvedTheme = 'light' | 'dark';

const LOCALE_KEY = 'ensure-admin-locale';
const THEME_KEY = 'theme-mode';
const LEGACY_THEME_KEY = 'ensure-admin-theme';

const media = typeof window !== 'undefined' ? window.matchMedia('(prefers-color-scheme: dark)') : null;

function readLocale(): AdminLocale {
  if (typeof window === 'undefined') return 'zh-CN';
  const stored = String(window.localStorage.getItem(LOCALE_KEY) || '').trim();
  return stored === 'en' ? 'en' : 'zh-CN';
}

function readThemeMode(): AdminThemeMode {
  if (typeof window === 'undefined') return 'system';
  const stored = String(window.localStorage.getItem(THEME_KEY) || '').trim();
  if (stored === 'light' || stored === 'dark' || stored === 'system') {
    return stored;
  }
  const legacy = String(window.localStorage.getItem(LEGACY_THEME_KEY) || '').trim();
  if (legacy === 'light' || legacy === 'dark') {
    return legacy;
  }
  return 'system';
}

const locale = ref<AdminLocale>(readLocale());
const themeMode = ref<AdminThemeMode>(readThemeMode());

function resolveTheme(mode: AdminThemeMode): ResolvedTheme {
  const prefersDark = Boolean(media?.matches);
  return mode === 'system' ? (prefersDark ? 'dark' : 'light') : mode;
}

function applyTheme(mode: AdminThemeMode) {
  if (typeof document === 'undefined') return;
  const resolved = resolveTheme(mode);
  document.documentElement.setAttribute('data-admin-theme', resolved);
  document.documentElement.setAttribute('data-admin-theme-mode', mode);
  document.documentElement.style.colorScheme = resolved;
}

function applyLocale(value: AdminLocale) {
  if (typeof document === 'undefined') return;
  document.documentElement.setAttribute('lang', value === 'zh-CN' ? 'zh-CN' : 'en');
}

watch(
  themeMode,
  (value) => {
    if (typeof window !== 'undefined') {
      window.localStorage.setItem(THEME_KEY, value);
      window.localStorage.removeItem(LEGACY_THEME_KEY);
    }
    applyTheme(value);
  },
  { immediate: true }
);

watch(
  locale,
  (value) => {
    if (typeof window !== 'undefined') {
      window.localStorage.setItem(LOCALE_KEY, value);
    }
    applyLocale(value);
  },
  { immediate: true }
);

export function initAdminPreferences() {
  applyTheme(themeMode.value);
  applyLocale(locale.value);
  const handler = () => {
    if (themeMode.value === 'system') {
      applyTheme('system');
    }
  };
  if (media) {
    if ('addEventListener' in media) {
      media.addEventListener('change', handler);
    } else if ('addListener' in media) {
      media.addListener(handler);
    }
  }
}

export function useAdminPreferences() {
  function setLocale(value: AdminLocale) {
    locale.value = value;
  }

  function setThemeMode(value: AdminThemeMode) {
    themeMode.value = value;
  }

  function toggleTheme() {
    if (themeMode.value === 'system') {
      themeMode.value = 'dark';
      return;
    }
    if (themeMode.value === 'dark') {
      themeMode.value = 'light';
      return;
    }
    themeMode.value = 'system';
  }

  return {
    locale,
    themeMode,
    resolvedTheme: computed(() => resolveTheme(themeMode.value)),
    isDark: computed(() => resolveTheme(themeMode.value) === 'dark'),
    setLocale,
    setThemeMode,
    toggleTheme
  };
}
