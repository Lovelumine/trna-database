import { ref, computed } from 'vue';
import Papa from 'papaparse';

export function useTableData(csvUrl) {
  const allData = ref([]);
  const searchText = ref('');
  const isLoading = ref(false);
  const error = ref(null);

  const loadData = async () => {
    isLoading.value = true;
    error.value = null;
    try {
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
          isLoading.value = false;
        }
      });
    } catch (err) {
      error.value = err;
      isLoading.value = false;
    }
  };

  const filteredDataSource = computed(() => {
    if (!searchText.value) return allData.value;
    return allData.value.filter(item =>
      Object.keys(item).some(key =>
        item[key] != null &&
        item[key].toString().toLowerCase().includes(searchText.value.toLowerCase())
      )
    );
  });

  return {
    searchText,
    filteredDataSource,
    loadData,
    isLoading,
    error
  };
}
