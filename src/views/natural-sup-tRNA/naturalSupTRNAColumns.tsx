import type { STableColumnsType } from '@shene/table';
import { ref } from 'vue';

export type DataType = { [key: string]: string };

export     const allColumns: STableColumnsType<DataType> = [
      { title: 'ID', dataIndex: 'id', width: 90, ellipsis: true, key: 'id', resizable: true },
      { title: 'Species', dataIndex: 'Species', width: 280, ellipsis: true, key: 'Species', resizable: true, sorter: true ,customRender: ({ text }) => <em>{text}</em>,},
      { title: 'Species ID', dataIndex: 'Species ID', width: 280, ellipsis: true, key: 'Species ID', resizable: true, sorter: true },
      { title: 'Tissue/Organelle of Origin', dataIndex: 'Tissue/Organelle of Origin', width: 280, ellipsis: true, key: 'Tissue/Organelle of Origin', resizable: true, sorter: true },
      { title: 'Anticodon before mutation', dataIndex: 'Anticodon before mutation', width: 180, ellipsis: true, key: 'Anticodon before mutation', resizable: true },
      { title: 'Anticodon after mutation', dataIndex: 'Anticodon after mutation', width: 180, ellipsis: true, key: 'Anticodon after mutation', resizable: true },
      {
        title: 'Stop codon for readthrough', dataIndex: 'Stop codon for readthrough', width: 240, ellipsis: true, key: 'Stop codon for readthrough', resizable: true,
        filter: {
          type: 'multiple',
          list: [
            { text: 'UAG(amber)', value: 'UAG(amber)' },
            { text: 'UAA(ochre)', value: 'UAA(ochre)' },
            { text: 'UGA(opal)', value: 'UGA(opal)' },
          ],
          onFilter: (value, record) => value.includes(record['Stop codon for readthrough']) || record['Stop codon for readthrough'].includes(value)
        }
      },
      {
        title: 'RNA central ID of tRNA', dataIndex: 'RNA central ID of tRNA', width: 250, ellipsis: true, key: 'RNA central ID of tRNA', resizable: true,

      },
      { title: 'Noncanonical charged amino acids', dataIndex: 'Noncanonical charged amino acids', width: 260, ellipsis: true, key: 'Noncanonical charged amino acids', resizable: true        
      ,filter: {
          type: 'multiple',
          list: [
            { text: 'Ser', value: 'Ser' },
            { text: 'Gln', value: 'Gln' },
            { text: 'Trp', value: 'Trp' },
            { text: 'Tyr', value: 'Tyr' },
            { text: 'Leu', value: 'Leu' },
            { text: 'Arg', value: 'Arg' },
            { text: 'Gly', value: 'Gly' },
            { text: 'Pro', value: 'Pro' },
            { text: 'Glu', value: 'Glu' },
            { text: 'Sec', value: 'Sec' },
            { text: 'Cys', value: 'Cys' },
            { text: 'Pyl', value: 'Pyl' },
          ],
          onFilter: (value, record) => value.includes(record['Noncanonical charged amino acids'])
        } },
      { title: 'tRNA sequence before mutation', dataIndex: 'tRNA sequence after mutation', width: 200, ellipsis: true, key: 'tRNA sequence after mutation', resizable: true },
      { title: 'tRNA sequence after mutation', dataIndex: 'tRNA sequence after mutation', width: 200, ellipsis: true, key: 'tRNA sequence after mutation', resizable: true },
      {
        title: 'Readthrough mechanism', dataIndex: 'Readthrough mechanism', width: 280, ellipsis: true, key: 'Readthrough mechanism', resizable: true, filter: {
          type: 'multiple',
          list: [
            { text: 'recode/reassignment', value: 'recode/reassignment ' },
            { text: 'wobble/misread/mispair/mismatch', value: 'wobble/misread/mispair/mismatch' },
            { text: 'mutations outside the anticodon', value: 'mutations outside the anticodon' },
            { text: 'other', value: 'other' },
            { text: 'mischarge', value: 'mischarge' },
            { text: 'mutations in the anticodon', value: 'mutations in the anticodon' }
          ],
          onFilter: (value, record) => {
            const mechanism = record['Readthrough mechanism'];
            return value.some(val => mechanism.includes(val));
          }
        }
      },
      { title: 'Mutational position of sup-tRNA', dataIndex: 'Mutational position of sup-tRNA', width: 250, ellipsis: true, key: 'Mutational position of sup-tRNA', resizable: true },
      { title: 'PMID of references', dataIndex: 'PMID of references', width: 150, ellipsis: true, key: 'PMID of references', customRender: ({ text, record }) => (<div><a href={'https://pubmed.ncbi.nlm.nih.gov/' + record['PMID of references'] || '#'} target="_blank" class="bracket-links">{record['PMID of references']}</a></div>), resizable: true },
      { title: 'Notes', dataIndex: 'Notes', width: 150, ellipsis: true, key: 'Notes', resizable: true }
    ];


export const selectedColumns = ref<string[]>(['Species', 'Stop codon for readthrough', 'Noncanonical charged amino acids', 'Readthrough mechanism']);
   
