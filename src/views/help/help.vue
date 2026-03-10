<template>
  <div class="help-page-shell">
    <div class="help-page">
      <header class="help-header">
        <div class="help-header__copy">
          <h1>Help</h1>
        </div>
      </header>

      <div class="help-layout">
        <aside class="sidebar-container">
          <Sidebar
            :headings="headings"
            :files="files"
            :activeFile="activeFile"
            :activeHeading="activeHeading"
            @navigateToHeading="navigateToHeading"
            @fileSelected="handleFileSelected"
          />
        </aside>

        <section class="help-content">
          <div
            class="markdown-body"
            v-loading="loading"
            element-loading-text="加载中..."
            @click="handleImageClick"
            v-html="content"
          >
          </div>
        </section>
      </div>
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
  { name: 'Mutation-induced Disease', file: '2-Coding Variation Disease.md' },
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

    content.value = md.render(processedContent) + '<div id="bottom"></div>';
    await nextTick();
    initLazyLoad();

    const hash = window.location.hash;
    if (hash === '#bottom') {
      const bottomEl = document.getElementById('bottom');
      if (bottomEl) {
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
      break;
    }
  }
}, 100);

watch(() => route.query.file, async (newFile) => {
  const file = newFile || '1-introduction.md';
  activeFile.value = file;
  headings.value = [];
  await loadMarkdown(file);
}, { immediate: true });

watch(content, async () => {
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
    const yOffset = -10;
    const y = element.getBoundingClientRect().top + window.pageYOffset + yOffset;
    window.scrollTo({ top: y, behavior: 'smooth' });
  }
};
</script>

<style scoped>
.help-page-shell {
  display: block;
  padding: 10px 18px 40px;
  box-sizing: border-box;
  background-color: var(--farallon-background-gray);
}

.help-page {
  width: min(1980px, 100%);
  margin: 0 auto;
}

.help-header {
  padding: 10px 0 18px;
}

.help-header__copy {
  display: block;
}

.help-header__copy h1 {
  margin: 0;
}

.help-header__copy h1 {
  color: var(--farallon-text-color);
  font-size: clamp(2rem, 2.6vw, 2.85rem);
  line-height: 1.08;
}

.help-layout {
  display: grid;
  grid-template-columns: clamp(240px, 18vw, 300px) minmax(0, 1fr);
  gap: 44px;
  align-items: start;
  padding-top: 8px;
}

.sidebar-container {
  position: sticky;
  top: 18px;
  align-self: start;
  max-height: calc(100vh - 32px);
  overflow: auto;
}

.help-content {
  min-width: 0;
}

.markdown-body {
  padding: 0 0 56px;
  background: transparent;
  color: var(--farallon-text-color);
  overflow-wrap: break-word;
  box-sizing: border-box;
  box-shadow: none;
  border: none;
  border-radius: 0;
  min-height: 60vh;
}

.markdown-body :deep(h1),
.markdown-body :deep(h2),
.markdown-body :deep(h3),
.markdown-body :deep(h4),
.markdown-body :deep(h5),
.markdown-body :deep(h6) {
  color: var(--farallon-text-color);
  scroll-margin-top: 18px;
}

.markdown-body :deep(h1) {
  font-size: clamp(2.15rem, 2.6vw, 3rem);
  margin: 0 0 1.1rem;
}

.markdown-body :deep(h2) {
  font-size: clamp(1.6rem, 2vw, 2.15rem);
  margin-top: 2.4rem;
}

.markdown-body :deep(p),
.markdown-body :deep(li) {
  color: var(--farallon-text-color);
  font-size: 1.13rem;
  line-height: 1.95;
}

.markdown-body :deep(ul),
.markdown-body :deep(ol) {
  padding-left: 1.5rem;
}

.markdown-body :deep(a) {
  color: var(--link-primary);
}

.markdown-body :deep(blockquote) {
  margin: 1.5rem 0;
  padding: 0.2rem 0 0.2rem 1rem;
  border-left: 3px solid rgba(37, 99, 235, 0.32);
  color: var(--farallon-text-light);
}

.markdown-body img {
  max-width: min(100%, 1200px);
  height: auto;
  cursor: pointer;
  display: block;
  margin: 1.8rem auto;
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

@media (max-width: 1200px) {
  .help-page-shell {
    padding-inline: 20px;
  }

  .help-layout {
    grid-template-columns: 260px minmax(0, 1fr);
    gap: 28px;
  }
}

@media (max-width: 768px) {
  .help-page-shell {
    padding: 12px 14px 28px;
  }

  .help-header {
    padding: 2px 0 14px;
  }

  .help-layout {
    grid-template-columns: 1fr;
    gap: 20px;
    padding-top: 20px;
  }

  .sidebar-container {
    position: static;
    max-height: none;
    overflow: visible;
  }

  .markdown-body {
    padding: 4px 0 28px;
    min-height: auto;
  }

  .markdown-body :deep(p),
  .markdown-body :deep(li) {
    font-size: 1rem;
    line-height: 1.78;
  }
}
</style>
