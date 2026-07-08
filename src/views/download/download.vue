<template>
  <div class="site--main">
    <div class="download-page">
      <div class="download-header">
        <h1>Download Data Files</h1>
        <div class="download-actions">
          <el-select v-model="format" class="format-select" placeholder="Format">
            <el-option label="CSV" value="csv" />
            <el-option label="TSV" value="tsv" />
          </el-select>
          <el-button type="primary" @click="downloadAllFiles" class="download-all-button">Download All</el-button>
        </div>
      </div>
      <el-progress :percentage="percentage" :stroke-width="15" stroke-width="6px" :text-inside="true" :status="status" />
      <el-table :data="downloadData" class="animated-table" style="width: 100%; margin-top: 20px;">
        <el-table-column prop="category" label="Category" width="200"></el-table-column>
        <el-table-column label="Files">
          <template v-slot="scope">
            <el-link href="#" @click.prevent="downloadFile(scope.row)">{{ scope.row.name }}</el-link>
          </template>
        </el-table-column>
        <el-table-column label="Download">
          <template v-slot="scope">
            <el-button type="primary" @click="downloadFile(scope.row)">Download</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="download-card-list" aria-label="Download files">
        <article v-for="file in downloadData" :key="file.table" class="download-card">
          <div class="download-card__content">
            <span class="download-card__category">{{ file.category }}</span>
            <button class="download-card__name" type="button" @click="downloadFile(file)">
              {{ file.name }}
            </button>
          </div>
          <el-button type="primary" class="download-card__button" @click="downloadFile(file)">
            Download
          </el-button>
        </article>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue';
import { ElMessage } from 'element-plus';
import 'element-plus/dist/index.css';

export default {
  setup() {
    const downloadData = ref([
      { category: 'Mutation-induced Disease', name: 'Coding Variation in Cancer', table: 'coding_variation_cancer' },
      { category: 'Mutation-induced Disease', name: 'Coding Variation in Disease', table: 'coding_variation_genetic_disease' },
      { category: 'Natural sup-tRNA', name: 'Nonsense Sup-RNA', table: 'nonsense_sup_rna' },
      { category: 'Natural sup-tRNA', name: 'Frameshift sup-tRNA', table: 'frameshift_sup_trna' },
      { category: 'Engineered sup-tRNA', name: 'Engineered sup-tRNA', table: 'Engineered_sup_tRNA' },
      { category: 'tRNA elements', name: 'Function of Modification', table: 'function_and_modification' },
      { category: 'tRNA elements', name: 'aaRS Recognition', table: 'aars_recognition' },
      { category: 'tRNA elements', name: 'EF-Tu recognition site', table: 'ef_tu' }
    ]);

    const percentage = ref(0);
    const status = ref('');
    const format = ref('csv');

    const getStatusUrl = (file) => {
      const params = new URLSearchParams({
        table: file.table,
        format: format.value
      });
      return `/download_table_status?${params.toString()}`;
    };

    const getBundleStatusUrl = () => {
      const params = new URLSearchParams({ format: format.value });
      return `/download_bundle_status?${params.toString()}`;
    };

    const pollForReady = async (statusUrl, onReady) => {
      const maxTries = 200;
      for (let attempt = 0; attempt < maxTries; attempt += 1) {
        const response = await fetch(statusUrl);
        if (!response.ok) {
          throw new Error(await response.text());
        }
        const data = await response.json();
        if (typeof data.progress === 'number') {
          percentage.value = data.progress;
        }
        if (data.status === 'ready' && data.url) {
          onReady(data.url);
          return;
        }
        await new Promise(resolve => setTimeout(resolve, 1500));
      }
      throw new Error('Export is taking longer than expected. Please try again later.');
    };

    const downloadAllFiles = async () => {
      try {
        status.value = 'active';
        percentage.value = 0;
        await pollForReady(getBundleStatusUrl(), (url) => {
          window.location.href = url;
        });
        percentage.value = 100;
        status.value = 'success';
      } catch (error) {
        ElMessage.error('Error downloading files!');
        status.value = 'exception';
      }
    };

    const downloadFile = async (file) => {
      try {
        status.value = 'active';
        percentage.value = 0;
        await pollForReady(getStatusUrl(file), (url) => {
          window.location.href = url;
        });
        percentage.value = 100;
        status.value = 'success';
      } catch (error) {
        ElMessage.error(`Error downloading ${file.name}!`);
        status.value = 'exception';
      }
    };

    return {
      downloadData,
      percentage,
      status,
      format,
      getStatusUrl,
      getBundleStatusUrl,
      downloadAllFiles,
      downloadFile
    };
  }
};
</script>

<style scoped>
.download-page {
  padding: 20px;
}

.download-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
}

.download-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.format-select {
  min-width: 120px;
}

.download-all-button {
  margin-bottom: 0;
  animation: fadeIn 1s ease-in-out;
}

.animated-table {
  animation: fadeInUp 1s ease-in-out;
}

.download-card-list {
  display: none;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 640px) {
  .download-page {
    padding: 8px 0 20px;
  }

  .download-header {
    align-items: flex-start;
    gap: 10px;
    margin-bottom: 12px;
  }

  .download-header h1 {
    font-size: clamp(2.05rem, 9.5vw, 2.35rem);
    line-height: 1.08;
    margin: 0;
  }

  .download-actions {
    width: 100%;
    align-items: stretch;
    gap: 8px;
    padding: 8px;
    border: 1px solid var(--app-border-light);
    border-radius: 8px;
    background: var(--app-surface);
  }

  .format-select {
    flex: 1 1 0;
    min-width: 0;
  }

  .download-all-button {
    flex: 1 1 0;
    min-width: 0;
  }

  .format-select :deep(.el-select__wrapper),
  .download-all-button {
    min-height: 40px;
  }

  :deep(.el-progress) {
    margin-top: 8px;
  }

  .animated-table {
    display: none;
  }

  .download-card-list {
    display: grid;
    gap: 10px;
    margin-top: 16px;
  }

  .download-card {
    display: grid;
    grid-template-columns: minmax(0, 1fr) auto;
    align-items: center;
    gap: 10px;
    padding: 12px;
    border: 1px solid var(--app-border);
    border-radius: 8px;
    background: var(--farallon-background-white);
    box-shadow: 0 8px 18px rgba(15, 23, 42, 0.06);
  }

  .download-card__content {
    display: grid;
    gap: 4px;
    min-width: 0;
  }

  .download-card__category {
    color: var(--app-text-faint);
    font-size: 0.82rem;
    line-height: 1.35;
  }

  .download-card__name {
    appearance: none;
    padding: 0;
    border: 0;
    background: transparent;
    color: var(--link-inline);
    font: inherit;
    font-weight: 600;
    line-height: 1.4;
    text-align: left;
    overflow-wrap: anywhere;
  }

  .download-card__button {
    width: auto;
    min-width: 104px;
    min-height: 38px;
    padding: 0 12px;
  }

  @media (max-width: 420px) {
    .download-card {
      grid-template-columns: minmax(0, 1fr);
      gap: 10px;
    }

    .download-card__button {
      width: 100%;
      min-height: 36px;
    }
  }
}
</style>
