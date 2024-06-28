<template>
  <el-menu
    :default-active="activeFile + '-sub'"
    class="custom-menu"
    :default-openeds="defaultOpeneds"
    collapse-transition
  >
    <template v-for="file in files" :key="file.file">
      <el-menu-item
        v-if="file.file !== activeFile"
        :index="file.file"
        @click="handleFileClick(file.file)"
      >
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
          @click="handleHeadingClick(heading.id)"
          :class="{ 'is-activated': heading.id === activeHeading }"
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
    default: '',
  },
  activeHeading: {
    type: String,
    default: '',
  },
});

const emits = defineEmits(['navigateToHeading', 'fileSelected']);

const router = useRouter();
const route = useRoute();

const defaultOpeneds = ref([]);

// 初始化 defaultOpeneds，确保菜单默认展开
watch(
  () => props.files,
  (newFiles) => {
    defaultOpeneds.value = newFiles.map((file) => file.file + '-sub');
    console.log('Default openeds initialized:', defaultOpeneds.value);
  },
  { immediate: true }
);

const handleFileClick = (file) => {
  console.log('File clicked:', file);
  emits('fileSelected', file);
  router.push({ path: '/help', query: { file } });
};

const handleHeadingClick = (id) => {
  console.log('Heading clicked:', id);
  emits('navigateToHeading', id);

};

</script>

<style>
.custom-menu {
  width: 100%;
  background-color: #f5f5f5;
  color: #2c3e50;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.custom-menu .el-menu-item,
.custom-menu .el-sub-menu__title {
  font-size: 14px;
  color: #2c3e50;
  white-space: normal !important; /* 确保文本自动换行 */
  word-break: break-word !important; /* 防止长单词溢出 */
  overflow-wrap: break-word !important; /* 处理长单词或URL */
  line-height: 1.5 !important; /* 确保行高正常 */
  padding-left: 20px !important; /* 增加内边距 */
}

.custom-menu .el-menu-item.is-activated,
.custom-menu .el-sub-menu__title.is-activated,
.custom-menu .el-menu-item.is-activated:hover,
.custom-menu .el-sub-menu__title.is-activated:hover {
  background-color: #3498db !important;
  color: #ffffff !important;
}

.custom-menu .el-menu-item:hover,
.custom-menu .el-sub-menu__title:hover {
  background-color: #d3d3d3;
  color: #2c3e50;
}

.custom-menu .el-menu-item {
  padding: 10px 20px !important; /* 设置一级标题的内边距 */
  text-align: left !important; /* 一级标题左对齐 */
}

.el-sub-menu .el-menu-item {
  height: auto !important; /* 自动调整高度 */
  line-height: 1.5 !important; /* 设置行高 */
  padding: 10px 20px !important; /* 设置内边距 */
  text-align: left !important; /* 二级标题左对齐 */
}

::v-deep .el-sub-menu__title {
  background-color: #3498db;
  color: #ffffff;
}

@media (max-width: 768px) {
  .custom-menu {
    font-size: 12px; /* 调整字体大小 */
  }

  .custom-menu .el-menu-item,
  .custom-menu .el-sub-menu__title {
    padding: 8px 15px !important; /* 调整内边距 */
  }
}
</style>
