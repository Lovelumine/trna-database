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
        title: 'AARS',
        ellipsis: true,
        dataIndex: 'aaRS',
        resizable: true,
        key: 'aaRS',
        width: 120,
        fixed: true,
        align: 'center'
      },
      {
        title: 'Identity Element Location',
        key: 'IdentityElementLocation',
        align: 'center',
        ellipsis: true,
        resizable: true,
        children: [
          {
            title: 'Acceptor stem',
            dataIndex: 'AcceptorStem',
            key: 'AcceptorStem',
            resizable: true,
            ellipsis: true,
            width: 200,
            align: 'center'
          },
          {
            title: 'Anticodon arm',
            dataIndex: 'AnticodonArm',
            ellipsis: true,
            resizable: true,
            key: 'AnticodonArm',
            width: 200,
            align: 'center'
          },
          {
            title: 'Other location',
            dataIndex: 'OtherLocation',
            resizable: true,
            ellipsis: true,
            key: 'OtherLocation',
            width: 160,
            align: 'center'
          },
          {
            title: 'Other domains (d-arm/T-arm/variable arm)',
            dataIndex: 'OtherDomains',
            key: 'OtherDomains',
            resizable: true,
            ellipsis: true,
            width: 300,
            align: 'center'
          }
        ]
      },
      {
        title: 'Reference/PMID',
        dataIndex: 'Reference',
        key: 'Reference',
        resizable: true,
        width: 200,
        align: 'center',
        ellipsis: true,
        customRender: ({ text, record }) => {
          const reference = String(record.Reference); // 确保 Reference 是字符串类型
          if (isPMID(reference)) {
            return (
              <div>
                {reference.split(',').map((pmid, index, array) => (
                  <span key={pmid}>
                    <a href={`https://pubmed.ncbi.nlm.nih.gov/${pmid.trim()}`} target="_blank" class="bracket-links">{pmid.trim()}</a>
                    {index < array.length - 1 && ','}
                  </span>
                ))}
              </div>
            );
          } else {
            return <div>{reference}</div>;
          }
        }
      }
    ];


export const selectedColumns = ref<string[]>([
      'aaRS',
      'AcceptorStem',
      'AnticodonArm',
      'OtherLocation',
      'OtherDomains',
      'Reference'
    ]);
