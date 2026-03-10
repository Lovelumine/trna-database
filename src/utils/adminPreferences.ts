import { computed, ref, watch } from 'vue';

export type AdminLocale = 'zh-CN' | 'en';
export type AdminTheme = 'light' | 'dark';

const LOCALE_KEY = 'ensure-admin-locale';
const THEME_KEY = 'ensure-admin-theme';

function readLocale(): AdminLocale {
  if (typeof window === 'undefined') return 'zh-CN';
  const stored = String(window.localStorage.getItem(LOCALE_KEY) || '').trim();
  return stored === 'en' ? 'en' : 'zh-CN';
}

function readTheme(): AdminTheme {
  if (typeof window === 'undefined') return 'light';
  const stored = String(window.localStorage.getItem(THEME_KEY) || '').trim();
  return stored === 'dark' ? 'dark' : 'light';
}

const locale = ref<AdminLocale>(readLocale());
const theme = ref<AdminTheme>(readTheme());

function applyTheme(value: AdminTheme) {
  if (typeof document === 'undefined') return;
  document.documentElement.setAttribute('data-admin-theme', value);
  document.documentElement.style.colorScheme = value;
}

function applyLocale(value: AdminLocale) {
  if (typeof document === 'undefined') return;
  document.documentElement.setAttribute('lang', value === 'zh-CN' ? 'zh-CN' : 'en');
}

watch(
  theme,
  (value) => {
    if (typeof window !== 'undefined') {
      window.localStorage.setItem(THEME_KEY, value);
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
  applyTheme(theme.value);
  applyLocale(locale.value);
}

export function useAdminPreferences() {
  function setLocale(value: AdminLocale) {
    locale.value = value;
  }

  function toggleTheme() {
    theme.value = theme.value === 'dark' ? 'light' : 'dark';
  }

  return {
    locale,
    theme,
    isDark: computed(() => theme.value === 'dark'),
    setLocale,
    toggleTheme
  };
}
