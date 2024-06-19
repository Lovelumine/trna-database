// processCSVData.js

export const processCSVData = (data, fieldsToProcess) => {
  return data.map(item => {
    fieldsToProcess.forEach(field => {
      if (typeof item[field] === 'string') {
        console.log(`Processing field: ${field}, value: ${item[field]}`);
        item[field] = parseCSVField(item[field]);
        console.log(`Processed field: ${field}, result: ${item[field]}`);
      }
    });
    return item;
  });
};

// 解析单个CSV字段，处理包含引号和逗号的情况
const parseCSVField = (field) => {
  const result = [];
  let current = '';
  let insideQuotes = false;

  console.log(`Parsing field: ${field}`);

  for (let i = 0; i < field.length; i++) {
    const char = field[i];
    console.log(`Character: ${char}, insideQuotes: ${insideQuotes}`);

    if (char === '"') {
      insideQuotes = !insideQuotes;
      console.log(`Quote detected. insideQuotes toggled to: ${insideQuotes}`);
    } else if (char === ',' && !insideQuotes) {
      console.log(`Comma found at index ${i}, current: "${current}"`);
      result.push(current.trim());
      current = '';
    } else {
      current += char;
    }
  }

  if (current.length > 0) {
    result.push(current.trim());
  }

  console.log(`Final result: ${JSON.stringify(result)}`);
  return result.map(str => str.replace(/^"|"$/g, '').trim());
};
