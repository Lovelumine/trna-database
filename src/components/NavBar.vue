<template>
  <header ref="headerRef" class="site--header" :style="headerStyle">
    <div ref="brandRef" class="site--header__brand">
      <router-link to="/" class="site--url" aria-label="18-tRNA therapeutics database">
        <img src="https://minio.lumoxuan.cn/ensure/bot/logo.webp" class="avatar" alt="18-tRNA therapeutics database">
        <span class="mobile-brand-mark">
          <span class="mobile-brand-mark__title">ENSURE</span>
          <span class="mobile-brand-mark__meta">Suppressor tRNA</span>
        </span>
      </router-link>
    </div>
    <nav class="site--header__center" :class="{ 'has-overflow': navProgressVisible }">
      <div ref="centerScrollRef" class="site--header__center-scroll" @scroll="syncNavProgress">
        <ul ref="centerListRef" class="topNav-items">
        <li><component :is="navLinkComponent" v-bind="navLinkProps('/')" :class="{ 'active-link': isActivePath('/') }">Home</component></li>
        <li><component :is="navLinkComponent" v-bind="navLinkProps('/CodingVariationDisease')" :class="{ 'active-link': isActivePath('/CodingVariationDisease') }">Mutation-induced Disease</component></li>
        <li><component :is="navLinkComponent" v-bind="navLinkProps('/naturalsuptRNA')" :class="{ 'active-link': isActivePath('/naturalsuptRNA') }">Natural sup-tRNA</component></li>
        <li><component :is="navLinkComponent" v-bind="navLinkProps('/tRNAtherapeutics')" :class="{ 'active-link': isActivePath('/tRNAtherapeutics') }">Engineered sup-tRNA</component></li>
        <li><component :is="navLinkComponent" v-bind="navLinkProps('/tRNAElements')" :class="{ 'active-link': isActivePath('/tRNAElements') }">tRNA Elements</component></li>
        <li><component :is="navLinkComponent" v-bind="navLinkProps('/blast')" :class="{ 'active-link': isActivePath('/blast') }">Blast Search</component></li>
        <li><component :is="navLinkComponent" v-bind="navLinkProps('/AIYingying')" :class="{ 'active-link': isActivePath('/AIYingying') }">AI Assistant</component></li>
        <li class="mobile-only"><component :is="navLinkComponent" v-bind="navLinkProps('/download')" :class="{ 'active-link': isActivePath('/download') }">Download</component></li>
        <li class="mobile-only"><a href="/help.html">Help</a></li>
        <li class="mobile-only"><component :is="navLinkComponent" v-bind="navLinkProps('/about')" :class="{ 'active-link': isActivePath('/about') }">About</component></li>
        </ul>
      </div>
      <div v-if="navProgressVisible" class="site--header__progress" aria-hidden="true">
        <span
          class="site--header__progress-bar"
          :style="{ width: `${navProgressWidth}%`, left: `${navProgressOffset}%` }"
        ></span>
      </div>
    </nav>
    <nav ref="rightRef" class="site--header__right">
      <ul class="topNav-items right">
        <li class="mobile-theme-entry">
          <button
            class="theme-toggle"
            type="button"
            :aria-label="`Theme: ${themeLabel}`"
            :title="`Theme: ${themeLabel}`"
            @click="toggleTheme"
          >
            <font-awesome-icon :icon="themeIcon" />
          </button>
        </li>
        <li class="desktop-tool-only"><router-link to="/download" active-class="active-link"><font-awesome-icon :icon="['fas', 'download']" title="Download" /></router-link></li>
        <li class="desktop-tool-only"><a href="/help.html" title="Help"><font-awesome-icon :icon="['fas', 'book']" /></a></li>
        <li class="desktop-tool-only"><router-link to="/about" active-class="active-link"><font-awesome-icon :icon="['fas', 'info-circle']" title="About" /></router-link></li>
        <li class="mobile-menu-only">
          <button
            class="mobile-menu-toggle"
            type="button"
            :aria-label="mobileMenuOpen ? 'Close navigation' : 'Open navigation'"
            :aria-expanded="mobileMenuOpen ? 'true' : 'false'"
            @click="toggleMobileMenu"
          >
            <span class="mobile-menu-toggle__label">{{ mobileMenuOpen ? 'Close' : 'Menu' }}</span>
            <font-awesome-icon :icon="mobileMenuOpen ? ['fas', 'xmark'] : ['fas', 'bars']" />
          </button>
        </li>
      </ul>
    </nav>
    <div v-if="mobileMenuOpen" class="mobile-nav-backdrop" @click="closeMobileMenu"></div>
    <div class="mobile-nav-sheet" :class="{ 'is-open': mobileMenuOpen }">
      <div class="mobile-nav-sheet__header">
        <span>Explore ENSURE</span>
        <button class="mobile-nav-sheet__close" type="button" aria-label="Close navigation" @click="closeMobileMenu">
          <font-awesome-icon :icon="['fas', 'xmark']" />
        </button>
      </div>
      <div class="mobile-nav-links">
        <component :is="navLinkComponent" v-bind="navLinkProps('/')" :class="{ 'active-link': isActivePath('/') }" @click="closeMobileMenu">Home</component>
        <component :is="navLinkComponent" v-bind="navLinkProps('/CodingVariationDisease')" :class="{ 'active-link': isActivePath('/CodingVariationDisease') }" @click="closeMobileMenu">Mutation-induced Disease</component>
        <component :is="navLinkComponent" v-bind="navLinkProps('/naturalsuptRNA')" :class="{ 'active-link': isActivePath('/naturalsuptRNA') }" @click="closeMobileMenu">Natural sup-tRNA</component>
        <component :is="navLinkComponent" v-bind="navLinkProps('/tRNAtherapeutics')" :class="{ 'active-link': isActivePath('/tRNAtherapeutics') }" @click="closeMobileMenu">Engineered sup-tRNA</component>
        <component :is="navLinkComponent" v-bind="navLinkProps('/tRNAElements')" :class="{ 'active-link': isActivePath('/tRNAElements') }" @click="closeMobileMenu">tRNA Elements</component>
        <component :is="navLinkComponent" v-bind="navLinkProps('/blast')" :class="{ 'active-link': isActivePath('/blast') }" @click="closeMobileMenu">Blast Search</component>
        <component :is="navLinkComponent" v-bind="navLinkProps('/AIYingying')" :class="{ 'active-link': isActivePath('/AIYingying') }" @click="closeMobileMenu">AI Assistant</component>
      </div>
      <div class="mobile-nav-tools">
        <button class="mobile-nav-theme" type="button" @click="toggleTheme">
          <font-awesome-icon :icon="themeIcon" />
          <span>Theme: {{ themeLabel }}</span>
        </button>
        <component :is="navLinkComponent" v-bind="navLinkProps('/download')" :class="{ 'active-link': isActivePath('/download') }" @click="closeMobileMenu">
          <font-awesome-icon :icon="['fas', 'download']" />
          <span>Download</span>
        </component>
        <a href="/help.html" @click="closeMobileMenu">
          <font-awesome-icon :icon="['fas', 'book']" />
          <span>Help</span>
        </a>
        <component :is="navLinkComponent" v-bind="navLinkProps('/about')" :class="{ 'active-link': isActivePath('/about') }" @click="closeMobileMenu">
          <font-awesome-icon :icon="['fas', 'info-circle']" />
          <span>About</span>
        </component>
      </div>
    </div>
  </header>
</template>

<script lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue';
import { useRoute } from 'vue-router';
import { getThemeMode, nextThemeMode, setThemeMode } from '../utils/theme';

export default {
  name: 'NavBar',
  setup() {
    const MOBILE_NAV_BREAKPOINT = 760;
    const route = useRoute();
    const themeMode = ref(getThemeMode());
    const headerRef = ref<HTMLElement | null>(null);
    const brandRef = ref<HTMLElement | null>(null);
    const centerScrollRef = ref<HTMLElement | null>(null);
    const centerListRef = ref<HTMLElement | null>(null);
    const rightRef = ref<HTMLElement | null>(null);
    const navCenterMaxWidth = ref(1280);
    const navCenterOffset = ref(0);
    const navProgressVisible = ref(false);
    const navProgressWidth = ref(0);
    const navProgressOffset = ref(0);
    const mobileMenuOpen = ref(false);

    const themeLabel = computed(() => {
      if (themeMode.value === 'dark') return 'Dark';
      if (themeMode.value === 'light') return 'Light';
      return 'System';
    });

    const themeIcon = computed(() => {
      if (themeMode.value === 'dark') return ['fas', 'moon'];
      if (themeMode.value === 'light') return ['fas', 'sun'];
      return ['fas', 'circle-half-stroke'];
    });

    const normalizedPath = computed(() => String(route.path || '').toLowerCase());
    const isStandaloneHelp = computed(() =>
      normalizedPath.value === '/help.html' || normalizedPath.value === '/help'
    );
    const navLinkComponent = computed(() => isStandaloneHelp.value ? 'a' : 'router-link');
    const navLinkProps = (path: string) => isStandaloneHelp.value ? { href: path } : { to: path };
    const isActivePath = (path: string) => normalizedPath.value === path.toLowerCase();

    const ensureActiveNavVisible = (behavior: ScrollBehavior = 'auto') => {
      const scrollEl = centerScrollRef.value;
      if (!scrollEl || window.innerWidth <= MOBILE_NAV_BREAKPOINT) return;

      const activeEl = scrollEl.querySelector('.topNav-items .active-link') as HTMLElement | null;
      if (!activeEl) return;

      const targetLeft = activeEl.offsetLeft - Math.max((scrollEl.clientWidth - activeEl.offsetWidth) / 2, 0);
      const maxScrollLeft = Math.max(scrollEl.scrollWidth - scrollEl.clientWidth, 0);
      const nextLeft = Math.max(0, Math.min(targetLeft, maxScrollLeft));

      scrollEl.scrollTo({ left: nextLeft, behavior });
    };

    const toggleTheme = () => {
      const next = nextThemeMode(themeMode.value);
      themeMode.value = next;
      setThemeMode(next);
      nextTick(syncHeaderLayout);
    };

    const closeMobileMenu = () => {
      mobileMenuOpen.value = false;
    };

    const toggleMobileMenu = () => {
      mobileMenuOpen.value = !mobileMenuOpen.value;
    };

    const headerStyle = computed(() => ({
      '--nav-center-max-width': `${navCenterMaxWidth.value}px`,
      '--nav-center-offset': `${navCenterOffset.value}px`
    }));

    const syncNavProgress = () => {
      const scrollEl = centerScrollRef.value;
      if (!scrollEl) return;

      const hiddenWidth = scrollEl.scrollWidth - scrollEl.clientWidth;
      const hasOverflow = window.innerWidth > MOBILE_NAV_BREAKPOINT && hiddenWidth > 8;

      navProgressVisible.value = hasOverflow;

      if (!hasOverflow) {
        navProgressWidth.value = 0;
        navProgressOffset.value = 0;
        scrollEl.scrollLeft = 0;
        return;
      }

      const thumbWidth = Math.max((scrollEl.clientWidth / scrollEl.scrollWidth) * 100, 18);
      const maxOffset = 100 - thumbWidth;
      const thumbOffset = hiddenWidth > 0 ? (scrollEl.scrollLeft / hiddenWidth) * maxOffset : 0;

      navProgressWidth.value = Math.min(thumbWidth, 100);
      navProgressOffset.value = Math.max(0, Math.min(thumbOffset, maxOffset));
    };

    const syncHeaderLayout = () => {
      const headerRect = headerRef.value?.getBoundingClientRect();
      if (!headerRect) return;

      const brandRect = brandRef.value?.getBoundingClientRect();
      const rightRect = rightRef.value?.getBoundingClientRect();
      const safeGap = headerRect.width > 1500 ? 10 : headerRect.width > 1320 ? 8 : 6;
      const safeLeft = brandRect ? brandRect.right - headerRect.left + safeGap : safeGap;
      const safeRight = rightRect ? rightRect.left - headerRect.left - safeGap : headerRect.width - safeGap;
      const corridorWidth = safeRight - safeLeft;
      const corridorCenter = safeLeft + corridorWidth / 2;

      navCenterMaxWidth.value = Math.max(Math.floor(corridorWidth), 320);
      navCenterOffset.value = window.innerWidth > MOBILE_NAV_BREAKPOINT
        ? Math.round(corridorCenter - headerRect.width / 2)
        : 0;

      if (window.innerWidth > MOBILE_NAV_BREAKPOINT && mobileMenuOpen.value) {
        closeMobileMenu();
      }

      nextTick(() => {
        ensureActiveNavVisible();
        syncNavProgress();
      });
    };

    const setScrollLock = (locked: boolean) => {
      const value = locked ? 'hidden' : '';
      document.documentElement.style.overflow = value;
      document.body.style.overflow = value;
    };

    const handleKeydown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        closeMobileMenu();
      }
    };

    onMounted(() => {
      nextTick(syncHeaderLayout);
      window.addEventListener('resize', syncHeaderLayout);
      window.addEventListener('keydown', handleKeydown);
      window.setTimeout(syncHeaderLayout, 120);
    });

    onBeforeUnmount(() => {
      window.removeEventListener('resize', syncHeaderLayout);
      window.removeEventListener('keydown', handleKeydown);
      setScrollLock(false);
    });

    watch(mobileMenuOpen, (open) => {
      setScrollLock(open);
    });

    watch(normalizedPath, () => {
      nextTick(() => {
        ensureActiveNavVisible('smooth');
        syncNavProgress();
      });
    });

    return {
      themeLabel,
      themeIcon,
      navLinkComponent,
      navLinkProps,
      isActivePath,
      toggleTheme,
      closeMobileMenu,
      toggleMobileMenu,
      headerRef,
      brandRef,
      centerScrollRef,
      centerListRef,
      rightRef,
      navCenterOffset,
      navProgressVisible,
      navProgressWidth,
      navProgressOffset,
      syncNavProgress,
      ensureActiveNavVisible,
      mobileMenuOpen,
      headerStyle
    };
  }
}
</script>

<style>
.site--header {
  padding: 20px 80px;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 108px;
}

.site--header__brand {
  display: flex;
  align-items: center;
  z-index: 2;
  flex: 0 0 auto;
}

.site--url {
  display: inline-flex;
  align-items: center;
  font-size: 18px;
  font-weight: 700;
  text-decoration: none;
  color: inherit;
}

.site--url .avatar {
  margin-right: 10px;
  height: 64px;
  width: 64px;
  min-width: 64px;
  border: 3px solid var(--farallon-background-white);
  border-radius: 50%;
  box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2);
  transition: .5s ease-in-out;
  overflow: hidden;
  background-color: var(--farallon-background-white);
  display: block;
  object-fit: cover;
  object-position: center;
  aspect-ratio: 1 / 1;
  flex: 0 0 auto;
}

.mobile-brand-mark {
  display: none;
  flex-direction: column;
  gap: 2px;
  margin-left: 12px;
  line-height: 1;
}

.mobile-brand-mark__title {
  font-size: 0.96rem;
  font-weight: 800;
  letter-spacing: 0.05em;
}

.mobile-brand-mark__meta {
  font-size: 0.72rem;
  color: var(--farallon-text-light);
}

.site--header__center {
  position: absolute;
  left: 50%;
  top: 25px;
  transform: translateX(calc(-50% + var(--nav-center-offset, 0px)));
  z-index: 1;
  height: 48px;
  width: max-content;
  max-width: min(var(--nav-center-max-width), calc(100% - 32px));
  box-shadow: 0 0 0 1px var(--farallon-border-color-light),
    0 12px 18px -6px rgba(39, 39, 42, 0.1),
    0 5px 8px -5px rgba(39, 39, 42, 0.08);
  -webkit-backdrop-filter: blur(12px);
  backdrop-filter: blur(12px);
  background-color: rgba(255, 255, 255, 0.76);
  border: 1px solid var(--farallon-border-color-light);
  border-radius: 999rem;
  overflow: hidden;
}

.site--header__center-scroll {
  height: 100%;
  overflow-x: auto;
  overflow-y: hidden;
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.site--header__center-scroll::-webkit-scrollbar {
  display: none;
}

.site--header__right {
  position: absolute;
  right: 80px;
  top: 25px;
  z-index: 2;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  min-height: 43px;
}

.topNav-items .mobile-only {
  display: none;
}

.topNav-items {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: clamp(12px, 1vw, 16px);
  height: 44px;
  box-sizing: border-box;
  width: max-content;
  padding: 0 clamp(24px, 2.4vw, 36px);
  margin: 0;
  list-style: none;
  overflow: visible;
  white-space: nowrap;
}

.topNav-items.right {
  gap: 6px;
  padding: 0;
  height: auto;
  width: auto;
  overflow: visible;
  white-space: nowrap;
}

.topNav-items li {
  display: inline-flex;
  align-items: center;
  margin-right: 0;
  padding: 0;
}

.topNav-items li a {
  color: var(--farallon-text-color);
  text-decoration: none;
  border-bottom: 2px solid transparent;
  transition: border-color 0.3s, color 0.3s;
  font-size: clamp(1rem, 0.94rem + 0.2vw, 1.1rem);
  line-height: 1.2;
  padding: 10px 0;
}

.topNav-items li a:hover {
  border-bottom: 2px solid var(--farallon-border-color);
}

.topNav-items li .active-link {
  color: var(--farallon-hover-color);
  border-bottom: 2px solid var(--farallon-hover-color);
}

.topNav-items.right li a {
  width: 32px;
  height: 32px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  border-radius: 999rem;
  border-bottom: none;
}

.topNav-items.right li a:hover,
.topNav-items.right li .active-link {
  border-bottom: none;
  background-color: var(--farallon-background-gray);
}

.theme-toggle {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  border-radius: 999px;
  border: 1px solid var(--farallon-border-color);
  background-color: var(--farallon-background-white);
  color: var(--farallon-text-color);
  padding: 0;
  cursor: pointer;
  transition: background-color 0.2s ease, border-color 0.2s ease;
}

.theme-toggle:hover {
  background-color: var(--farallon-background-gray);
  border-color: var(--farallon-border-color);
}

.mobile-menu-only {
  display: none !important;
}

.mobile-menu-toggle,
.mobile-nav-sheet__close {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  border-radius: 999px;
  border: 1px solid var(--farallon-border-color);
  background-color: var(--farallon-background-white);
  color: var(--farallon-text-color);
  padding: 0;
  cursor: pointer;
  transition: background-color 0.2s ease, border-color 0.2s ease;
}

.mobile-menu-toggle {
  gap: 10px;
  width: auto;
  min-width: 96px;
  padding: 0 16px;
  border-color: rgba(78, 120, 191, 0.18);
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.96), rgba(243, 247, 255, 0.92));
  box-shadow: 0 10px 16px -14px rgba(65, 90, 140, 0.28);
}

.mobile-menu-toggle__label {
  font-size: 0.95rem;
  font-weight: 700;
  letter-spacing: 0.01em;
}

.mobile-menu-toggle:hover,
.mobile-nav-sheet__close:hover {
  background-color: var(--farallon-background-gray);
  border-color: var(--farallon-border-color);
}

.mobile-nav-backdrop {
  position: fixed;
  inset: 0;
  z-index: 120;
  background: rgba(10, 16, 28, 0.26);
  -webkit-backdrop-filter: blur(8px);
  backdrop-filter: blur(8px);
}

.mobile-nav-sheet {
  position: fixed;
  top: 76px;
  left: 12px;
  right: 12px;
  z-index: 130;
  display: none;
  padding: 14px;
  border-radius: 28px;
  border: 1px solid var(--farallon-border-color-light);
  background: rgba(255, 255, 255, 0.92);
  -webkit-backdrop-filter: blur(18px);
  backdrop-filter: blur(18px);
  box-shadow: 0 20px 30px -20px rgba(39, 39, 42, 0.34),
    0 10px 16px -12px rgba(39, 39, 42, 0.22);
}

.mobile-nav-sheet.is-open {
  display: block;
}

.mobile-nav-sheet__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
  padding: 2px 2px 8px;
  color: var(--farallon-text-color);
  font-size: 1rem;
  font-weight: 700;
}

.mobile-nav-links {
  display: grid;
  gap: 8px;
}

.mobile-nav-links a {
  display: block;
  padding: 14px 16px;
  border-radius: 18px;
  border: 1px solid transparent;
  color: var(--farallon-text-color);
  text-decoration: none;
  background: rgba(255, 255, 255, 0.55);
}

.mobile-nav-links a:hover,
.mobile-nav-links a.active-link {
  border-color: var(--farallon-border-color-light);
  background: var(--farallon-background-white);
  color: var(--farallon-hover-color);
}

.mobile-nav-tools {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 8px;
  margin-top: 12px;
}

.mobile-nav-tools a {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  min-height: 44px;
  padding: 0 12px;
  border-radius: 16px;
  border: 1px solid var(--farallon-border-color-light);
  color: var(--farallon-text-color);
  text-decoration: none;
  background: rgba(255, 255, 255, 0.55);
}

.mobile-nav-theme {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  min-height: 44px;
  padding: 0 12px;
  border-radius: 16px;
  border: 1px solid var(--farallon-border-color-light);
  color: var(--farallon-text-color);
  background: rgba(255, 255, 255, 0.55);
  cursor: pointer;
}

.mobile-nav-tools a:hover,
.mobile-nav-tools a.active-link,
.mobile-nav-theme:hover {
  background: var(--farallon-background-white);
  color: var(--farallon-hover-color);
}

.site--header__progress {
  position: absolute;
  left: 20px;
  right: 20px;
  top: 6px;
  height: 2px;
  border-radius: 999px;
  background: rgba(87, 105, 145, 0.12);
  overflow: hidden;
}

.site--header__progress-bar {
  position: absolute;
  top: 0;
  bottom: 0;
  border-radius: 999px;
  background: linear-gradient(90deg, rgba(76, 110, 175, 0.72), rgba(108, 141, 204, 0.92));
}

@media (max-width: 1500px) and (min-width: 761px) {
  .site--header {
    padding: 18px 56px;
    min-height: 98px;
  }

  .site--header__center,
  .site--header__right {
    top: 22px;
  }

  .site--header__right {
    right: 56px;
  }

  .site--url .avatar {
    height: 58px;
    width: 58px;
  }

  .topNav-items {
    gap: 10px;
    padding: 0 22px;
  }

  .topNav-items.right {
    gap: 5px;
  }
}

@media (max-width: 1320px) and (min-width: 761px) {
  .site--header {
    padding: 16px 36px;
    min-height: 90px;
  }

  .site--header__center,
  .site--header__right {
    top: 18px;
  }

  .site--header__right {
    right: 36px;
    padding: 4px 6px;
  }

  .site--header__center {
    height: 46px;
  }

  .topNav-items {
    height: 42px;
    gap: 8px;
    padding: 0 18px;
  }

  .topNav-items li a {
    font-size: 0.98rem;
    padding: 9px 0;
  }

  .site--url .avatar {
    height: 52px;
    width: 52px;
  }

  .theme-toggle {
    width: 31px;
    height: 31px;
  }
}

@media (prefers-color-scheme: dark) {
  .site--header__center {
    background-color: rgba(23, 26, 33, 0.85);
    box-shadow: 0 0 0 1px var(--farallon-border-color-light),
      0 10px 20px -8px rgba(0, 0, 0, 0.6);
  }
}

:root[data-theme="dark"] .site--header__center {
  background-color: rgba(23, 26, 33, 0.85);
  box-shadow: 0 0 0 1px var(--farallon-border-color-light),
    0 10px 20px -8px rgba(0, 0, 0, 0.6);
}

:root[data-theme="dark"] .mobile-nav-backdrop {
  background: rgba(4, 8, 16, 0.44);
}

:root[data-theme="dark"] .mobile-menu-toggle {
  border-color: rgba(122, 168, 255, 0.24);
  background: linear-gradient(135deg, rgba(34, 38, 48, 0.96), rgba(28, 36, 54, 0.94));
  box-shadow: 0 12px 18px -16px rgba(0, 0, 0, 0.48);
}

:root[data-theme="dark"] .mobile-nav-sheet {
  background: rgba(23, 26, 33, 0.94);
  box-shadow: 0 22px 34px -22px rgba(0, 0, 0, 0.64),
    0 10px 16px -12px rgba(0, 0, 0, 0.4);
}

:root[data-theme="dark"] .mobile-nav-links a,
:root[data-theme="dark"] .mobile-nav-tools a,
:root[data-theme="dark"] .mobile-nav-theme {
  background: rgba(34, 38, 48, 0.76);
}

:root[data-theme="dark"] .mobile-nav-links a:hover,
:root[data-theme="dark"] .mobile-nav-links a.active-link,
:root[data-theme="dark"] .mobile-nav-tools a:hover,
:root[data-theme="dark"] .mobile-nav-tools a.active-link,
:root[data-theme="dark"] .mobile-nav-theme:hover {
  background: rgba(44, 50, 64, 0.96);
}

@media (max-width: 760px) {
  .site--header {
    padding: 12px 14px 8px;
    display: grid;
    grid-template-columns: auto 1fr;
    grid-template-areas: "logo right";
    align-items: center;
    row-gap: 0;
    min-height: 0;
  }

  header.site--header {
    padding-top: 12px;
  }

  .site--header__brand {
    grid-area: logo;
  }

  .site--header__center {
    display: none !important;
  }

  .site--header__right {
    grid-area: right;
    position: static;
    display: flex;
    width: auto;
    min-height: 40px;
    padding: 0;
    border: none;
    background: transparent;
    -webkit-backdrop-filter: none;
    backdrop-filter: none;
    box-shadow: none;
    justify-content: flex-end;
    margin-top: 0;
  }

  .topNav-items.right {
    justify-content: flex-end;
    padding: 0;
    overflow: visible;
    height: auto;
    width: auto;
    gap: 8px;
  }

  .topNav-items.right .desktop-tool-only {
    display: none;
  }

  .mobile-theme-entry {
    display: none;
  }

  .topNav-items.right .mobile-menu-only {
    display: inline-flex !important;
  }

  .mobile-menu-toggle {
    min-width: 102px;
    height: 42px;
    padding: 0 15px;
  }

  .site--header__brand .avatar {
    height: 48px;
    width: 48px;
    margin-right: 0;
  }

  .mobile-brand-mark {
    display: inline-flex;
  }

  .mobile-nav-sheet {
    top: 84px;
    left: 14px;
    right: 14px;
  }
}

@media (max-width: 767px) {
  .mobile-brand-mark__title {
    font-size: 0.9rem;
  }

  .mobile-brand-mark__meta {
    font-size: 0.68rem;
  }

  .mobile-menu-toggle {
    min-width: 96px;
    height: 40px;
    padding: 0 14px;
  }

  .mobile-nav-tools {
    grid-template-columns: 1fr;
  }
}

</style>
