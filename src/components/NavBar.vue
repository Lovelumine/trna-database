<template>
  <header class="site--header">
    <router-link to="/" class="site--url" aria-label="18-tRNA therapeutics database">
      <img src="https://minio.lumoxuan.cn/ensure/bot/logo.webp" class="avatar" alt="18-tRNA therapeutics database">
    </router-link>
    <nav class="site--header__center">
      <ul class="topNav-items">
        <li><router-link to="/" active-class="active-link">Home</router-link></li>
        <li><router-link to="/CodingVariationDisease" active-class="active-link">Mutation-induced Disease</router-link></li>
        <li><router-link to="/naturalsuptRNA" active-class="active-link">Natural sup-tRNA</router-link></li>
        <li><router-link to="/tRNAtherapeutics" active-class="active-link">Engineered sup-tRNA</router-link></li>
        <li><router-link to="/tRNAElements" active-class="active-link">tRNA Elements</router-link></li>
        <li><router-link to="/blast" active-class="active-link">Blast Search</router-link></li>
        <li><router-link to="/AIyingying" active-class="active-link">AI Assistant</router-link></li>
        <li class="mobile-only"><router-link to="/download" active-class="active-link">Download</router-link></li>
        <li class="mobile-only"><a href="/help.html">Help</a></li>
        <li class="mobile-only"><router-link to="/about" active-class="active-link">About</router-link></li>
      </ul>
    </nav>
    <nav class="site--header__right">
      <ul class="topNav-items right">
        <li>
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
        <li><router-link to="/download" active-class="active-link"><font-awesome-icon :icon="['fas', 'download']" title="Download" /></router-link></li>
        <li><a href="/help.html" title="Help"><font-awesome-icon :icon="['fas', 'book']" /></a></li>
        <li><router-link to="/about" active-class="active-link"><font-awesome-icon :icon="['fas', 'info-circle']" title="About" /></router-link></li>
      </ul>
    </nav>
  </header>
</template>




<script lang="ts">
import { computed, ref } from 'vue';
import { getThemeMode, nextThemeMode, setThemeMode } from '../utils/theme';

export default {
  name: 'NavBar',
  setup() {
    const themeMode = ref(getThemeMode());

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

    const toggleTheme = () => {
      const next = nextThemeMode(themeMode.value);
      themeMode.value = next;
      setThemeMode(next);
    };

    return { themeLabel, themeIcon, toggleTheme };
  }
}
</script>

<style>@media (max-width: 1100px) {
  .site--header {
    padding: 15px 20px; /* 为较小屏幕减少内边距 */
    flex-direction: column; /* 将徽标和菜单垂直堆叠 */
  }

  header.site--header {
    padding-top: 80px;
  }

  .site--header__center {
    position: static; /* 移除绝对定位 */
    transform: none;
    width: 100%; /* 全宽 */
    top: auto; /* 移除顶部定位 */
    box-shadow: none; /* 简化较小屏幕的样式 */
    border-radius: 0; /* 移除圆角 */
    padding: 0; /* 移除额外内边距 */
  }

  .topNav-items {
    justify-content: flex-start; /* 将项目对齐到开始位置 */
    overflow-x: auto; /* 允许较小屏幕上水平滚动 */
    white-space: nowrap; /* 防止换行 */
    overflow-y: hidden; /* 禁止垂直滚动 */
    padding-left: 20px;
    padding-right: 20px;
  }

  .topNav-items li {
    display: inline-block; /* 内联显示项目 */
    padding: 10px; /* 调整链接周围的内边距 */
  }

  .site--header__right {
    position: static;
    width: 100%;
    justify-content: flex-end;
    margin-top: 8px;
  }

  .topNav-items.right {
    justify-content: flex-end;
    padding: 0 20px 10px;
    overflow: visible;
    height: auto;
  }
}

@media (max-width: 1100px) {
  .topNav-items {
    padding-left: 40px;
    padding-right: 40px;
  }
}

.site--header {
  padding: 20px 80px;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-between; /* 确保空间分配 */
}

.site--url {
  align-items: center;
  font-size: 18px;
  font-weight: 700;
  text-decoration: none;
  color: inherit;
}

.site--url .avatar {
  margin-right: 10px;
  height: 64px; /* 调整高度 */
  width: 64px; /* 调整宽度 */
  border: 3px solid var(--farallon-background-white);
  border-radius: 50%; /* 完全圆形 */
  box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2); /* 增加阴影 */
  transition: .5s ease-in-out;
  overflow: hidden; /* 确保内容适应圆形 */
  background-color: var(--farallon-background-white); /* 背景色以防图像透明 */
  display: flex; /* 用于居中对齐 */
  align-items: center; /* 垂直居中对齐 */
  justify-content: center; /* 水平居中对齐 */
}

.site--url .avatar img {
  max-width: 100%; /* 最大宽度 */
  max-height: 100%; /* 最大高度 */
  object-fit: contain; /* 确保图像不变形 */
}

.site--header__center {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  height: 39px;
  top: 25px;
  z-index: 1;
  box-shadow: 0 0 0 1px var(--farallon-border-color-light),
    0 10px 15px -3px rgba(39, 39, 42, 0.08),
    0 4px 6px -4px rgba(39, 39, 42, 0.08);
  -webkit-backdrop-filter: blur(12px);
  backdrop-filter: blur(12px);
  background-color: rgba(255, 255, 255, 0.75);
  border: 1px solid var(--farallon-border-color-light);
  border-radius: 999rem;
  overflow: hidden;
}

.site--header__right {
  display: flex;
  align-items: center;
  justify-content: flex-end;
}

.topNav-items .mobile-only {
    display: inline-block; /* 显示移动端的导航链接 */
  }

.topNav-items {
  display: flex;
  align-items: center;
  height: 39px;
  box-sizing: border-box;
  padding: 5px 30px;
  margin: 0;
  list-style: none;
  overflow-x: auto; /* 允许水平滚动 */
  white-space: nowrap; /* 防止项目换行 */
  overflow-y: hidden; /* 禁止垂直滚动 */
}

.site--header__right {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  position: absolute;
  right: 0; /* 绝对定位到右边 */
  top: 25px; /* 调整顶部间距 */
}

@media (min-width: 1101px) {
  .topNav-items .mobile-only {
    display: none; /* 隐藏移动端的导航链接 */
  }
}

.topNav-items li {
  display: inline-block; /* 项目内联显示 */
  margin-right: 10px;
}

.topNav-items li a {
  color: var(--farallon-text-color); /* 默认颜色，未选中 */
  text-decoration: none; /* 移除下划线 */
}

.topNav-items li .active-link {
  color: var(--farallon-hover-color); /* 选中颜色 */
}

.topNav-items li {
  display: inline-block;
  margin-right: 10px;
  padding: 10px;
}

.topNav-items li a {
  color: var(--farallon-text-color);
  text-decoration: none;
  border-bottom: 2px solid transparent;
  transition: border-color 0.3s;
}

.topNav-items li a:hover {
  border-bottom: 2px solid var(--farallon-border-color);
}

.topNav-items li .active-link {
  color: var(--farallon-hover-color);
  border-bottom: 2px solid var(--farallon-hover-color);
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

</style>
