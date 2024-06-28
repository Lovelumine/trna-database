<template>
  <el-menu :default-active="activeFile" class="custom-menu">
    <template v-for="file in files" :key="file.file">
      <el-menu-item :index="file.file" @click="navigateToFile(file.file)">
        {{ file.name }}
      </el-menu-item>
      <el-sub-menu v-if="file.file === activeFile" :index="file.file + '-sub'">
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
});

const emits = defineEmits(['navigateToHeading']);

const activeFile = ref('');
const router = useRouter();
const route = useRoute();

watch(
  () => route.query.file,
  (newFile) => {
    activeFile.value = newFile || '1-introduction.md';
  },
  { immediate: true }
);

const navigateToFile = (file) => {
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
  font-size: 16px;
  color: #2c3e50;
}
.custom-menu .el-menu-item.is-active {
  background-color: #3498db;
  color: #ffffff;
}
.custom-menu .el-menu-item:hover {
  background-color: #d3d3d3;
  color: #2c3e50;
}
</style>
