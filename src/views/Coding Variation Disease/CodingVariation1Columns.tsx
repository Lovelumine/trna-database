import { STableColumnsType } from "@shene/table";
import { ref } from "vue";
export type DataType = { [key: string]: string };

export         const selectedColumns = ref<string[]>([
      'mutationType',
      'diseaseName',
      'gene',
      'Protein Alteration',
      'Codon Change',

  ])
 export   const allColumns: STableColumnsType<DataType> = [
      {
        title: 'Mutation Type',
        dataIndex: 'mutationType',
        width: 140, ellipsis: true,
        key: 'mutationType',
        resizable: true,
        filter: {
          type: 'multiple',
          list: [
            { text: 'Missense', value: 'Missense' },
            { text: 'Nonsense', value: 'Nonsense' },
            {text:'Frameshift',value:'Frameshift'}
          ],
          onFilter: (value, record) => value.includes(record.mutationType)
        }
      },
      { title: 'Disease Name', dataIndex: 'diseaseName', width: 360, ellipsis: true, key: 'diseaseName', resizable: true },
      { title: 'Phenotype MIM Number', dataIndex: 'Phenotype', width: 200, ellipsis: true, key: 'Phenotype', resizable: true },
      { title: 'GenBank Accession Number', dataIndex: 'GenBank Accession Number', width: 200, ellipsis: true, key: 'GenBank Accession Number', resizable: true },
      { title: 'Gene', dataIndex: 'gene', width: 120, ellipsis: true, key: 'gene', resizable: true },
      { title: 'Gene/Locus MIM Number', dataIndex: 'Locus', width: 200, ellipsis: true, key: 'Locus', resizable: true },
      { title: 'Mutation Site', dataIndex: 'mutationSite', width: 120, ellipsis: true, key: 'mutationSite', resizable: true },
      { title: 'Protein Alteration', dataIndex: 'Protein Alteration', width: 240, ellipsis: true, key: 'Protein Alteration', resizable: true },
      { title: 'Codon Change', dataIndex: 'Codon Change', width: 240, ellipsis: true, key: 'Codon Change', resizable: true },
      { title: 'Chromosome', dataIndex: 'chromosome', width: 120, ellipsis: true, key: 'chromosome', resizable: true },
      { title: 'Genome Position', dataIndex: 'Genomeposition', width: 220, ellipsis: true, key: 'Genomeposition', resizable: true },
      {
        title: 'De Novo / Inherited',
        dataIndex: 'denovoinherited',
        width: 180, ellipsis: true,
        key: 'denovoinherited',
        resizable: true,
        filter: {
          type: 'multiple',
          list: [
            { text: 'de novo', value: 'de novo' },
            { text: 'inherited', value: 'inherited' },
            { text: 'de novo / inherited', value: 'de novo / inherited' },
            { text: 'uncertain', value: 'uncertain' },
          ],
          onFilter: (value, record) => value.includes(record.denovoinherited)
        }
      },
      { title: 'Zygosity', dataIndex: 'zygosity', width: 140, ellipsis: true, key: 'zygosity', resizable: true,
        filter: {
          type: 'multiple',
          list: [
            { text: 'heterozygous', value: 'heterozygous' },
            { text: 'hemizygous', value: 'hemizygous' },
            { text: 'homozygous', value: 'homozygous' },
          ],
          onFilter: (value, record) => value.includes(record.zygosity)
        } },
      {
        title: 'Incidence Rate',
        dataIndex: 'incidenceRate',
        width: 320, ellipsis: true,
        key: 'incidenceRate',
        resizable: true,
        sorter: (a, b) => parseFloat(a.incidenceRate) - parseFloat(b.incidenceRate)
      },
      { title: 'Diagnostic Method', dataIndex: 'DiagnosticMethod', width: 320, ellipsis: true, key: 'DiagnosticMethod', resizable: true },
      {
        title: 'References', width: 120, ellipsis: true, key: 'References', dataIndex: 'References',
        customRender: ({ text, record }) => (<div><a href={text || '#'} target="_blank" class="bracket-links">References</a></div>),
        resizable: true
      },
      {
        title: 'Source', width: 120, ellipsis: true, key: 'source', dataIndex: 'source',
        customRender: ({ text, record }) => (<div><a href={text || '#'} target="_blank" class="bracket-links">Link</a></div>),
        resizable: true
      }
    ];