import { STableColumnsType } from "@shene/table";
import { ref } from "vue";
export type DataType = { [key: string]: string };

// 判断是否为PMID格式
export function isPMID(reference) {
  // 将输入转换为字符串再进行判断
  const referenceStr = String(reference);
  return /^\d+(,\s*\d+)*$/.test(referenceStr);
}

export const allColumns: STableColumnsType<DataType> = [
      {
        title: 'tRNA families',
        ellipsis: true,
        dataIndex: 'tRNA families',
        resizable: true,
        key: 'tRNA families',
        width: 120,
        fixed: true,
        align: 'center'
      },
      {
        title: 'Acceptor branch',
        dataIndex: 'Acceptor branch',
        key: 'Acceptor branch',
        resizable: true,
        width: 250,
        align: 'center',
        ellipsis: true
      },
      {
        title: 'Core region',
        dataIndex: 'Core region',
        key: 'Core region',
        resizable: true,
        width: 250,
        align: 'center',
        ellipsis: true
      },
      {
        title: 'Anticodon branch',
        dataIndex: 'Anticodon branch',
        key: 'Anticodon branch',
        resizable: true,
        width: 250,
        align: 'center',
        ellipsis: true
      },
      {
        title: 'Modification elements',
        dataIndex: 'Modification elements',
        key: 'Modification elements',
        resizable: true,
        width: 250,
        align: 'center',
        ellipsis: true
      },
    ];


export const selectedColumns = ref<string[]>([
        'tRNA families',
      'Acceptor branch',
        'Core region',
        'Anticodon branch',
        'Modification elements',

    ]);
