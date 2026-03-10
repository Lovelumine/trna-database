<template>
  <div class="admin-login-page">
    <div class="admin-login-shell">
      <header class="admin-login-topbar">
        <div class="admin-login-brand">
          <div class="admin-login-brand-mark">EA</div>
          <div class="admin-login-brand-copy">
            <strong>{{ t('brand.admin') }}</strong>
          </div>
        </div>

        <div class="admin-login-tools">
          <button class="admin-login-tool" type="button" :title="t('tool.language')" @click="toggleLocale">
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path
                d="M12 3a9 9 0 1 0 9 9a9.01 9.01 0 0 0-9-9Zm5.64 5h-2.2a14.5 14.5 0 0 0-1.08-2.67A7.02 7.02 0 0 1 17.64 8ZM12 5.05A12.4 12.4 0 0 1 13.39 8h-2.78A12.4 12.4 0 0 1 12 5.05ZM5.36 14a7.4 7.4 0 0 1 0-4h2.51a16.2 16.2 0 0 0 0 4Zm1 2h2.2a14.5 14.5 0 0 0 1.08 2.67A7.02 7.02 0 0 1 6.36 16ZM8.56 8h-2.2a7.02 7.02 0 0 1 3.28-2.67A14.5 14.5 0 0 0 8.56 8Zm3.44 10.95A12.4 12.4 0 0 1 10.61 16h2.78A12.4 12.4 0 0 1 12 18.95ZM13.83 14h-3.66a14.38 14.38 0 0 1 0-4h3.66a14.38 14.38 0 0 1 0 4Zm.53 4.67A14.5 14.5 0 0 0 15.44 16h2.2a7.02 7.02 0 0 1-3.28 2.67ZM16.13 14a16.2 16.2 0 0 0 0-4h2.51a7.4 7.4 0 0 1 0 4Z"
                fill="currentColor"
              />
            </svg>
            <span class="admin-login-tool-badge">{{ localeBadge }}</span>
          </button>

          <button class="admin-login-tool" type="button" :title="themeLabel" @click="toggleTheme">
            <svg v-if="themeMode === 'dark'" viewBox="0 0 24 24" aria-hidden="true">
              <path d="M20.74 15.28A8.68 8.68 0 0 1 8.72 3.26A9 9 0 1 0 20.74 15.28Z" fill="currentColor" />
            </svg>
            <svg v-else-if="themeMode === 'light'" viewBox="0 0 24 24" aria-hidden="true">
              <path
                d="M6.76 4.84l-1.8-1.79l-1.41 1.41l1.79 1.8l1.42-1.42Zm10.48 0l1.42 1.42l1.79-1.8l-1.41-1.41l-1.8 1.79ZM12 4h1V1h-2v3h1Zm7 8h3v-2h-3v2Zm-7 7h-1v3h2v-3h-1Zm8.95-.64l-1.79-1.79l-1.42 1.41l1.8 1.8l1.41-1.42ZM4.84 17.24l-1.79 1.8l1.41 1.41l1.8-1.79l-1.42-1.42ZM4 12H1v-2h3v2Zm8 5a5 5 0 1 1 0-10a5 5 0 0 1 0 10Z"
                fill="currentColor"
              />
            </svg>
            <svg v-else viewBox="0 0 24 24" aria-hidden="true">
              <path
                d="M12 2a10 10 0 0 0 0 20a1 1 0 0 0 0-2a8 8 0 1 1 0-16a1 1 0 0 0 0-2Zm0 2v16a8 8 0 0 0 0-16Z"
                fill="currentColor"
              />
            </svg>
          </button>
        </div>
      </header>

      <main class="admin-login-stage">
        <section class="admin-login-brief">
          <h1>{{ t('login.heroTitle') }}</h1>
          <p>{{ t('login.heroLead') }}</p>
          <ul class="admin-login-points">
            <li>{{ t('login.featureContentTitle') }}</li>
            <li>{{ t('login.featureAiTitle') }}</li>
            <li>{{ t('login.featureAuditTitle') }}</li>
          </ul>
        </section>

        <section class="admin-login-panel">
          <div class="admin-login-copy">
            <h2>{{ t('login.title') }}</h2>
            <p>{{ t('login.lead') }}</p>
          </div>

          <el-form class="admin-login-form" @submit.prevent="handleLogin">
            <el-form-item :label="t('login.username')">
              <el-input v-model="username" autocomplete="username" :placeholder="t('login.usernamePlaceholder')" />
            </el-form-item>

            <el-form-item :label="t('login.password')">
              <el-input
                v-model="password"
                type="password"
                show-password
                autocomplete="current-password"
                :placeholder="t('login.passwordPlaceholder')"
                @keyup.enter="handleLogin"
              />
            </el-form-item>

            <el-button type="primary" :loading="submitting" class="admin-login-button" @click="handleLogin">
              {{ t('login.submit') }}
            </el-button>
          </el-form>

          <button class="admin-login-site-link" type="button" @click="openSite">
            {{ t('login.openSite') }}
          </button>
        </section>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';

import { useAdminI18n } from '@/utils/adminI18n';

const route = useRoute();
const router = useRouter();
const { locale, themeMode, setLocale, toggleTheme, t, themeLabel } = useAdminI18n();

const username = ref('');
const password = ref('');
const submitting = ref(false);

const localeBadge = computed(() => (locale.value === 'zh-CN' ? '中' : 'EN'));

function toggleLocale() {
  setLocale(locale.value === 'zh-CN' ? 'en' : 'zh-CN');
}

async function handleLogin() {
  if (!username.value.trim() || !password.value) {
    ElMessage.error(t('login.missing'));
    return;
  }

  submitting.value = true;
  try {
    const resp = await fetch('/admin/api/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      credentials: 'same-origin',
      body: JSON.stringify({
        username: username.value.trim(),
        password: password.value
      })
    });

    const json = await resp.json().catch(() => ({}));
    if (!resp.ok || json?.error) {
      throw new Error(json?.error || t('login.failed'));
    }

    const next = typeof route.query.next === 'string' ? route.query.next : '/workspace';
    ElMessage.success(t('login.success'));
    await router.replace(next);
  } catch (error: any) {
    ElMessage.error(error?.message || t('login.failed'));
  } finally {
    submitting.value = false;
  }
}

function openSite() {
  window.open('/', '_blank', 'noopener,noreferrer');
}
</script>

<style scoped>
.admin-login-page {
  min-height: 100vh;
  padding: 24px;
  background:
    radial-gradient(circle at top left, rgba(37, 99, 235, 0.08), transparent 26%),
    linear-gradient(180deg, var(--admin-page) 0%, var(--admin-bg) 100%);
}

.admin-login-shell {
  width: min(1440px, calc(100vw - 48px));
  min-height: calc(100vh - 48px);
  margin: 0 auto;
  display: grid;
  grid-template-rows: auto 1fr;
  border: 1px solid var(--admin-border);
  border-radius: 28px;
  background: color-mix(in srgb, var(--admin-surface) 96%, transparent);
  box-shadow: 0 24px 60px rgba(15, 23, 42, 0.08);
  overflow: hidden;
}

.admin-login-topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 22px 28px;
  border-bottom: 1px solid var(--admin-border);
}

.admin-login-brand {
  display: inline-flex;
  align-items: center;
  gap: 14px;
}

.admin-login-brand-mark {
  width: 42px;
  height: 42px;
  border-radius: 14px;
  display: grid;
  place-items: center;
  font-size: 0.9rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  color: #eff6ff;
  background: linear-gradient(135deg, #60a5fa, #2563eb);
}

.admin-login-brand-copy strong {
  font-size: 1rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  color: var(--admin-text);
}

.admin-login-tools {
  display: inline-flex;
  gap: 10px;
}

.admin-login-tool {
  position: relative;
  width: 40px;
  height: 40px;
  border-radius: 999px;
  border: 1px solid var(--admin-border);
  background: var(--admin-surface);
  color: var(--admin-text-muted);
  display: grid;
  place-items: center;
  cursor: pointer;
}

.admin-login-tool:hover {
  background: var(--admin-surface-soft);
  border-color: var(--admin-border-strong);
  color: var(--admin-text);
}

.admin-login-tool svg {
  width: 17px;
  height: 17px;
}

.admin-login-tool-badge {
  position: absolute;
  right: -1px;
  bottom: -1px;
  min-width: 16px;
  height: 16px;
  padding: 0 4px;
  border-radius: 999px;
  display: grid;
  place-items: center;
  font-size: 0.62rem;
  font-weight: 800;
  color: #fff;
  background: var(--admin-accent);
  box-shadow: 0 0 0 2px var(--admin-surface);
}

.admin-login-stage {
  display: grid;
  grid-template-columns: minmax(360px, 1fr) minmax(420px, 520px);
  align-items: center;
  gap: 80px;
  padding: 40px 56px 56px;
}

.admin-login-brief {
  display: grid;
  gap: 18px;
  max-width: 540px;
}

.admin-login-brief h1,
.admin-login-copy h2 {
  margin: 0;
  line-height: 1.05;
  letter-spacing: -0.05em;
}

.admin-login-brief h1 {
  font-size: clamp(2.8rem, 5vw, 4.6rem);
  color: var(--admin-text);
}

.admin-login-brief p,
.admin-login-copy p {
  margin: 0;
  color: var(--admin-text-muted);
  line-height: 1.75;
}

.admin-login-points {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  padding: 0;
  margin: 4px 0 0;
  list-style: none;
}

.admin-login-points li {
  padding: 10px 14px;
  border-radius: 999px;
  border: 1px solid var(--admin-border);
  background: var(--admin-surface);
  font-weight: 700;
  color: var(--admin-text);
}

.admin-login-panel {
  width: 100%;
  display: grid;
  gap: 22px;
  padding: 28px;
  border-radius: 24px;
  border: 1px solid var(--admin-border);
  background: var(--admin-surface);
}

.admin-login-copy {
  display: grid;
  gap: 8px;
}

.admin-login-copy h2 {
  font-size: clamp(2rem, 3vw, 2.4rem);
}

.admin-login-form {
  width: 100%;
}

.admin-login-button,
.admin-login-site-link {
  width: 100%;
  min-height: 48px;
  border-radius: 14px;
  font-weight: 800;
}

.admin-login-button {
  margin-top: 8px;
}

.admin-login-site-link {
  border: 1px solid var(--admin-border);
  background: var(--admin-surface-muted);
  color: var(--admin-text);
  cursor: pointer;
}

.admin-login-site-link:hover {
  background: var(--admin-surface-soft);
  border-color: var(--admin-border-strong);
}

:deep(.el-form-item) {
  margin-bottom: 18px;
}

:deep(.el-form-item__label) {
  margin-bottom: 6px;
  font-weight: 700;
  color: var(--admin-text-muted);
}

:deep(.el-input__wrapper) {
  min-height: 46px;
  border-radius: 12px;
  box-shadow: 0 0 0 1px var(--admin-border) inset;
  background: var(--admin-surface);
}

:deep(.el-input__wrapper.is-focus) {
  box-shadow:
    0 0 0 2px color-mix(in srgb, var(--admin-accent) 16%, transparent),
    0 0 0 1px color-mix(in srgb, var(--admin-accent) 42%, transparent) inset;
}

:global(:root[data-admin-theme='dark']) .admin-login-page {
  background:
    radial-gradient(circle at top left, rgba(59, 130, 246, 0.12), transparent 26%),
    linear-gradient(180deg, #0f172a 0%, #0b1220 100%);
}

:global(:root[data-admin-theme='dark']) .admin-login-shell {
  background: #0f1a2e;
  box-shadow: 0 28px 70px rgba(2, 6, 23, 0.34);
}

:global(:root[data-admin-theme='dark']) .admin-login-topbar {
  border-bottom-color: rgba(148, 163, 184, 0.16);
}

:global(:root[data-admin-theme='dark']) .admin-login-brand-copy strong,
:global(:root[data-admin-theme='dark']) .admin-login-brief h1,
:global(:root[data-admin-theme='dark']) .admin-login-points li {
  color: #f8fafc;
}

:global(:root[data-admin-theme='dark']) .admin-login-brief p,
:global(:root[data-admin-theme='dark']) .admin-login-copy p {
  color: rgba(226, 232, 240, 0.76);
}

:global(:root[data-admin-theme='dark']) .admin-login-panel,
:global(:root[data-admin-theme='dark']) .admin-login-points li,
:global(:root[data-admin-theme='dark']) .admin-login-tool {
  background: #162235;
  border-color: rgba(148, 163, 184, 0.18);
}

:global(:root[data-admin-theme='dark']) .admin-login-tool {
  color: #dbeafe;
}

:global(:root[data-admin-theme='dark']) .admin-login-tool:hover {
  background: #1d2b43;
  border-color: rgba(147, 197, 253, 0.24);
}

:global(:root[data-admin-theme='dark']) .admin-login-tool-badge {
  box-shadow: 0 0 0 2px #162235;
}

@media (max-width: 1080px) {
  .admin-login-shell {
    width: calc(100vw - 32px);
    min-height: auto;
  }

  .admin-login-stage {
    grid-template-columns: 1fr;
    gap: 32px;
    padding: 28px;
  }

  .admin-login-brief {
    max-width: none;
  }
}

@media (max-width: 640px) {
  .admin-login-page {
    padding: 12px;
  }

  .admin-login-shell {
    width: 100%;
    border-radius: 22px;
  }

  .admin-login-topbar,
  .admin-login-stage {
    padding-left: 18px;
    padding-right: 18px;
  }

  .admin-login-topbar {
    padding-top: 16px;
    padding-bottom: 16px;
  }

  .admin-login-stage {
    padding-top: 22px;
    padding-bottom: 22px;
  }

  .admin-login-brief h1 {
    font-size: 2.2rem;
  }

  .admin-login-copy h2 {
    font-size: 1.9rem;
  }

  .admin-login-panel {
    padding: 20px;
    border-radius: 20px;
  }
}
</style>
