<template>
    <el-menu :default-active="activeFile" class="el-menu-vertical-demo">
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
  .el-menu-vertical-demo {
    width: 100%;
  }
  </style>
  