import { STableColumnsType } from "@shene/table";
import { ref } from "vue";
export type DataType = { [key: string]: string };

export  const allColumns: STableColumnsType<DataType> = [
      { title: 'ID', dataIndex: 'id', width: 90, ellipsis: true, key: 'id', resizable: true },
      { title: 'Modification Type', dataIndex: 'Modification_Type', width: 140, ellipsis: true, key: 'Modification_Type', resizable: true },
      { title: 'Modomics CODE', dataIndex: 'Modomics_CODE', width: 140, ellipsis: true, key: 'Modomics_CODE', resizable: true },
      { title: 'Modification site', dataIndex: 'Modification_site', width: 500, ellipsis: true, key: 'Modification_site', resizable: true },
      { title: 'tRNA TYPE', dataIndex: 'tRNA_TYPE', width: 500, ellipsis: true, key: 'tRNA_TYPE', resizable: true },
      { title: 'Function of Modification', dataIndex: 'Function_of_Modification', width: 560, ellipsis: true, key: 'Function_of_Modification', resizable: true },
      { title: 'species', dataIndex: 'species', width: 200, ellipsis: true, key: 'species', resizable: true, customRender: ({ text, record }) => (<span className="latin-name">{record.species}</span>)},
      { title: 'tissue or cell line', dataIndex: 'tissue_or_cell_line', width: 240, ellipsis: true, key: 'tissue_or_cell_line', resizable: true },
      { title: 'condition', dataIndex: 'condition', width: 200, ellipsis: true, key: 'condition', resizable: true },      
      {
        title: 'PMID', width: 112, ellipsis: true, key: 'PMID', dataIndex: 'PMID',
        customRender: ({ text, record }) => (<div><a href={'https://pubmed.ncbi.nlm.nih.gov/' + record.PMID || '#'} target="_blank" class="bracket-links">{record.PMID}</a></div>),
        resizable: true
      }
    ];

export const selectedColumns = ref<string[]>([
      'Modification_Type',
      'Function_of_Modification',
      'tissue_or_cell_line',
      'PMID'
    ]);
