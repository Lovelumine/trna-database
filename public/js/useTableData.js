import { ref, computed } from 'vue';
import Papa from 'papaparse';

export function useTableData(csvUrl) {
  const allData = ref([]);
  const searchText = ref('');

  const loadData = async () => {
    const response = await fetch(csvUrl);
    const csvData = await response.text();
    Papa.parse(csvData, {
      header: true,
      delimiter: ',',
      skipEmptyLines: true,
      dynamicTyping: true,
      complete: (results) => {
        allData.value = results.data.map((item, index) => ({
          key: index.toString(),
          ...item
        }));
      }
    });
  };

  const filteredDataSource = computed(() => {
    return allData.value.filter(item =>
      Object.keys(item).some(key =>
        String(item[key]).toLowerCase().includes(searchText.value.toLowerCase())
      )
    );
  });

  return {
    searchText,
    filteredDataSource,
    loadData
  };
}
