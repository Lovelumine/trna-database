//columns.ts
import type { STableColumnsType } from '@shene/table';

export type DataType = { [key: string]: string };

export const allColumns: STableColumnsType<DataType> = [
  { title: 'Related Disease', dataIndex: 'Related_disease', width: 200, ellipsis: true, key: 'Related_disease', 
    filter: {
      type: 'multiple',
      list: [
        { text: 'cystic fibrosis', value: 'cystic fibrosis' },
        { text: 'Model protein', value: 'Model protein' },
        { text: 'primary ciliary dyskinesia (PCD)', value: 'primary ciliary dyskinesia (PCD)' },
        { text: 'Xeroderma pigmentosum', value: 'Xeroderma pigmentosum' }, 
        { text: 'hereditary diffuse gastric cancer (HDGC)', value: 'hereditary diffuse gastric cancer (HDGC)' },    
        { text: 'mucopolysaccharidosis type I', value: 'mucopolysaccharidosis type I' },    
      ],
      onFilter: (value, record) => value.includes(record.Related_disease)
    },
    resizable: true },
  { title: 'PTC_gene', dataIndex: 'PTC_gene', width: 150, ellipsis: true, key: 'PTC_gene', resizable: true },
  { title: 'Species Source of PTC gene', dataIndex: 'Species_source_of_PTC_gene', width: 100, ellipsis: true, key: 'Species_source_of_PTC_gene', resizable: true },
  { title: 'NCBI ref ID', dataIndex: 'NCBI_ref_ID', width: 220, ellipsis: true, key: 'NCBI_ref_ID', resizable: true },
  { title: 'PTC(mutation_site)', dataIndex: 'PTC(mutation_site)', width: 300, ellipsis: true, key: 'PTC(mutation_site)', resizable: true },
  { title: 'PTC_site', dataIndex: 'PTC_site', width: 340, ellipsis: true, key: 'PTC_site', resizable: true },
  { title: 'Origin AA and Codon of PTC Site', dataIndex: 'Origin_aa_and_codon_of_PTC_site', width: 200, ellipsis: true, key: 'Origin_aa_and_codon_of_PTC_site', resizable: true },
  { title: 'PTC Codon', dataIndex: 'PTC_codon', width: 100, ellipsis: true, key: 'PTC_codon', resizable: true },
  { title: 'Delivery as Vector or IVT tRNA', dataIndex: 'Delivery_as_vector_or_IVT_tRNA', width: 200, ellipsis: true, key: 'Delivery_as_vector_or_IVT_tRNA', resizable: true },
  { title: 'AA and Anticodon of Origin tRNA', dataIndex: 'aa_and_anticodon_of_origin_tRNA', width: 250, ellipsis: true, key: 'aa_and_anticodon_of_origin_tRNA', resizable: true },
  { title: 'AA and Anticodon of sup-tRNA', dataIndex: 'aa_and_anticodon_of_sup-tRNA', width: 250, ellipsis: true, key: 'aa_and_anticodon_of_sup-tRNA', resizable: true },
  { title: 'Rnacentral ID of Origin tRNA', dataIndex: 'rnacentral_ID_of_origin_tRNA', width: 100, ellipsis: true, key: 'rnacentral_ID_of_origin_tRNA', resizable: true },
  { title: 'tRNAscan-SE ID of origin tRNA', dataIndex: 'tRNAscan_SE_ID_of_origin_tRNA', width: 300, ellipsis: true, key: 'tRNAscan_SE_ID_of_origin_tRNA', resizable: true },
  { title: 'Species Source of Origin tRNA', dataIndex: 'Species_source_of_origin_tRNA', width: 250, ellipsis: true, key: 'Species_source_of_origin_tRNA', resizable: true },
  { title: 'ENSURE ID', dataIndex: 'ENSURE_ID', width: 300, ellipsis: true, key: 'ENSURE_ID', resizable: true },
  { title: 'Sequence of Origin tRNA', dataIndex: 'Sequence_of_origin_tRNA', width: 300, ellipsis: true, key: 'Sequence_of_origin_tRNA', resizable: true },
  { title: 'Sequence of Sup-tRNA', dataIndex: 'Sequence_of_sup-tRNA', width: 350, ellipsis: true, key: 'Sequence_of_sup-tRNA', resizable: true },
  { title: 'sup-tRNA Gene', dataIndex: 'sup-tRNA_gene', width: 300, ellipsis: true, key: 'sup-tRNA_gene', resizable: true },
  { title: 'Modification', dataIndex: 'Modification', width: 300, ellipsis: true, key: 'Modification', resizable: true },
  { title: 'Prediction_of_tRNAScan-SE', dataIndex: 'Prediction_of_tRNAScan-SE', width: 300, ellipsis: true, key: 'Prediction_of_tRNAScan-SE', resizable: true },
  { title: 'Alignment', dataIndex: 'Alignment', width: 300, ellipsis: true, key: 'Alignment', resizable: true },
  { title: 'E-Value', dataIndex: 'E_Value', width: 300, ellipsis: true, key: 'E_Value', resizable: true },
  { title: 'Score', dataIndex: 'Score', width: 300, ellipsis: true, key: 'Score', resizable: true },
  { title: 'Identities', dataIndex: 'Identities', width: 300, ellipsis: true, key: 'Identities', resizable: true },
  { title: 'Gaps', dataIndex: 'Gaps', width: 300, ellipsis: true, key: 'Gaps', resizable: true },
  { title: 'Ref Length', dataIndex: 'Ref_length', width: 100, ellipsis: true, key: 'Ref_length', resizable: true },
  { title: 'Engineered aaRS', dataIndex: 'Engineered_aaRS', width: 150, ellipsis: true, key: 'Engineered_aaRS', resizable: true },
  { title: 'Reading Through Efficiency', dataIndex: 'Reading_through_efficiency', width: 200, ellipsis: true, key: 'Reading_through_efficiency', resizable: true },
  { title: 'Measuring of Efficiency', dataIndex: 'Measuring_of_efficiency', width: 200, ellipsis: true, key: 'Measuring_of_efficiency', resizable: true },
  { title: 'Supplementary Information of Measurement', dataIndex: 'Supplenmentary_information_of_Measurement', width: 300, ellipsis: true, key: 'Supplenmentary_information_of_Measurement', resizable: true },
  { title: 'Reaction System', dataIndex: 'Reaction_system', width: 150, ellipsis: true, key: 'Reaction_system', resizable: true },
  { title: 'Dose for IVT tRNA Delivery', dataIndex: 'Dose_for_IVT_tRNA_delivery', width: 150, ellipsis: true, key: 'Dose_for_IVT_tRNA_delivery', resizable: true },
  { title: 'Dose for Vector Delivery', dataIndex: 'Dose_for_IVT_tRNA_delivery', width: 150, ellipsis: true, key: 'Dose_for_IVT_tRNA_delivery', resizable: true },
  { title: 'tRNA Gene Copy Number for Vector Delivery', dataIndex: 'tRNA_gene_copy_number_for_vector_delivery', width: 150, ellipsis: true, key: 'tRNA_gene_copy_number_for_vector_delivery', resizable: true },
  { title: 'Promoter for Vector Delivery', dataIndex: 'Promoter_for_vector_delivery', width: 150, ellipsis: true, key: 'Promoter_for_vector_delivery', resizable: true },
  { title: 'Safety', dataIndex: 'Safety', width: 100, ellipsis: true, key: 'Safety', resizable: true },
  { title: 'Immunogenicity', dataIndex: 'Immunogenicity', width: 150, ellipsis: true, key: 'Immunogenicity', resizable: true },
  { title: 'PMID', dataIndex: 'PMID', width: 100, ellipsis: true, key: 'PMID', customRender: ({ text, record }) => (<div><a href={'https://pubmed.ncbi.nlm.nih.gov/' + record.PMID || '#'} target="_blank" class="bracket-links">{record.PMID}</a></div>),
  filter: {
    type: 'multiple',
    list: [
      { text: '2990894', value: '2990894' },
      { text: '6308765', value: '6308765' },
      { text: '9465022', value: '9465022' },
      { text: '10498252', value: '10498252' }, 
      { text: '24424122', value: '24424122' },    
      { text: '30778053', value: '30778053' }, 
      { text: '34158503', value: '34158503' }, 
      { text: '35322228', value: '35322228' }, 
      { text: '37258671', value: '37258671' }, 
      { text: '38580646', value: '38580646' },    
    ],
    onFilter: (value, record) => String(record.PMID).includes(value),
  }, resizable: true },
  { title: 'View Details', dataIndex: 'pre_ENSURE_ID', width: 100, ellipsis: true, key: 'pre_ENSURE_ID', customRender: ({ text, record }) => (<div><a href={'/expanded/' + record.pre_ENSURE_ID || '#'} target="_blank" class="bracket-links">View Details</a></div>),resizable: true },
];
