<template>
    <div class="site--main">
      <div class="download-page">
        <h1>Download Data Files</h1>
        <el-button type="primary" @click="downloadAllFiles" class="download-all-button">Download All</el-button>
        <el-progress :percentage="percentage" :stroke-width="15"  stroke-width="6px" :text-inside="true" :status="status" />
        <el-table :data="downloadData" class="animated-table" style="width: 100%; margin-top: 20px;">
          <el-table-column prop="category" label="Category" width="200"></el-table-column>
          <el-table-column label="Files">
            <template v-slot="scope">
              <el-link :href="scope.row.link" target="_blank">{{ scope.row.name }}</el-link>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
  </template>
  
  <script>
  import { ref } from 'vue';
  import JSZip from 'jszip';
  import { saveAs } from 'file-saver';
  import { ElMessage } from 'element-plus';
  import 'element-plus/dist/index.css';
  
  export default {
    setup() {
      const downloadData = ref([
        { category: 'Coding Variation Disease', name: 'Coding Variation in Cancer', link: '/src/data/Coding Variation in Cancer.csv' },
        { category: 'Coding Variation Disease', name: 'Coding Variation in Genetic Disease', link: '/src/data/Coding Variation in Genetic Disease.csv' },
        { category: 'Natural Sup-tRNA', name: 'Nonsense Sup-RNA', link: '/src/data/Nonsense Sup-RNA.csv' },
        { category: 'Natural Sup-tRNA', name: 'Frameshift sup-tRNA', link: '/src/data/Frameshift sup-tRNA.csv' },
        { category: 'tRNA Therapeutics', name: 'tRNAtherapeutics', link: '/src/data/tRNAtherapeutics.csv' },
        { category: 'tRNA elements', name: 'Function and Modification', link: '/src/data/Function and Modification.csv' },
        { category: 'tRNA elements', name: 'aaRS Recognition', link: '/src/data/aaRS Recognition.csv' }
      ]);
  
      const percentage = ref(0);
      const status = ref('');
  
      const downloadAllFiles = async () => {
        try {
          status.value = 'active';
          const zip = new JSZip();
          const promises = downloadData.value.map(async (file, index) => {
            const response = await fetch(file.link);
            const blob = await response.blob();
            zip.file(file.name, blob);
            percentage.value = ((index + 1) / downloadData.value.length) * 100; // 更新进度
          });
          await Promise.all(promises);
          percentage.value = 100; // 确保进度条走满
          const content = await zip.generateAsync({ type: 'blob' });
          saveAs(content, 'all_files.zip');
          ElMessage.success('Files downloaded successfully!');
          setTimeout(() => { // 延迟以确保用户能看到进度条满
            status.value = 'success';
          }, 500);
        } catch (error) {
          ElMessage.error('Error downloading files!');
          status.value = 'exception';
        }
      };
  
      return {
        downloadData,
        percentage,
        status,
        downloadAllFiles
      };
    }
  };
  </script>
  
  <style scoped>
  .download-page {
    padding: 20px;
  }
  
  .download-all-button {
    margin-bottom: 20px;
    animation: fadeIn 1s ease-in-out;
  }
  
  .animated-table {
    animation: fadeInUp 1s ease-in-out;
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
  </style>
  