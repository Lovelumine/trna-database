<template>
  <div class="site--main">
    <div class="help-container">
      <el-row>
        <el-col :span="6">
          <Sidebar :headings="headings" :files="files" :activeFile="activeFile" @navigateToHeading="navigateToHeading" @fileSelected="handleFileSelected" />
        </el-col>
        <el-col :span="18">
          <div v-html="content" class="markdown-body" @click="handleImageClick"></div>
        </el-col>
      </el-row>
    </div>
    <vue-easy-lightbox
      :visible="showViewer"
      :imgs="images"
      :index="currentIndex"
      @hide="showViewer = false"
    />
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';
import { useRoute } from 'vue-router';
import axios from 'axios';
import markdownIt from 'markdown-it';
import Sidebar from './sidebar.vue';
import VueEasyLightbox from 'vue-easy-lightbox';

const content = ref('');
const headings = ref([]);
const images = ref([]);
const currentIndex = ref(0);
const showViewer = ref(false);
const activeFile = ref('');
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
      id: match[2].toLowerCase().replace(/ /g, '-')
    };
  });

  images.value = [];
  const processedContent = markdownContent.replace(/!\[([^\]]*)\]\(([^)]+)\)/g, (match, alt, src) => {
    images.value.push(src);
    return `<img src="${src}" alt="${alt}" style="max-width: 100%; height: auto;" class="clickable-image" />`;
  });

  return processedContent;
};

const loadMarkdown = async (file) => {
  try {
    const response = await axios.get(`/src/views/help/docs/${file}`);
    const markdownContent = response.data;
    const processedContent = extractHeadings(markdownContent);
    content.value = md.render(processedContent);
  } catch (error) {
    console.error(`Failed to load markdown file: ${file}`, error);
  }
};

watch(() => route.query.file, (newFile) => {
  const file = newFile || '1-introduction.md';
  activeFile.value = file;
  loadMarkdown(file);
}, { immediate: true });

const handleFileSelected = (file) => {
  activeFile.value = file;
};

const handleImageClick = (event) => {
  if (event.target.tagName === 'IMG' && event.target.classList.contains('clickable-image')) {
    currentIndex.value = images.value.indexOf(event.target.src);
    showViewer.value = true;
  }
};

const navigateToHeading = (id) => {
  const element = document.getElementById(id);
  if (element) {
    element.scrollIntoView({ behavior: 'smooth' });
  }
};
</script>

<style scoped>
.site--main {
  display: flex;
  justify-content: center;
  padding: 20px;
  box-sizing: border-box;
  background-color: #f5f5f5;
}

.help-container {
  display: flex;
  max-width: 1200px;
  width: 100%;
  padding: 20px;
  box-sizing: border-box;
  background-color: #ffffff;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
}

.el-row {
  width: 100%;
}

.markdown-body {
  padding: 20px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  overflow-wrap: break-word;
  box-sizing: border-box;
}

.markdown-body img {
  max-width: 100%;
  height: auto;
  cursor: pointer;
}
</style>
