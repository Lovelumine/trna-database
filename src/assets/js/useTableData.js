import { ref, computed } from 'vue';
import Papa from 'papaparse';

export function useTableData(csvUrl) {
  const allData = ref([]);
  const searchText = ref('');
  const searchColumn = ref(''); // 新增搜索列的引用
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
    return allData.value.filter(item => {
      if (searchColumn.value && item[searchColumn.value] != null) {
        return item[searchColumn.value].toString().toLowerCase().includes(searchText.value.toLowerCase());
      }
      return Object.keys(item).some(key =>
        item[key] != null &&
        item[key].toString().toLowerCase().includes(searchText.value.toLowerCase())
      );
    });
  });

  return {
    searchText,
    searchColumn, // 返回搜索列引用
    filteredDataSource,
    loadData,
    isLoading,
    error
  };
}
