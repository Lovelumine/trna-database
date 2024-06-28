<template>
  <el-menu :default-active="activeFile + '-sub'" class="custom-menu">
    <template v-for="file in files" :key="file.file">
      <el-menu-item 
        v-if="file.file !== activeFile" 
        :index="file.file" 
        @click="handleFileClick(file.file)">
        {{ file.name }}
      </el-menu-item>
      <el-sub-menu v-else :index="file.file + '-sub'">
        <template #title>
          <span>{{ file.name }}</span>
        </template>
        <el-menu-item
          v-for="heading in headings"
          :key="heading.id"
          :index="heading.id"
          @click="navigateToHeading(heading.id)"
        >
          {{ heading.text }}
        </el-menu-item>
      </el-sub-menu>
    </template>
  </el-menu>
</template>

<script setup>
import { ref, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { defineProps, defineEmits } from 'vue';
import 'element-plus/theme-chalk/el-menu.css';
import 'element-plus/theme-chalk/el-sub-menu.css';

const props = defineProps({
  files: {
    type: Array,
    required: true,
  },
  headings: {
    type: Array,
    required: true,
  },
  activeFile: {
    type: String,
    default: ''
  }
});

const emits = defineEmits(['navigateToHeading', 'fileSelected']);

const router = useRouter();
const route = useRoute();

const handleFileClick = (file) => {
  emits('fileSelected', file);
  router.push({ path: '/help', query: { file } });
};

const navigateToHeading = (id) => {
  emits('navigateToHeading', id);
};
</script>

<style scoped>
.custom-menu {
  width: 100%;
  background-color: #f5f5f5;
  color: #2c3e50;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}
.custom-menu .el-menu-item {
  font-size: 14px;
  color: #2c3e50;
  white-space: normal; /* 确保文本自动换行 */
  word-break: break-word; /* 防止长单词溢出 */
}
.custom-menu .el-sub-menu__title {
  white-space: normal; /* 确保文本自动换行 */
  word-break: break-word; /* 防止长单词溢出 */
}
.custom-menu .el-menu-item.is-active,
.custom-menu .el-sub-menu__title.is-active {
  background-color: #3498db;
  color: #ffffff;
}
.custom-menu .el-menu-item:hover,
.custom-menu .el-sub-menu__title:hover {
  background-color: #d3d3d3;
  color: #2c3e50;
}

::v-deep .el-sub-menu__title {
  background-color: #3498db;
  color: #ffffff;
}
</style>
