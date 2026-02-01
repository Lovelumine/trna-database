<template>
  <div class="site--main">
    <div class="home-container">
      <header class="hero">
        <div class="hero-main">
          <h1 class="hero-title">
            ENSURE: The Encyclopedia of Suppressor tRNA with an AI Assistant
            <span class="cite-inline">
              <button
                class="cite-button cite-button--hero"
                type="button"
                @click="openCitationModal"
                :aria-expanded="showCitationModal"
                aria-label="Full citation"
                title="Full citation"
              >
                Cite
              </button>
            </span>
          </h1>
          <p class="lead">
            A scholarly resource for suppressor tRNA research, integrating curated datasets, mechanistic insights,
            and an AI assistant to accelerate discovery.
          </p>
          <div class="cta-row">
            <a class="btn btn-primary" href="/expanded/ensure-0">Explore Structures</a>
            <a class="btn btn-ghost" href="/AIyingying">Ask the AI Assistant</a>
          </div>
        </div>
      </header>

      <section class="section">
        <div class="section-title">
          <h2>Figures</h2>
          <span class="section-line"></span>
        </div>
        <div class="figure-grid">
          <figure class="figure-card" style="--i: 1">
            <div class="image-card">
              <img
                :src="'https://minio.lumoxuan.cn/ensure/picture/structure.png'"
                @click="openLightbox(0)"
                class="centered-image"
                alt="Structure"
              >
            </div>
            <figcaption>Structural overview of suppressor tRNA.</figcaption>
          </figure>
          <figure class="figure-card" style="--i: 2">
            <div class="image-card">
              <img
                :src="'https://minio.lumoxuan.cn/ensure/picture/flowchart-ENSURE.png'"
                @click="openLightbox(1)"
                class="centered-image"
                alt="Flowchart ENSURE"
              >
            </div>
            <figcaption>Workflow and content organization of ENSURE.</figcaption>
          </figure>
        </div>
      </section>

      <section class="section plain-section">
        <p class="notice-title">Usage notice</p>
        <p class="notice-text">
          The ENSURE database is provided for academic and non-commercial research use only. Commercial use
          requires prior written permission from the authors and Sun Yat-sen University.
        </p>
      </section>

      <section class="section plain-section">
        <div class="section-title">
          <h2>Key Features</h2>
          <span class="section-line"></span>
        </div>

        <h3><a :href="geneticVariationUrl">Mutation-induced Disease Database</a></h3>
        <p>Explore coding variation in diseases and cancers, including missense, nonsense, and frameshift mutations, with potential sup-tRNA therapy applications.</p>

        <h3><a :href="naturalSupTRNACatalogUrl">Natural sup-tRNAs Catalog</a></h3>
        <p>Discover detailed information on natural sup-tRNAs, including their species of origin, sequences, and structures.</p>

        <h3><a :href="tRNATherapeuticsDataUrl">Engineered sup-tRNA Information</a></h3>
        <p>Access data on existing tRNA therapies, including targeted genes, mutation sites, sup-tRNA sequences, and therapy efficiency and safety.</p>

        <h3><a :href="tRNAIdentifyElementsUrl">tRNA Identify Elements</a></h3>
        <p>Understand key elements of tRNA molecules—sequences, structures, and modifications—that influence their function including interaction sites with AARS, EF-Tu and ribosome.</p>
      </section>

      <section class="section plain-section">
        <div class="section-title">
          <h2>Research Tools</h2>
          <span class="section-line"></span>
        </div>
        <ul class="tool-list">
          <li><strong><a href="/download">Data Download:</a></strong> Access downloadable datasets for further research.</li>
          <li><strong><a href="/expanded/ensure-0">Interactive Visualization:</a></strong> Explore tRNA structures and functions interactively.</li>
          <li><strong><a href="/AIyingying">AI Assistant:</a></strong> Get expert answers to your tRNA therapeutic questions from Yingying, our AI assistant built on the GPT-4o model.</li>
          <li><strong><a href="/blast">BLAST Functionality:</a></strong> Quickly find specific tRNA data using our advanced BLAST tools.</li>
        </ul>
      </section>

      <section class="section closing">
        <div class="section-title">
          <h2>Empowering tRNA Research</h2>
          <span class="section-line"></span>
        </div>
        <p>
          ENSURE is designed to accelerate the discovery and development of sup-tRNA. Our rich dataset, combined
          with AI-driven insights, makes ENSURE an invaluable resource for the tRNA research community.
        </p>
        <p class="closing-links">
          Get started: <a class="text-link" href="/download">download data</a> or
          <a class="text-link" href="/AIyingying">consult the AI assistant</a>.
        </p>
      </section>

      <div v-if="showCitationModal" class="cite-modal" role="dialog" aria-modal="true">
        <div class="cite-modal__backdrop" @click="closeCitationModal"></div>
        <div class="cite-modal__panel">
          <div class="cite-modal__header">
            <h3>Cite ENSURE</h3>
            <button class="cite-modal__close" type="button" @click="closeCitationModal" aria-label="Close">
              x
            </button>
          </div>
          <div class="cite-modal__formats">
            <button
              v-for="format in citationFormatOptions"
              :key="format"
              type="button"
              class="cite-format"
              :class="{ active: citationFormat === format }"
              @click="setCitationFormat(format)"
            >
              {{ format }}
            </button>
          </div>
          <div class="cite-modal__body">
            <pre class="cite-text">{{ currentCitation }}</pre>
          </div>
          <div class="cite-modal__actions">
            <button class="btn btn-ghost" type="button" @click="copyCitation">
              {{ citationCopied ? 'Copied' : 'Copy citation' }}
            </button>
          </div>
        </div>
      </div>

      <vue-easy-lightbox
        :visible="showViewer"
        :imgs="['https://minio.lumoxuan.cn/ensure/picture/structure.png', 'https://minio.lumoxuan.cn/ensure/picture/flowchart-ENSURE.png']"
        :index="currentIndex"
        @hide="showViewer = false"
      />
    </div>
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
      tRNAIdentifyElementsUrl: '/tRNAElements',
      citationCopied: false,
      showCitationModal: false,
      citationFormat: 'APA',
      citationFormatOptions: ['APA', 'MLA', 'Chicago', 'BibTeX', 'Plain'],
      citationFormats: {
        APA: 'Ouyang, Z., Zhang, Y., Feng, F., Zeng, X., Wu, Q., Hafeez, A., Teng, W., Kong, Y., Bu, X., Sun, Y., Li, B., Wen, Y., Lun, Z.-R., Qu, L., Feng, X., & Zheng, L. (2025). ENSURE: the encyclopedia of suppressor tRNA with an AI assistant. Nucleic Acids Research, gkaf1062. https://doi.org/10.1093/nar/gkaf1062',
        MLA: 'Ouyang, Zhuo, et al. \"ENSURE: the encyclopedia of suppressor tRNA with an AI assistant.\" Nucleic Acids Research, 2025, gkaf1062. https://doi.org/10.1093/nar/gkaf1062.',
        Chicago: 'Ouyang, Zhuo, Yifeng Zhang, Fan Feng, Xudong Zeng, Qiuhui Wu, Abdul Hafeez, Wenkai Teng, Yixin Kong, Xuan Bu, Yang Sun, Bin Li, Yanzi Wen, Zhao-Rong Lun, Lianghu Qu, Xiao Feng, and Lingling Zheng. \"ENSURE: the encyclopedia of suppressor tRNA with an AI assistant.\" Nucleic Acids Research (2025): gkaf1062. https://doi.org/10.1093/nar/gkaf1062.',
        BibTeX: '@article{Ouyang2025ENSURE,\\n  title = {ENSURE: the encyclopedia of suppressor tRNA with an AI assistant},\\n  author = {Ouyang, Zhuo and Zhang, Yifeng and Feng, Fan and Zeng, Xudong and Wu, Qiuhui and Hafeez, Abdul and Teng, Wenkai and Kong, Yixin and Bu, Xuan and Sun, Yang and Li, Bin and Wen, Yanzi and Lun, Zhao-Rong and Qu, Lianghu and Feng, Xiao and Zheng, Lingling},\\n  journal = {Nucleic Acids Research},\\n  year = {2025},\\n  pages = {gkaf1062},\\n  doi = {10.1093/nar/gkaf1062}\\n}',
        Plain: 'Zhuo Ouyang, Yifeng Zhang, Fan Feng, Xudong Zeng, Qiuhui Wu, Abdul Hafeez, Wenkai Teng, Yixin Kong, Xuan Bu, Yang Sun, Bin Li, Yanzi Wen, Zhao-Rong Lun, Lianghu Qu, Xiao Feng, Lingling Zheng, ENSURE: the encyclopedia of suppressor tRNA with an AI assistant, Nucleic Acids Research, 2025; gkaf1062, https://doi.org/10.1093/nar/gkaf1062'
      }
    };
  },
  computed: {
    currentCitation() {
      return this.citationFormats[this.citationFormat] || this.citationFormats.Plain;
    }
  },
  methods: {
    openLightbox(index) {
      this.currentIndex = index;
      this.showViewer = true;
    },
    openCitationModal() {
      this.showCitationModal = true;
    },
    closeCitationModal() {
      this.showCitationModal = false;
    },
    setCitationFormat(format) {
      this.citationFormat = format;
      this.citationCopied = false;
    },
    copyCitation() {
      const citation = this.currentCitation;
      navigator.clipboard?.writeText(citation).then(() => {
        this.citationCopied = true;
        setTimeout(() => {
          this.citationCopied = false;
        }, 1800);
      }).catch(() => {
        this.citationCopied = false;
      });
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
  --home-link: var(--link-inline);
  --home-link-hover: var(--link-inline-hover);
  --home-focus-ring: rgba(26, 115, 232, 0.25);
}

.home-container {
  display: flex;
  flex-direction: column;
  gap: 28px;
}

.hero {
  display: grid;
  grid-template-columns: 1fr;
  gap: 18px;
  align-items: start;
  padding: 12px 0 4px;
}

.kicker {
  text-transform: uppercase;
  letter-spacing: 0.18em;
  font-size: 0.78rem;
  color: var(--home-subtle);
  font-weight: 600;
}

.hero-title {
  font-size: clamp(2.2rem, 2rem + 1vw, 3rem);
  line-height: 1.2;
  margin: 12px 0 14px;
  color: var(--home-heading);
}

.cite-inline {
  display: inline-flex;
  align-items: center;
  margin-left: 4px;
  white-space: nowrap;
}

.lead {
  font-size: 1.02rem;
  line-height: 1.7;
  color: var(--home-body);
  max-width: 38rem;
}

.cta-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin: 12px 0 12px;
}

.btn {
  border-radius: 8px;
  padding: 7px 12px;
  font-size: 0.86rem;
  font-weight: 600;
  text-decoration: none;
  border: 1px solid transparent;
  transition: transform 160ms ease, box-shadow 160ms ease, background 160ms ease;
}

.btn-primary {
  background: var(--app-accent-strong);
  color: #ffffff;
  box-shadow: 0 6px 16px rgba(24, 50, 78, 0.2);
}

.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 10px 20px rgba(24, 50, 78, 0.24);
}

.btn-ghost {
  background: transparent;
  color: var(--app-accent-strong);
  border-color: rgba(43, 76, 111, 0.25);
}

.btn-ghost:hover {
  background: rgba(43, 76, 111, 0.08);
}

.notice-text {
  margin: 0;
  font-size: 0.92rem;
  color: var(--home-subtle);
}

.notice-title {
  margin: 0 0 4px;
  font-weight: 600;
  color: var(--home-heading);
}

.cite-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 999px;
  border: 1px solid transparent;
  background: #f97316;
  color: #ffffff;
  font-size: 0.75rem;
  font-weight: 700;
  padding: 4px 10px;
  cursor: pointer;
}

.cite-button:hover {
  background: #ea580c;
}

.cite-button--hero {
  font-size: 0.72rem;
  padding: 4px 10px;
  box-shadow: 0 6px 14px rgba(249, 115, 22, 0.24);
}

.citation-text {
  margin: 12px 0 0;
  line-height: 1.6;
  word-break: break-word;
  color: var(--home-body);
  font-size: 0.9rem;
}

.citation-actions {
  margin-top: 12px;
}

.cite-modal {
  position: fixed;
  inset: 0;
  z-index: 2000;
  display: flex;
  align-items: center;
  justify-content: center;
}

.cite-modal__backdrop {
  position: absolute;
  inset: 0;
  background: rgba(15, 23, 42, 0.45);
}

.cite-modal__panel {
  position: relative;
  width: min(720px, calc(100% - 32px));
  max-height: calc(100vh - 80px);
  overflow: auto;
  background: #ffffff;
  color: #0f172a;
  border: 1px solid var(--app-border);
  border-radius: 10px;
  padding: 18px;
  z-index: 1;
}

.cite-modal__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  border-bottom: 1px solid var(--app-border);
  padding-bottom: 10px;
  margin-bottom: 12px;
}

.cite-modal__header h3 {
  margin: 0;
  font-size: 1.1rem;
  color: var(--home-heading);
}

.cite-modal__close {
  border: none;
  background: transparent;
  font-size: 1.4rem;
  line-height: 1;
  cursor: pointer;
  color: var(--home-subtle);
}

.cite-modal__formats {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
}

.cite-format {
  border: 1px solid var(--app-border);
  background: transparent;
  padding: 6px 10px;
  border-radius: 6px;
  font-size: 0.85rem;
  cursor: pointer;
}

.cite-format.active {
  border-color: var(--app-accent-strong);
  color: var(--app-accent-strong);
  font-weight: 600;
}

.cite-modal__body {
  border: 1px solid var(--app-border);
  background: #f8fafc;
  padding: 10px;
  border-radius: 8px;
}

.cite-text {
  margin: 0;
  white-space: pre-wrap;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
  font-size: 0.88rem;
  color: #0f172a;
}

.cite-modal__actions {
  margin-top: 12px;
  display: flex;
  justify-content: flex-end;
}

@media (prefers-color-scheme: dark) {
  .cite-modal__panel {
    background: #0f172a;
    color: #e2e8f0;
    border-color: rgba(148, 163, 184, 0.25);
  }

  .cite-modal__header h3 {
    color: #f1f5f9;
  }

  .cite-modal__close {
    color: #cbd5f5;
  }

  .cite-format {
    border-color: rgba(148, 163, 184, 0.3);
    color: #e2e8f0;
  }

  .cite-modal__body {
    background: #111827;
    border-color: rgba(148, 163, 184, 0.25);
  }

  .cite-text {
    color: #e2e8f0;
  }
}

.section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 16px;
}

.section-title h2 {
  font-size: 1.6rem;
  margin: 0;
  color: var(--home-heading);
}

.section-line {
  flex: 1;
  height: 1px;
  background: linear-gradient(90deg, rgba(43, 76, 111, 0.28), transparent);
}

.figure-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 18px;
}

.figure-card {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.figure-card figcaption {
  font-size: 0.9rem;
  color: var(--home-subtle);
}

.image-card {
  height: 360px;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.centered-image {
  width: 100%;
  height: 100%;
  max-width: 720px;
  object-fit: contain;
  cursor: pointer;
}

.plain-section h2 {
  margin: 4px 0 6px;
  color: var(--home-heading);
}

.plain-section h3 {
  margin: 12px 0 6px;
  color: var(--home-heading);
}

.plain-section p {
  margin: 0 0 6px;
}

.tool-list {
  margin: 0;
  padding-left: 18px;
}

.tool-list li {
  margin-bottom: 8px;
}

.closing-links {
  margin: 6px 0 0;
}

.text-link {
  color: var(--home-link);
  text-decoration: none;
  font-weight: 600;
}

.text-link:hover {
  color: var(--home-link-hover);
  text-decoration: underline;
}

@media (max-width: 980px) {
  .hero {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 900px) {
  .image-card {
    height: 320px;
  }
}

@media (max-width: 640px) {
  .image-card {
    height: 260px;
  }
}
</style>
