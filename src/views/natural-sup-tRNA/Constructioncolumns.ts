import type { STableColumnsType } from '@shene/table';

export type DataType = { [key: string]: string };

export const allColumns: STableColumnsType<DataType> = [
      { title: 'Species', dataIndex: 'Species', width: 150, ellipsis: true, key: 'Species', resizable: true },
      { title: 'Anticodon before mutation', dataIndex: 'Anticodon before mutation', width: 180, ellipsis: true, key: 'Anticodon before mutation', resizable: true },
      { title: 'Anticodon after mutation', dataIndex: 'Anticodon after mutation', width: 180, ellipsis: true, key: 'Anticodon after mutation', resizable: true },
      { title: 'Stop codon for readthrough', dataIndex: 'Stop codon for readthrough', width: 180, ellipsis: true, key: 'Stop codon for readthrough', resizable: true },
      { title: 'Noncanonical charged amino acids', dataIndex: 'Noncanonical charged amino acids', width: 150, ellipsis: true, key: 'Noncanonical charged amino acids', resizable: true },
      { title: 'tRNA sequence before mutation', dataIndex: 'tRNA sequence before mutation', width: 200, ellipsis: true, key: 'tRNA sequence before mutation', resizable: true },
      { title: 'tRNA sequence after mutation', dataIndex: 'tRNA sequence after mutation', width: 200, ellipsis: true, key: 'tRNA sequence after mutation', resizable: true },
      { title: 'Structure of sup-tRNA', dataIndex: 'Structure of sup-tRNA', width: 150, ellipsis: true, key: 'Structure of sup-tRNA', resizable: true },
      { title: 'Readthrough mechanism', dataIndex: 'Readthrough mechanism', width: 200, ellipsis: true, key: 'Readthrough mechanism', resizable: true },
      { title: 'Mutational position of sup-tRNA', dataIndex: 'Mutational position of sup-tRNA', width: 250, ellipsis: true, key: 'Mutational position of sup-tRNA', resizable: true },
      { title: 'PMID of references', dataIndex: 'PMID of references', width: 150, ellipsis: true, key: 'PMID of references', resizable: true }
    ];
