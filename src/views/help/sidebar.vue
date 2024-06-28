<template>
  <el-menu :default-active="activeFile" class="custom-menu">
    <el-menu-item
      v-for="file in files"
      :key="file.file"
      :index="file.file"
      @click="navigateToFile(file.file)"
    >
      {{ file.name }}
    </el-menu-item>
  </el-menu>
</template>

<script setup>
import { ref, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { defineProps } from 'vue';

const props = defineProps({
  files: {
    type: Array,
    required: true,
  },
});

const activeFile = ref('');
const router = useRouter();
const route = useRoute();

watch(() => route.query.file, (newFile) => {
  activeFile.value = newFile || '1-introduction.md';
}, { immediate: true });

const navigateToFile = (file) => {
  router.push({ path: '/help', query: { file } });
};
</script>

<style scoped>
.custom-menu {
  width: 100%;
  background-color: #f5f5f5; /* 调整背景颜色为更浅的色调 */
  color: #2c3e50; /* 字体颜色调整为深色以便对比 */
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}
.custom-menu .el-menu-item {
  font-size: 16px;
  color: #2c3e50; /* 字体颜色与背景颜色对比 */
}
.custom-menu .el-menu-item.is-active {
  background-color: #3498db; /* 活动项背景颜色 */
  color: #ffffff;
}
.custom-menu .el-menu-item:hover {
  background-color: #d3d3d3; /* 调整悬停背景颜色为更浅的色调 */
  color: #2c3e50;
}
</style>
