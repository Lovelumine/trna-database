<template>
  <div class="site--main">
    <div class="help-container">
      <div class="help-title">
        <h1>Help & Documentation</h1>
        <p>Your guide to navigating and understanding our resources</p>
      </div>
      <el-row>
        <el-col :span="6">
          <div class="sidebar-container">
            <Sidebar
              :headings="headings"
              :files="files"
              :activeFile="activeFile"
              :activeHeading="activeHeading"
              @navigateToHeading="navigateToHeading"
              @fileSelected="handleFileSelected"
            />
          </div>
        </el-col>
        <el-col :span="18">
          <!-- 只保留这一处 v-html，同时让 v-loading 在同一个元素上控制“加载中”遮罩 -->
          <div
            class="markdown-body"
            v-loading="loading"
            element-loading-text="加载中..."
            @click="handleImageClick"
            v-html="content"
          >
          </div>
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
  <!-- 删除: 原来放在这里的 <div id="bottom"></div> 已移动到 markdown-body 内  -->
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted, nextTick } from 'vue';
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
const activeHeading = ref('');
const loading = ref(false);
const route = useRoute();

const md = markdownIt({
  html: true,
  linkify: true,
  typographer: true,
}).use(md => {
  const defaultRender = md.renderer.rules.heading_open || function(tokens, idx, options, env, self) {
    return self.renderToken(tokens, idx, options);
  };

  md.renderer.rules.heading_open = function(tokens, idx, options, env, self) {
    const token = tokens[idx];
    const headingId = tokens[idx + 1].content.toLowerCase().replace(/[^\w]+/g, '-');
    token.attrs = token.attrs || [];
    token.attrs.push(['id', headingId]);
    return defaultRender(tokens, idx, options, env, self);
  };
});

const files = [
  { name: 'Introduction', file: '1-introduction.md' },
  { name: 'Genetic Disorders', file: '2-Coding Variation Disease.md' },
  { name: 'Natural sup-tRNA', file: '3-Natural Sup-tRNA.md' },
  { name: 'Engineered sup-tRNA', file: '4-Engineered Sup-tRNA.md' },
  { name: 'Modification with Function', file: '5-Modification with Function.md' }
];

const extractHeadings = (markdownContent) => {
  const headingLines = markdownContent.split('\n').filter(line => line.match(/^#{1,6}\s/));
  headings.value = headingLines.map(line => {
    const match = line.match(/^(#{1,6})\s+(.*)/);
    return {
      level: match[1].length,
      text: match[2],
      id: match[2].toLowerCase().replace(/[^\w]+/g, '-')
    };
  });

  images.value = [];
  const processedContent = markdownContent.replace(/!\[([^\]]*)\]\(([^)]+)\)/g, (match, alt, src) => {
    images.value.push(src);
    return `<img data-src="${src}" alt="${alt}" style="max-width: 100%; height: auto;" class="clickable-image lazy-load" />`;
  });

  return processedContent;
};

const loadMarkdown = async (file) => {
  try {
    loading.value = true;
    content.value = '';
    const encoded = encodeURIComponent(file);
    const response = await axios.get(`/docs/${encoded}`);
    const markdownContent = response.data;
    const processedContent = extractHeadings(markdownContent);

    // 把锚点注入到渲染后的 HTML 里
    content.value = md.render(processedContent) + '<div id="bottom"></div>';
    await nextTick();
    initLazyLoad();

    // 如果 URL 带了 #bottom，就滚到这个锚点
    const hash = window.location.hash; // 直接用原生的 hash
    if (hash === '#bottom') {
      const bottomEl = document.getElementById('bottom');
      if (bottomEl) {
        // 滚到锚点，并把它对齐到视口底部
        bottomEl.scrollIntoView({ behavior: 'smooth', block: 'end' });
      }
    }

    loading.value = false;
  } catch (error) {
    console.error(`Failed to load markdown file: ${file}`, error);
    loading.value = false;
  }
};

const initLazyLoad = () => {
  const lazyImages = document.querySelectorAll('.lazy-load');
  const imageObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const img = entry.target;
        img.src = img.dataset.src;
        img.classList.remove('lazy-load');
        observer.unobserve(img);
      }
    });
  });

  lazyImages.forEach(image => {
    imageObserver.observe(image);
  });

  // Preload remaining images
  lazyImages.forEach(img => {
    const src = img.dataset.src;
    const image = new Image();
    image.src = src;
    image.onload = () => {
      img.src = src;
      img.classList.remove('lazy-load');
    };
  });
};

// 简单节流函数
const throttle = (func, delay) => {
  let lastCall = 0;
  return (...args) => {
    const now = new Date().getTime();
    if (now - lastCall < delay) {
      return;
    }
    lastCall = now;
    return func(...args);
  };
};

const onScroll = throttle(() => {
  const headingElements = headings.value.map(heading => document.getElementById(heading.id));
  const scrollPosition = window.scrollY;
  for (let i = 0; i < headingElements.length; i++) {
    const current = headingElements[i];
    const next = headingElements[i + 1];
    if (current && (!next || next.offsetTop > scrollPosition)) {
      activeHeading.value = headings.value[i].id;
      console.log('Active heading on scroll:', activeHeading.value);
      break;
    }
  }
}, 100); // 限制滚动事件的调用频率

watch(activeHeading, (newHeading) => {
  console.log('Active heading changed:', newHeading);
});

watch(() => route.query.file, async (newFile) => {
  const file = newFile || '1-introduction.md';
  console.log('Route query changed, new file:', file);
  activeFile.value = file;
  headings.value = []; // 清空headings
  await loadMarkdown(file); // 加载新的文件并更新headings
}, { immediate: true });

watch(content, async () => {
  // 等 v-html 真正插入完
  await nextTick();
  if (route.hash === '#bottom') {
    const bottomEl = document.getElementById('bottom');
    if (bottomEl) {
      bottomEl.scrollIntoView({ behavior: 'smooth' });
    }
  }
});

onMounted(() => {
  window.addEventListener('scroll', onScroll);
});

onUnmounted(() => {
  window.removeEventListener('scroll', onScroll);
});

const handleFileSelected = (file) => {
  console.log('File selected:', file);
  activeFile.value = file;
};

const handleImageClick = (event) => {
  if (event.target.tagName === 'IMG' && event.target.classList.contains('clickable-image')) {
    console.log('Image clicked:', event.target.src);
    currentIndex.value = images.value.indexOf(event.target.src);
    showViewer.value = true;
  }
};

const navigateToHeading = (id) => {
  console.log('Navigating to heading:', id);
  const element = document.getElementById(id);
  if (element) {
    console.log('Element found, scrolling into view:', element);
    const yOffset = -10; // 可根据需要调整偏移量
    const y = element.getBoundingClientRect().top + window.pageYOffset + yOffset;
    window.scrollTo({ top: y, behavior: 'smooth' });
  } else {
    console.warn('Element not found:', id);
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
  flex-direction: column;
  align-items: center;
  max-width: 1200px;
  width: 100%;
  padding: 20px;
  box-sizing: border-box;
  background-color: #ffffff;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
}

.help-title {
  text-align: center;
  margin-bottom: 20px;
}

.help-title h1 {
  font-size: 2em;
  color: #2c3e50;
  margin: 0;
}

.help-title p {
  font-size: 1em;
  color: #7f8c8d;
  margin: 0;
}

.el-row {
  width: 100%;
}

.sidebar-container {
  position: sticky;
  top: 20px; /* 调整此值以设置边栏的顶部偏移 */
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

.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.5s;
}

.fade-enter, .fade-leave-to /* .fade-leave-active in <2.1.8 */ {
  opacity: 0;
}
</style>
