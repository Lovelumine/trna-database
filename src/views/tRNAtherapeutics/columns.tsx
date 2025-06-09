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
  { title: 'PTC gene', dataIndex: 'PTC_gene', width: 150, ellipsis: true, key: 'PTC_gene', resizable: true },
  { title: 'Species Source of PTC gene', dataIndex: 'Species_source_of_PTC_gene', width: 100, ellipsis: true, key: 'Species_source_of_PTC_gene', resizable: true },
  { title: 'NCBI ref ID', dataIndex: 'NCBI_ref_ID', width: 220, ellipsis: true, key: 'NCBI_ref_ID', resizable: true },
  { title: 'PTC(mutation site)', dataIndex: 'PTC(mutation_site)', width: 300, ellipsis: true, key: 'PTC(mutation_site)', resizable: true },
  { title: 'PTC site', dataIndex: 'PTC_site', width: 340, ellipsis: true, key: 'PTC_site', resizable: true },
  { title: 'Origin AA and Codon of PTC Site', dataIndex: 'Origin_aa_and_codon_of_PTC_site', width: 200, ellipsis: true, key: 'Origin_aa_and_codon_of_PTC_site', resizable: true },
  { title: 'PTC Codon', dataIndex: 'PTC_codon', width: 100, ellipsis: true, key: 'PTC_codon', resizable: true },
  { title: 'Delivery as Vector or IVT tRNA', dataIndex: 'Delivery_as_vector_or_IVT_tRNA', width: 200, ellipsis: true, key: 'Delivery_as_vector_or_IVT_tRNA', resizable: true },
  { title: 'AA and Anticodon of Origin tRNA', dataIndex: 'aa_and_anticodon_of_origin_tRNA', width: 250, ellipsis: true, key: 'aa_and_anticodon_of_origin_tRNA', resizable: true },
  { title: 'AA and Anticodon of sup-tRNA', dataIndex: 'aa_and_anticodon_of_sup-tRNA', width: 250, ellipsis: true, key: 'aa_and_anticodon_of_sup-tRNA', resizable: true },
  { title: 'Rnacentral ID of Origin tRNA', dataIndex: 'rnacentral_ID_of_origin_tRNA', width: 100, ellipsis: true, key: 'rnacentral_ID_of_origin_tRNA', resizable: true },
  { title: 'tRNAscan-SE ID of origin tRNA', dataIndex: 'tRNAscan_SE_ID_of_origin_tRNA', width: 300, ellipsis: true, key: 'tRNAscan_SE_ID_of_origin_tRNA', resizable: true },
  { title: 'Species Source of Origin tRNA', dataIndex: 'Species_source_of_origin_tRNA', width: 250, ellipsis: true, key: 'Species_source_of_origin_tRNA', resizable: true ,customRender: ({ text }) => <em>{text}</em>,},
  { title: 'ENSURE ID', dataIndex: 'ENSURE_ID', width: 300, ellipsis: true, key: 'ENSURE_ID', resizable: true },
  { title: 'Sequence of Origin tRNA', dataIndex: 'Sequence_of_origin_tRNA', width: 300, ellipsis: true, key: 'Sequence_of_origin_tRNA', resizable: true },
  { title: 'Sequence of Sup-tRNA', dataIndex: 'Sequence_of_sup-tRNA', width: 350, ellipsis: true, key: 'Sequence_of_sup-tRNA', resizable: true },
  { title: 'sup-tRNA Gene', dataIndex: 'sup-tRNA_gene', width: 300, ellipsis: true, key: 'sup-tRNA_gene', resizable: true },
  { title: 'Modification', dataIndex: 'Modification', width: 300, ellipsis: true, key: 'Modification', resizable: true },
  { title: 'Engineered aaRS', dataIndex: 'Engineered_aaRS', width: 150, ellipsis: true, key: 'Engineered_aaRS', resizable: true },
  { title: 'Reading Through Efficiency', dataIndex: 'Reading_through_efficiency', width: 200, ellipsis: true, key: 'Reading_through_efficiency', resizable: true },
  { title: 'Measuring of Efficiency', dataIndex: 'Measuring_of_efficiency', width: 200, ellipsis: true, key: 'Measuring_of_efficiency', resizable: true },
  { title: 'Reaction_system', dataIndex: 'Reaction_system', width: 150, ellipsis: true, key: 'Reaction_system', resizable: true },
  { title: 'Safety', dataIndex: 'Safety', width: 100, ellipsis: true, key: 'Safety', resizable: true },
  { title: 'Secondary structure', dataIndex: 'Secondary structure', width: 150, ellipsis: true, key: 'Secondary structure', resizable: true },
  { title: 'Secondary structure of sup-tRNA', dataIndex: 'Secondary structure of sup-trna', width: 150, ellipsis: true, key: 'Secondary structure of sup-trna', resizable: true },
    // { title: 'Pairwise Alignment', dataIndex: 'pairwise_alignment', width: 150, ellipsis: true, key: 'pairwise_alignment', resizable: true },
 
  { title: 'PMID', dataIndex: 'PMID', width: 100, ellipsis: true, key: 'PMID', customRender: ({ text, record }) => (<div><a href={'https://pubmed.ncbi.nlm.nih.gov/' + record.PMID || '#'} target="_blank" class="bracket-links">{record.PMID}</a></div>),
  filter: {
    type: 'multiple',
    list: [{'text': '9465022', 'value': '9465022'}, {'text': '30778053', 'value': '30778053'}, {'text': '38580646', 'value': '38580646'}, {'text': '10498252', 'value': '10498252'}, {'text': '37258671', 'value': '37258671'}, {'text': '2990894', 'value': '2990894'}, {'text': '6308765', 'value': '6308765'}, {'text': '24424122', 'value': '24424122'}, {'text': '35322228', 'value': '35322228'}, {'text': '34158503', 'value': '34158503'}, {'text': '29155943', 'value': '29155943'}, {'text': '30112727', 'value': '30112727'}, {'text': '19852970', 'value': '19852970'}, {'text': '38042487', 'value': '38042487'}, {'text': '25918386', 'value': '25918386'}, {'text': '28076288', 'value': '28076288'}, {'text': '26694948', 'value': '26694948'}, {'text': '35532803', 'value': '35532803'}, {'text': '20571084', 'value': '20571084'}, {'text': '23274575', 'value': '23274575'}, {'text': '15576346', 'value': '15576346'}, {'text': '10220370', 'value': '10220370'}, {'text': '2193162', 'value': '2193162'}, {'text': '33069552', 'value': '33069552'}, {'text': '11226228', 'value': '11226228'}, {'text': '24386240', 'value': '24386240'}, {'text': '23379331', 'value': '23379331'}, {'text': '6310546', 'value': '6310546'}, {'text': '31346230', 'value': '31346230'}, {'text': '17360621', 'value': '17360621'}, {'text': '9331409', 'value': '9331409'}, {'text': '8416930', 'value': '8416930'}, {'text': '11564556', 'value': '11564556'}, {'text': '2251270', 'value': '2251270'}, {'text': '12409460', 'value': '12409460'}, {'text': '23924161', 'value': '23924161'}, {'text': '9294168', 'value': '9294168'}, {'text': '3045821', 'value': '3045821'}, {'text': '38777090', 'value': '38777090'}, {'text': '26405058', 'value': '26405058'}, {'text': '15187228', 'value': '15187228'}, {'text': '11717406', 'value': '11717406'}, {'text': '1344892', 'value': '1344892'}, {'text': '3532123', 'value': '3532123'}, {'text': '6254058', 'value': '6254058'}, {'text': '12466560', 'value': '12466560'}, {'text': '6363071', 'value': '6363071'}, {'text': '9447966', 'value': '9447966'}, {'text': '23874413', 'value': '23874413'}, {'text': '19378306', 'value': '19378306'}, {'text': '12582239', 'value': '12582239'}, {'text': '19749377', 'value': '19749377'}, {'text': '15222758', 'value': '15222758'}, {'text': '2602139', 'value': '2602139'}, {'text': '2096017', 'value': '2096017'}, {'text': '11866580', 'value': '11866580'}, {'text': '17698637', 'value': '17698637'}, {'text': '17685515', 'value': '17685515'}, {'text': '23103832', 'value': '23103832'}],
    onFilter: (value, record) => String(record.PMID).includes(value),
  }, resizable: true },
  { title: 'View Details', dataIndex: 'ENSURE_ID', width: 100, ellipsis: true, key: 'pre_ENSURE_ID', customRender: ({ text, record }) => (<div><a href={'/expanded/' + record.ENSURE_ID || '#'} target="_blank" class="bracket-links">View Details</a></div>),resizable: true },
];
