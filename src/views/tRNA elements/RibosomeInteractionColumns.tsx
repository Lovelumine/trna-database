import type { STableColumnsType } from '@shene/table';
import { ref } from 'vue';

export type RowType = { [key: string]: string };

// 默认显示的列
export const selectedColumns = ref<string[]>([
  'site', 'subsite','tRNA region', 'trna_pos', 'ribo_pos'
]);

// 列定义（dataIndex 必须与 CSV 表头一致；若你的 CSV 表头不同，请把 dataIndex 改成对应名字）
export const allColumns: STableColumnsType<RowType> = [
  {
    title: 'Site',
    dataIndex: 'site',
    key: 'site',
    width: 120,
    ellipsis: true,
    resizable: true,
    filter: {
      type: 'multiple',
      list: [
        { text: 'A site', value: 'A site' },
        { text: 'P site', value: 'P site' },
        { text: 'E site', value: 'E site' }
      ],
      onFilter: (value, record) => value.includes(record['site'])
    }
  },
    {
    title: 'subsite',
    dataIndex: 'subsite',
    key: 'subsite',
    width: 100,
    ellipsis: true,
    resizable: true
  },
  {
    title: 'tRNA Region',
    dataIndex: 'tRNA region',
    key: 'tRNA region',
    width: 440,
    ellipsis: true,
    resizable: true
  },
  {
    title: 'tRNA Positions',
    dataIndex: 'tRNA positions',
    key: 'trna_pos',
    width: 240,
    ellipsis: true,
    resizable: true
  },
  {
    title: 'Ribosome Positions',
    dataIndex: 'Ribosome positions',
    key: 'ribo_pos',
    width: 240,
    ellipsis: true,
    resizable: true
  }
];