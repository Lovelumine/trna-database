<template>
  <div class="admin-login-page">
    <div class="admin-login-shell">
      <section class="admin-login-panel admin-login-panel--hero">
        <div class="admin-login-controls">
          <div class="admin-segmented">
            <button class="admin-segmented-item" :class="{ active: locale === 'zh-CN' }" type="button" @click="setLocale('zh-CN')">
              {{ t('prefs.languageZh') }}
            </button>
            <button class="admin-segmented-item" :class="{ active: locale === 'en' }" type="button" @click="setLocale('en')">
              {{ t('prefs.languageEn') }}
            </button>
          </div>

          <button class="admin-theme-toggle" type="button" @click="toggleTheme">
            {{ themeLabel }}
          </button>
        </div>

        <p class="admin-login-eyebrow">{{ t('brand.eyebrow') }}</p>
        <h1>{{ t('login.heroTitle') }}</h1>
        <p class="admin-login-lead">{{ t('login.heroLead') }}</p>

        <div class="admin-login-feature-list">
          <article class="admin-login-feature">
            <strong>{{ t('login.featureContentTitle') }}</strong>
            <span>{{ t('login.featureContentDesc') }}</span>
          </article>
          <article class="admin-login-feature">
            <strong>{{ t('login.featureAiTitle') }}</strong>
            <span>{{ t('login.featureAiDesc') }}</span>
          </article>
          <article class="admin-login-feature">
            <strong>{{ t('login.featureAuditTitle') }}</strong>
            <span>{{ t('login.featureAuditDesc') }}</span>
          </article>
        </div>
      </section>

      <section class="admin-login-panel admin-login-panel--form">
        <div class="admin-login-copy">
          <p class="admin-login-form-eyebrow">{{ t('login.signIn') }}</p>
          <h2>{{ t('login.title') }}</h2>
          <p>{{ t('login.lead') }}</p>
        </div>

        <el-form @submit.prevent="handleLogin">
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
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';

import { useAdminI18n } from '@/utils/adminI18n';

const route = useRoute();
const router = useRouter();
const { locale, setLocale, toggleTheme, themeLabel, t } = useAdminI18n();

const username = ref('');
const password = ref('');
const submitting = ref(false);

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
  display: grid;
  place-items: center;
  padding: 28px;
}

.admin-login-shell {
  width: min(1120px, 100%);
  display: grid;
  grid-template-columns: 1.15fr minmax(360px, 0.85fr);
  border: 1px solid var(--admin-border);
  border-radius: 32px;
  overflow: hidden;
  box-shadow: var(--admin-shadow);
  background: color-mix(in srgb, var(--admin-surface) 92%, transparent);
  backdrop-filter: blur(12px);
}

.admin-login-panel {
  padding: 40px;
}

.admin-login-panel--hero {
  background:
    radial-gradient(circle at top left, rgba(96, 165, 250, 0.24), transparent 26%),
    linear-gradient(160deg, #0f172a 0%, #111b30 54%, #172554 100%);
  color: #eff6ff;
  display: grid;
  gap: 20px;
  align-content: space-between;
}

.admin-login-panel--form {
  display: grid;
  align-content: center;
  gap: 18px;
}

.admin-login-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.admin-segmented {
  display: inline-flex;
  gap: 4px;
  padding: 4px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.12);
}

.admin-segmented-item,
.admin-theme-toggle {
  border: 0;
  background: transparent;
  color: rgba(239, 246, 255, 0.78);
  padding: 10px 14px;
  border-radius: 999px;
  font-weight: 700;
}

.admin-segmented-item.active {
  background: rgba(255, 255, 255, 0.14);
  color: #fff;
}

.admin-theme-toggle {
  border: 1px solid rgba(255, 255, 255, 0.12);
  background: rgba(255, 255, 255, 0.08);
}

.admin-login-eyebrow,
.admin-login-form-eyebrow {
  margin: 0;
  font-size: 0.78rem;
  font-weight: 800;
  letter-spacing: 0.18em;
  text-transform: uppercase;
}

.admin-login-eyebrow {
  color: #93c5fd;
}

.admin-login-form-eyebrow {
  color: var(--admin-accent);
}

.admin-login-panel--hero h1,
.admin-login-copy h2 {
  margin: 0;
  line-height: 1.05;
}

.admin-login-panel--hero h1 {
  font-size: clamp(2.6rem, 5vw, 4.3rem);
  max-width: 8ch;
}

.admin-login-copy {
  display: grid;
  gap: 8px;
}

.admin-login-copy p,
.admin-login-lead {
  margin: 0;
  color: inherit;
  line-height: 1.7;
}

.admin-login-lead {
  max-width: 42ch;
  color: rgba(239, 246, 255, 0.8);
}

.admin-login-feature-list {
  display: grid;
  gap: 14px;
}

.admin-login-feature {
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 18px;
  padding: 16px 18px;
  background: rgba(255, 255, 255, 0.06);
}

.admin-login-feature strong {
  display: block;
  margin-bottom: 4px;
  font-size: 0.95rem;
}

.admin-login-feature span {
  color: rgba(239, 246, 255, 0.72);
  line-height: 1.65;
  font-size: 0.96rem;
}

.admin-login-button {
  width: 100%;
  min-height: 48px;
  margin-top: 8px;
  border-radius: 14px;
  font-weight: 700;
}

.admin-login-site-link {
  width: 100%;
  border: 1px solid var(--admin-border);
  background: var(--admin-surface-muted);
  color: var(--admin-text-muted);
  padding: 14px 16px;
  border-radius: 14px;
  font-weight: 700;
}

@media (max-width: 980px) {
  .admin-login-shell {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .admin-login-page {
    padding: 16px;
  }

  .admin-login-panel {
    padding: 24px;
  }

  .admin-login-controls {
    justify-content: flex-start;
  }

  .admin-login-panel--hero h1 {
    font-size: 2.4rem;
  }
}
</style>
