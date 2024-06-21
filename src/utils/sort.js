export function sortData(data, sorter) {
    if (!sorter || !sorter.field || !sorter.order) {
      return data;
    }
  
    return data.concat().sort((a, b) => {
      if (sorter.field === 'Species') {
        return sorter.order === 'descend' 
          ? b[sorter.field].localeCompare(a[sorter.field])
          : a[sorter.field].localeCompare(b[sorter.field]);
      }
      return sorter.order === 'descend' 
        ? b[sorter.field] - a[sorter.field]
        : a[sorter.field] - b[sorter.field];
    });
  }
  