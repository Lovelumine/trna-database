<template>
  <div class="site--main">
    <div class="ensure-banner">
      <p class="ensure-disclaimer">
        ⚠️ The ENSURE database is provided for academic and non-commercial research use only.
        Commercial use requires prior written permission from the authors and Sun Yat-sen University.
      </p>
    </div>

    <h1>Welcome to ENSURE: The Encyclopedia of Suppressor tRNA with an AI Assistant</h1>
    <p>Welcome to ENSURE! Our platform offers extensive data and tools to advance the field of sup-tRNA.</p>

    <h2>How to Cite</h2>
    <div class="citation-card citation-card--fold" tabindex="0" title="Hover to expand">
      <p class="citation-hint">
        If you use ENSURE in your research, please cite:
        <span class="citation-expand-indicator">Hover to expand</span>
      </p>
      <p class="citation-text">
        Zhuo Ouyang, Yifeng Zhang, Fan Feng, Xudong Zeng, Qiuhui Wu, Abdul Hafeez, Wenkai Teng, Yixin Kong, Xuan Bu,
        Yang Sun, Bin Li, Yanzi Wen, Zhao-Rong Lun, Lianghu Qu, Xiao Feng, Lingling Zheng, ENSURE: the encyclopedia of
        suppressor tRNA with an AI assistant, <i>Nucleic Acids Research</i>, 2025; gkaf1062,
        <a href="https://doi.org/10.1093/nar/gkaf1062" target="_blank" rel="noopener noreferrer">
          https://doi.org/10.1093/nar/gkaf1062
        </a>
      </p>
    </div>
    
    <div class="image-container">
      <div class="image-card">
        <img :src="'https://minio.lumoxuan.cn/ensure/picture/structure.png'" @click="openLightbox(0)" class="centered-image" alt="Structure">
      </div>
    </div>
    
    <div class="image-container">
      <div class="image-card">
        <img :src="'https://minio.lumoxuan.cn/ensure/picture/flowchart-ENSURE.png'" @click="openLightbox(1)" class="centered-image" alt="Flowchart ENSURE">
      </div>
    </div>
    
    <h2>Key Features</h2>
    
    <h3><a :href="geneticVariationUrl">Mutation-induced Disease Database</a></h3>
    <p>Explore conding variation in diseases and cancers, including missense, nonsense, and frameshift mutations, with potential sup-tRNA therapy applications.</p>
    
    <h3><a :href="naturalSupTRNACatalogUrl">Natural sup-tRNAs Catalog</a></h3>
    <p>Discover detailed information on natural sup-tRNAs, including their species of origin, sequences, and structures.</p>
    
    <h3><a :href="tRNATherapeuticsDataUrl">Engineered sup-tRNA Information</a></h3>
    <p>Access data on existing tRNA therapies, including targeted genes, mutation sites, sup-tRNA sequences, and therapy efficiency and safety.</p>
    
    <h3><a :href="tRNAIdentifyElementsUrl">tRNA Identify Elements</a></h3>
    <p>Understand key elements of tRNA molecules—sequences, structures, and modifications—that influence their function including interaction sites with AARS, EF-Tu and ribosome.</p>
    
    <h2>Research Tools</h2>
<ul>
  <li><strong><a href="/download">Data Download:</a></strong> Access downloadable datasets for further research.</li>
  <li><strong><a href="/expanded/ensure-0">Interactive Visualization:</a></strong> Explore tRNA structures and functions interactively.</li>
  <li><strong><a href="/AIyingying">AI Assistant:</a></strong> Get expert answers to your tRNA therapeutic questions from Yingying, our AI assistant built on the GPT-4o model.</li>
  <li><strong><a href="/blast">BLAST Functionality:</a></strong> Quickly find specific tRNA data using our advanced BLAST tools.</li>
</ul>
    
    <h2>Empowering tRNA Research</h2>
    <p>ENSURE is designed to accelerate the discovery and development of sup-tRNA. Our rich dataset, combined with AI-driven insights, makes ENSURE an invaluable resource for the tRNA research community.</p>
    
    <vue-easy-lightbox
      :visible="showViewer"
      :imgs="['https://minio.lumoxuan.cn/ensure/picture/structure.png', 'https://minio.lumoxuan.cn/ensure/picture/flowchart-ENSURE.png']"
      :index="currentIndex"
      @hide="showViewer = false"
    />
  </div>
</template>

<script>
import VueEasyLightbox from 'vue-easy-lightbox';

export default {
  name: 'Home',
  components: {
    VueEasyLightbox
  },
  data() {
    return {
      showViewer: false,
      currentIndex: 0,
      geneticVariationUrl: '/CodingVariationDisease',
      naturalSupTRNACatalogUrl: '/naturalsuptRNA',
      tRNATherapeuticsDataUrl: '/tRNAtherapeutics',
      tRNAIdentifyElementsUrl: '/tRNAElements'
    };
  },
  methods: {
    openLightbox(index) {
      this.currentIndex = index;
      this.showViewer = true;
    }
  }
}
</script>

<style scoped>
.site--main {
  padding: 20px;
  color: var(--home-body);
  --home-heading: var(--app-text);
  --home-body: var(--app-text-muted);
  --home-subtle: var(--app-text-faint);
  --home-banner-bg: #fff3cd;
  --home-banner-border: #ffc107;
  --home-banner-text: #856404;
  --home-card-bg: #f6f8fa;
  --home-card-border: #1a73e8;
  --home-card-outline: rgba(15, 23, 42, 0.12);
  --home-card-shadow: 0 12px 28px rgba(15, 23, 42, 0.08);
  --home-image-bg: #f8fafc;
  --home-image-border: rgba(15, 23, 42, 0.12);
  --home-image-shadow: 0 20px 40px rgba(15, 23, 42, 0.14);
  --home-link: #1a73e8;
  --home-link-hover: #1558c0;
  --home-focus-ring: rgba(26, 115, 232, 0.25);
}

/* 顶部免责声明横幅 */
.ensure-banner {
  background-color: var(--home-banner-bg);
  border-left: 6px solid var(--home-banner-border);
  padding: 12px 18px;
  margin-bottom: 18px;
  border-radius: 4px;
}

.ensure-disclaimer {
  margin: 0;
  font-size: 14px;
  color: var(--home-banner-text);
  font-weight: 600;
  line-height: 1.5;
}

.image-container {
  display: flex;
  justify-content: center;
  margin: 20px 0;
}

.image-card {
  background: var(--home-image-bg);
  border: 1px solid var(--home-image-border);
  border-radius: 14px;
  padding: 16px;
  box-shadow: var(--home-image-shadow);
  max-width: 100%;
}

.centered-image {
  width: 800px;
  max-width: 100%;
  height: auto;
  object-fit: contain;
  border-radius: 10px;
  cursor: pointer;
}

h1, h2, h3 {
  color: var(--home-heading);
}

p, ul {
  color: var(--home-body);
}

a {
  color: var(--home-link);
  text-decoration: none;
}

a:hover {
  color: var(--home-link-hover);
  text-decoration: underline;
}

.citation-card {
  background: var(--home-card-bg);
  border: 1px solid var(--home-card-outline);
  border-left: 6px solid var(--home-card-border);
  border-radius: 4px;
  padding: 14px 18px;
  margin: 14px 0 26px;
  box-shadow: var(--home-card-shadow);
}

.citation-hint {
  margin: 0 0 8px;
  font-weight: 600;
  display: flex;
  gap: 10px;
  align-items: baseline;
  justify-content: space-between;
  color: var(--home-heading);
}

.citation-text {
  margin: 0;
  line-height: 1.6;
  word-break: break-word;
  color: var(--home-body);
}

.citation-card--fold {
  cursor: pointer;
  outline: none;
  position: relative;
}

.citation-card--fold:focus-visible {
  box-shadow: 0 0 0 3px var(--home-focus-ring);
}

.citation-expand-indicator {
  font-size: 12px;
  font-weight: 500;
  color: var(--home-subtle);
  white-space: nowrap;
}

.citation-card--fold::after {
  content: "▾";
  position: absolute;
  right: 14px;
  top: 14px;
  color: var(--home-link);
  transition: transform 180ms ease;
  pointer-events: none;
}

.citation-card--fold .citation-text {
  max-height: 0;
  opacity: 0;
  overflow: hidden;
  transition: max-height 180ms ease, opacity 180ms ease;
}

.citation-card--fold:hover .citation-text,
.citation-card--fold:focus-within .citation-text {
  max-height: 260px;
  opacity: 1;
}

.citation-card--fold:hover::after,
.citation-card--fold:focus-within::after {
  transform: rotate(-180deg);
}

@media (hover: none) {
  .citation-card--fold .citation-text {
    max-height: none;
    opacity: 1;
  }

  .citation-expand-indicator {
    display: none;
  }

  .citation-card--fold::after {
    display: none;
  }
}

@media (prefers-color-scheme: dark) {
  .site--main {
    --home-heading: rgba(242, 244, 248, 0.96);
    --home-body: rgba(231, 233, 239, 0.78);
    --home-subtle: rgba(231, 233, 239, 0.6);
    --home-banner-bg: #2a2112;
    --home-banner-border: #d2a347;
    --home-banner-text: rgba(248, 231, 181, 0.95);
    --home-card-bg: #141a24;
    --home-card-border: rgba(126, 165, 255, 0.75);
    --home-card-outline: rgba(226, 232, 240, 0.14);
    --home-card-shadow: 0 18px 36px rgba(3, 7, 18, 0.45);
    --home-image-bg: #111827;
    --home-image-border: rgba(148, 163, 184, 0.24);
    --home-image-shadow: 0 24px 48px rgba(2, 6, 23, 0.6);
    --home-link: #8ab4ff;
    --home-link-hover: #b7d1ff;
    --home-focus-ring: rgba(138, 180, 255, 0.35);
  }

  .ensure-banner {
    background-color: #2a2112;
    border-left-color: #d2a347;
  }

  .ensure-disclaimer {
    color: rgba(248, 231, 181, 0.95);
  }

  .citation-card {
    background: #141a24;
    border-color: rgba(226, 232, 240, 0.14);
    border-left-color: rgba(126, 165, 255, 0.75);
    box-shadow: 0 18px 36px rgba(3, 7, 18, 0.45);
  }

  .image-card {
    background: #111827;
    border-color: rgba(148, 163, 184, 0.24);
    box-shadow: 0 24px 48px rgba(2, 6, 23, 0.6);
  }
}

:global(:root[data-theme="dark"]) .site--main {
  --home-heading: rgba(242, 244, 248, 0.96);
  --home-body: rgba(231, 233, 239, 0.78);
  --home-subtle: rgba(231, 233, 239, 0.6);
  --home-banner-bg: #2a2112;
  --home-banner-border: #d2a347;
  --home-banner-text: rgba(248, 231, 181, 0.95);
  --home-card-bg: #141a24;
  --home-card-border: rgba(126, 165, 255, 0.75);
  --home-card-outline: rgba(226, 232, 240, 0.14);
  --home-card-shadow: 0 18px 36px rgba(3, 7, 18, 0.45);
  --home-image-bg: #111827;
  --home-image-border: rgba(148, 163, 184, 0.24);
  --home-image-shadow: 0 24px 48px rgba(2, 6, 23, 0.6);
  --home-link: #8ab4ff;
  --home-link-hover: #b7d1ff;
  --home-focus-ring: rgba(138, 180, 255, 0.35);
}

:global(:root[data-theme="dark"]) .ensure-banner {
  background-color: #2a2112;
  border-left-color: #d2a347;
}

:global(:root[data-theme="dark"]) .ensure-disclaimer {
  color: rgba(248, 231, 181, 0.95);
}

:global(:root[data-theme="dark"]) .citation-card {
  background: #141a24;
  border-color: rgba(226, 232, 240, 0.14);
  border-left-color: rgba(126, 165, 255, 0.75);
  box-shadow: 0 18px 36px rgba(3, 7, 18, 0.45);
}

:global(:root[data-theme="dark"]) .image-card {
  background: #111827;
  border-color: rgba(148, 163, 184, 0.24);
  box-shadow: 0 24px 48px rgba(2, 6, 23, 0.6);
}
</style>
