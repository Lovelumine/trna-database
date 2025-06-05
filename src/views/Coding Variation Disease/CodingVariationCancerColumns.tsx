import { STableColumnsType } from "@shene/table";
import { ref } from "vue";
export type DataType = { [key: string]: string };

export     const allColumns: STableColumnsType<DataType> = [
      { title: 'Mutation Type', dataIndex: 'MUTATION_TYPE', width: 150, ellipsis: true, key: 'MUTATION_TYPE', resizable: true ,        filter: {
          type: 'multiple',
          list: [
            { text: 'Missense', value: 'Missense' },
            { text: 'Nonsense', value: 'Nonsense' },
            {text:'Frameshift',value:'Frameshift'},
            {text:'Deletion-Frameshift',value:'Deletion-Frameshift'},
            {text:'Insertion-Frameshift',value:'Insertion-Frameshift'}
          ],
          onFilter: (value, record) => value.includes(record.MUTATION_TYPE)
        }},
      { title: 'Gene Name', dataIndex: 'GENE_NAME', width: 150, ellipsis: true, key: 'GENE_NAME', resizable: true },
      { title: 'Ensembl ID', dataIndex: 'ENSEMBL_ID', width: 180, ellipsis: true, key: 'ENSEMBL_ID', resizable: true },
      { title: 'Genomic Mutation ID', dataIndex: 'GENOMIC_MUTATION_ID', width: 120, ellipsis: true, key: 'GENOMIC_MUTATION_ID', resizable: true },
      { title: 'Genomic Mutation URL', dataIndex: 'GENOMIC_MUTATION_URL', width: 120, ellipsis: true, key: 'GENOMIC_MUTATION_URL', resizable: true },
      { title: 'Legacy Mutation ID', dataIndex: 'LEGACY_MUTATION_ID', width: 150, ellipsis: true, key: 'LEGACY_MUTATION_ID', resizable: true },
      { title: 'Legacy Mutation URL', dataIndex: 'LEGACY_MUTATION_URL', width: 150, ellipsis: true, key: 'LEGACY_MUTATION_URL', resizable: true },
      { title: 'Mutation Locus in GRCh37', dataIndex: 'MUTATION_LOCUS_IN_GRCh37', width: 200, ellipsis: true, key: 'MUTATION_LOCUS_IN_GRCh37', resizable: true },
      { title: 'Mutation Locus in GRCh38', dataIndex: 'MUTATION_LOCUS_IN_GRCh38', width: 200, ellipsis: true, key: 'MUTATION_LOCUS_IN_GRCh38', resizable: true },
      { title: 'Mutation CDS', dataIndex: 'MUTATION_CDS', width: 150, ellipsis: true, key: 'MUTATION_CDS', resizable: true },
      { title: 'MUTATION AA', dataIndex: 'MUTATION_AA', width: 150, ellipsis: true, key: 'MUTATION_AA', resizable: true },
      { title: 'Genomic Ref Allele', dataIndex: 'GENOMIC_REF_ALLELE', width: 150, ellipsis: true, key: 'GENOMIC_REF_ALLELE', resizable: true },
      { title: 'Genomic Mut Allele', dataIndex: 'GENOMIC_MUT_ALLELE', width: 150, ellipsis: true, key: 'GENOMIC_MUT_ALLELE', resizable: true },
      { title: 'Disease', dataIndex: 'DISEASE', width: 1200, ellipsis: true, key: 'DISEASE', resizable: true }
    ];

export     const selectedColumns = ref<string[]>([
      'GENE_NAME',
      'MUTATION_LOCUS_IN_GRCh37',
      'MUTATION_LOCUS_IN_GRCh38',
      'MUTATION_TYPE',
      'DISEASE'
    ]);