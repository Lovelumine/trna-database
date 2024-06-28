<template>
    <div class="site--main">
      <div class="help-container">
        <el-row>
          <el-col :span="6">
            <Sidebar :headings="headings" :files="files" />
          </el-col>
          <el-col :span="18">
            <div v-html="content" class="markdown-body"></div>
          </el-col>
        </el-row>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, watch } from 'vue';
  import { useRoute } from 'vue-router';
  import axios from 'axios';
  import markdownIt from 'markdown-it';
  import Sidebar from './sidebar.vue';
  
  const content = ref('');
  const headings = ref([]);
  const route = useRoute();
  
  const md = markdownIt({
    html: true,
    linkify: true,
    typographer: true,
  });
  
  const files = [
    { name: 'Introduction', file: '1-introduction.md' },
    { name: 'Coding Variation Disease', file: '2-Coding Variation Disease.md' },
    { name: 'Natural Sup-tRNA', file: '3-Natural Sup-tRNA.md' },
    { name: 'tRNA Therapeutics', file: '4-tRNA Therapeutics.md' },
    { name: 'Modification with Function', file: '5-Modification with Function.md' }
  ];
  
  const extractHeadings = (markdownContent) => {
    const headingLines = markdownContent.split('\n').filter(line => line.match(/^#{1,6}\s/));
    headings.value = headingLines.map(line => {
      const match = line.match(/^(#{1,6})\s+(.*)/);
      return {
        level: match[1].length,
        text: match[2],
      };
    });
  };
  
  const loadMarkdown = async (file) => {
    try {
      const response = await axios.get(`/src/views/help/docs/${file}`);
      const markdownContent = response.data;
      extractHeadings(markdownContent);
      content.value = md.render(markdownContent);
    } catch (error) {
      console.error(`Failed to load markdown file: ${file}`, error);
    }
  };
  
  // 监听路由变化，加载对应的 Markdown 文件
  watch(() => route.query.file, (newFile) => {
    const file = newFile || '1-introduction.md';
    loadMarkdown(file);
  }, { immediate: true });
  </script>
  
  <style scoped>
  .site--main {
    display: flex;
    justify-content: center;
    padding: 20px;
    box-sizing: border-box;
  }
  
  .help-container {
    display: flex;
    max-width: 1000px; /* 更严格的最大宽度 */
    width: 100%;
    padding: 20px;
    box-sizing: border-box;
  }
  
  .el-row {
    width: 100%; /* 确保 el-row 使用 100% 的宽度 */
  }
  
  .markdown-body {
    padding: 20px;
    background-color: #fff;
    border-radius: 8px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
    overflow-wrap: break-word; /* 防止内容超出 */
    box-sizing: border-box;
  }
  </style>
  