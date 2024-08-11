//src/views/AIYingying/AISidebar.vue
<template>
  <div class="sidebar">
    <div class="sidebar-header">
      <div class="logo">
        <img src="https://framerusercontent.com/images/1w0lzT7QXS4SRJgD02kucFjmSL4.png" alt="logo" />
        <div class="title">AY-GLM 4.0</div>
      </div>
    </div>
    <div class="sidebar-menu">
      <div
        class="menu-item"
        v-for="item in menuItems"
        :key="item.id"
        :class="{ 'active': item.id === selectedMenuId }"
        @click="selectMenuItem(item.id)"
      >
        <font-awesome-icon :icon="item.icon" />
        <span>{{ item.text }}</span>
      </div>
    </div>
  </div>
</template>

<script>
import { library } from '@fortawesome/fontawesome-svg-core';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { faPenNib, faLightbulb, faLanguage, faBookOpen, faBookReader, faHistory } from '@fortawesome/free-solid-svg-icons';

library.add(faPenNib, faLightbulb, faLanguage, faBookOpen, faBookReader, faHistory);

export default {
  name: 'Sidebar',
  components: {
    FontAwesomeIcon
  },
  data() {
    return {
      menuItems: [
        { id: 1, text: 'Intelligent Document', icon: 'book-open' },
        { id: 6, text: 'Session History', icon: 'history' }
      ],
      selectedMenuId: 1 // 默认选中的菜单项 ID
    };
  },
  methods: {
    selectMenuItem(id) {
      this.selectedMenuId = id;
      this.$emit('menu-selected', id);
    }
  }
};
</script>

<style scoped>
.sidebar {
  width: 240px;
  height: calc(100vh - 80px); /* 顶部导航栏减去80px */
  background-color: #f4f7ff;
  display: flex;
  flex-direction: column;
  padding: 24px 10px;
  border-radius: 12px; /* 增加圆角 */
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); /* 添加阴影效果 */
}

.sidebar-header {
  display: flex;
  align-items: center;
  margin-bottom: 30px;
}

.logo {
  display: flex;
  align-items: center;
}

.logo img {
  width: 40px;
  height: 40px;
  margin-right: 10px;
}

.title {
  font-size: 22px;
  font-weight: 600;
  color: #2c3e50;
}

.sidebar-menu {
  display: flex;
  flex-direction: column;
  gap: 16px; /* 增加菜单项之间的间距 */
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 12px 20px; /* 调整菜单项的内边距 */
  font-size: 15px;
  font-weight: 500;
  color: #2c3e50;
  cursor: pointer;
  transition: background-color 0.3s, color 0.3s;
  border-radius: 8px; /* 增加圆角 */
}

.menu-item:hover,
.menu-item.active {
  background-color: #d0e2ff; /* 鼠标悬停和选中状态的背景色 */
  color: #007bff; /* 鼠标悬停和选中状态的字体颜色 */
}

.menu-item svg {
  width: 22px;
  height: 22px;
  margin-right: 12px;
}

/* 手机端适配 */
@media screen and (max-width: 768px) {
  .sidebar {
    width: 62px;
  }

  /* 隐藏文字 */
  .title {
    display: none;
  }

  .sidebar-menu .menu-item {
    padding: 10px 10px; /* 调整菜单项的内边距 */
  }

  .sidebar-menu .menu-item>span {
    display: none;
  }
}

</style>
