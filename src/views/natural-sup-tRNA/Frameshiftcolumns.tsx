import type { STableColumnsType } from '@shene/table';
import { ref } from 'vue';

export type DataType = { [key: string]: string };

export const allColumns: STableColumnsType<DataType> = [
      { title: 'Species', dataIndex: 'Species', width: 180, ellipsis: true, key: 'Species', resizable: true, sorter: true },
      { title: 'Species ID', dataIndex: 'Species ID', width: 280, ellipsis: true, key: 'Species ID', resizable: true, sorter: true },
      { title: 'Anticodon before mutation', dataIndex: 'Anticodon before mutation', width: 180, ellipsis: true, key: 'Anticodon before mutation', resizable: true },
      { title: 'Anticodon after mutation', dataIndex: 'Anticodon after mutation', width: 180, ellipsis: true, key: 'Anticodon after mutation', resizable: true },
      {
        title: 'Codon for readthrough', dataIndex: 'Codon for readthrough', width: 180, ellipsis: true, key: 'Codon for readthrough', resizable: true
      },
      {
        title: 'Noncanonical charged amino acids', dataIndex: 'Noncanonical charged amino acids', width: 260, ellipsis: true, key: 'Noncanonical charged amino acids', resizable: true,
        filter: {
          type: 'multiple',
          list: [
            { text: 'Val', value: 'Val' },
            { text: 'Gln', value: 'Gln' },
            { text: 'Lys', value: 'Lys' },
            { text: 'Pro', value: 'Pro' },
            { text: 'Gly', value: 'Gly' },
            { text: 'Thr', value: 'Thr' },
          ],
          onFilter: (value, record) => value.includes(record['Noncanonical charged amino acids']) || record['Noncanonical charged amino acids'].includes(value)
        }
      },
      { title: 'tRNA sequence before mutation', dataIndex: 'tRNA sequence before mutation', width: 200, ellipsis: true, key: 'tRNA sequence before mutation', resizable: true },
      { title: 'tRNA sequence after mutation', dataIndex: 'tRNA sequence after mutation', width: 200, ellipsis: true, key: 'tRNA sequence after mutation', resizable: true },
      {
        title: 'Readthrough mechanism', dataIndex: 'Readthrough mechanism', width: 260, ellipsis: true, key: 'Readthrough mechanism', resizable: true, filter: {
          type: 'multiple',
          list: [
            { text: 'mutations in the anticodon', value: 'mutations in the anticodon' },
            { text: 'tRNA hopping', value: 'tRNA hopping' },
            { text: 'quadruple pairing', value: 'quadruple pairing' },
            { text: 'mutations outside the anticodon', value: 'mutations outside the anticodon' },
          ],
    onFilter: (value, record) => {
      const mechanism = record['Readthrough mechanism'];
      return value.some(val => mechanism.includes(val));
    }}
      },
      { title: 'Mutational position of sup-tRNA', dataIndex: 'Mutational position of sup-tRNA', width: 250, ellipsis: true, key: 'Mutational position of sup-tRNA', resizable: true },
      { title: 'PMID of references', 
  dataIndex: 'PMID of references', 
  key: 'PMID of references', 
  resizable: true,
  width: 250, 
  align: 'center',
  ellipsis: true, 
  customRender: ({ text, record }) => {
    const reference = String(record['PMID of references']); // 确保 Reference 是字符串类型
    return (
        <div>
            {reference.split('、').map((pmid, index, array) => (
                <span key={pmid.trim()}>
                    <a href={`https://pubmed.ncbi.nlm.nih.gov/${pmid.trim()}`} target="_blank" class="bracket-links">{pmid.trim()}</a>
                    {index < array.length - 1 && '、'}
                </span>
            ))}
        </div>
    );
}}
];


export const selectedColumns = ref<string[]>(['Species', 'Codon for readthrough', 'Anticodon after mutation', 'Codon for readthrough', 'Noncanonical charged amino acids', 'Readthrough mechanism']);
   