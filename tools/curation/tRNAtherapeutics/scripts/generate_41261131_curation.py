from pathlib import Path
import csv

BASE = Path(__file__).resolve().parents[4] / "field-curation-workdir"
PMID = "41261131"
DOI = "10.1038/s41586-025-09732-2"


def rna(seq):
    return seq.replace("\ufeff", "").replace(" ", "").replace("\n", "").upper().replace("T", "U")


def anticodon_edit(origin_dna, anticodon_dna):
    # Anticodon is nt 34-36 in these mature tRNA sequences.
    return origin_dna[:33] + anticodon_dna + origin_dna[36:]


human_leu1_origin = "ACCAGGATGGCCGAGTGGTTAAGGCGTTGGACTTAAGATCCAATGGACATATGTCCGCGTGGGTTCGAACCCCACTCCTGGTA"
human_leu1_ac = anticodon_edit(human_leu1_origin, "CTA")
human_leu1_hp13ta_hp12cg = "ACCAGGATGGCCGAGTGGTTAAGGCGTCTGACTCTAGATCAGATGGACATATGTCCGCGTGGGTTCGAACCCCACTCCTGGTA"
human_leu1_hp13cg_hp12cg = "ACCAGGATGGCCGAGTGGTTAAGGCGTCCGACTCTAGATCGGATGGACATATGTCCGCGTGGGTTCGAACCCCACTCCTGGTA"

human_leu4_origin = "ACCGGGATGGCTGAGTGGTTAAGGCGTTGGACTTAAGATCCAATGGACAGGTGTCCGCGTGGGTTCGAGCCCCACTCCCGGTA"
human_leu4_sup = anticodon_edit(human_leu4_origin, "CTA")
human_leu3_origin = "ACCAGAATGGCCGAGTGGTTAAGGCGTTGGACTTAAGATCCAATGGATTCATATCCGCGTGGGTTCGAACCCCACTTCTGGTA"
human_leu3_sup = anticodon_edit(human_leu3_origin, "CTA")
human_leu2_origin = "ACCGGGATGGCCGAGTGGTTAAGGCGTTGGACTTAAGATCCAATGGGCTGGTGCCCGCGTGGGTTCGAACCCCACTCTCGGTA"
human_leu2_sup = anticodon_edit(human_leu2_origin, "CTA")
human_tyr7_origin = "CCTTCGATAGCTCAGCTGGTAGAGCGGAGGACTGTAGACTGCGGAAACGTTTGTGGACATCCTTAGGTCGCTGGTTCAATTCCGGCTCGAAGGA"
human_tyr7_sup = anticodon_edit(human_tyr7_origin, "CTA")

mouse_leu2_origin = "ACCAGGATGGCCGAGTGGTTAAGGCGTTGGACTTAAGATCCAATGGACATATGTCTGCGTGGGTTCGAACCCCACTCCTGGTA"
mouse_leu2_tag = anticodon_edit(mouse_leu2_origin, "CTA")
mouse_leu2_tga = anticodon_edit(mouse_leu2_origin, "TCA")
mouse_leu2_engineered = "ACCAGGATGGCCGAGTGGTTAAGGCGTTTGACTCTAGTTCAAATGGACATATGTCTGCGTGGGTTCGAACCCCACTCCTGGTA"

rows = []


def add(action, ensure_id, evidence_source, evidence_location, confidence="high", notes="", **fields):
    row = {
        "action": action,
        "ENSURE_ID": ensure_id,
        "PMID": PMID,
        "DOI": DOI,
        "evidence_source": evidence_source,
        "evidence_location": evidence_location,
        "confidence": confidence,
        "notes": notes,
        "Related_disease": "",
        "PTC_gene": "",
        "Species_source_of_PTC_gene": "",
        "NCBI_ref_ID": "",
        "PTC(mutation_site)": "",
        "PTC_site": "",
        "Origin_aa_and_codon_of_PTC_site": "",
        "PTC_codon": "",
        "Delivery_as_vector_or_IVT_tRNA": "",
        "aa_and_anticodon_of_origin_tRNA": "",
        "aa_and_anticodon_of_sup-tRNA": "",
        "rnacentral_ID_of_origin_tRNA": "",
        "tRNAscan-SE_ID_of_origin_tRNA": "",
        "Species_source_of_origin_tRNA": "",
        "Sequence_of_origin_tRNA": "",
        "Sequence_of_sup-tRNA": "",
        "sup-tRNA_gene": "",
        "Modification": "",
        "Engineered_aaRS": "",
        "Reading_through_efficiency": "",
        "Measuring_of_efficiency": "",
        "Reaction_system": "",
        "Safety": "",
        "Secondary structure": "",
        "Secondary structure of sup-trna": "",
        "js_origin_tRNA": "",
        "js_sup_tRNA": "",
        "pdbid": "",
    }
    row.update(fields)
    rows.append(row)


common_human_disease = {
    "Related_disease": "Disease-agnostic PTC rescue",
    "PTC_gene": "TPP1; HEXA; NPC1; CFTR",
    "Species_source_of_PTC_gene": "Homo sapiens",
    "PTC(mutation_site)": "TPP1 p.L211X/p.L527X; HEXA p.L273X/p.L274X; NPC1 p.Q421X/p.Y423X; CFTR 15 pathogenic PTC variants",
    "PTC_site": "multiple TAG PTCs",
    "PTC_codon": "UAG",
    "Delivery_as_vector_or_IVT_tRNA": "prime editing",
    "Reaction_system": "HEK293T disease PTC models and CFTR cDNA panel; mCherry-STOP-GFP reporter validation",
    "Safety": "No significant off-target editing; no detected NTC readthrough",
}

add(
    "update",
    "1205",
    "Nature 2025 main text + Supplementary Tables 1 and 3",
    "epegRNA_00004; text lines 418-431, 1518-1523, 1868-1872",
    notes="Human Leu-TAA-1-1 ac-only TAG suppressor; sequence reconstructed from control tRNA-Leu-TAA-1-1-TAA and epegRNA RTT TAA>CTA.",
    **common_human_disease,
    **{
        "aa_and_anticodon_of_origin_tRNA": "Leu(UAA)",
        "aa_and_anticodon_of_sup-tRNA": "Leu(CUA)",
        "tRNAscan-SE_ID_of_origin_tRNA": "tRNA-Leu-TAA-1-1",
        "Species_source_of_origin_tRNA": "Homo sapiens",
        "Sequence_of_origin_tRNA": rna(human_leu1_origin),
        "Sequence_of_sup-tRNA": rna(human_leu1_ac),
        "sup-tRNA_gene": "tRNA-Leu-TAA-1-1",
        "Modification": "TAA>CTA anticodon-only edit",
        "Reading_through_efficiency": "Mature-tRNA screen FE hU6=53.361, minU6=32.699, none=38.971; prime editing 67-80% tRNA edit.",
        "Measuring_of_efficiency": "GFP FE; edit/rescue",
    },
)

add(
    "update",
    "1200",
    "Nature 2025 main text + Supplementary Table 1",
    "epegRNA_00005; text lines 1210-1213 and 1518-1523",
    notes="One of two engineered human Leu-TAA-1-1 variants explicitly advanced after optimization.",
    **common_human_disease,
    **{
        "aa_and_anticodon_of_origin_tRNA": "Leu(UAA)",
        "aa_and_anticodon_of_sup-tRNA": "Leu(CUA)",
        "tRNAscan-SE_ID_of_origin_tRNA": "tRNA-Leu-TAA-1-1",
        "Species_source_of_origin_tRNA": "Homo sapiens",
        "Sequence_of_origin_tRNA": rna(human_leu1_origin),
        "Sequence_of_sup-tRNA": rna(human_leu1_hp13ta_hp12cg),
        "sup-tRNA_gene": "tRNA-Leu-TAA-1-1+hp12ta>cg+hp13gc>ta",
        "Modification": "TAA>CTA; hp12ta>cg; hp13gc>ta",
        "Reading_through_efficiency": "Prime editing 56-84% tRNA edit; disease models showed 17-70% enzyme/protein restoration.",
        "Measuring_of_efficiency": "edit/rescue",
    },
)

add(
    "update",
    "1204",
    "Nature 2025 main text + Supplementary Table 1",
    "epegRNA_00006; text lines 1210-1213 and 1518-1523",
    notes="One of two engineered human Leu-TAA-1-1 variants explicitly advanced after optimization.",
    **common_human_disease,
    **{
        "aa_and_anticodon_of_origin_tRNA": "Leu(UAA)",
        "aa_and_anticodon_of_sup-tRNA": "Leu(CUA)",
        "tRNAscan-SE_ID_of_origin_tRNA": "tRNA-Leu-TAA-1-1",
        "Species_source_of_origin_tRNA": "Homo sapiens",
        "Sequence_of_origin_tRNA": rna(human_leu1_origin),
        "Sequence_of_sup-tRNA": rna(human_leu1_hp13cg_hp12cg),
        "sup-tRNA_gene": "tRNA-Leu-TAA-1-1+hp12ta>cg+hp13gc>cg",
        "Modification": "TAA>CTA; hp12ta>cg; hp13gc>cg",
        "Reading_through_efficiency": "Prime editing 64-83% tRNA edit; disease models showed 17-70% enzyme/protein restoration.",
        "Measuring_of_efficiency": "edit/rescue",
    },
)

lentiviral_common = {
    "Related_disease": "mCherry-STOP-GFP reporter",
    "PTC_gene": "mCherry-STOP-GFP",
    "Species_source_of_PTC_gene": "synthetic reporter",
    "PTC(mutation_site)": "mCherry-STOP-GFP TAG reporter",
    "PTC_site": "TAG reporter",
    "PTC_codon": "UAG",
    "Delivery_as_vector_or_IVT_tRNA": "lentiviral vector",
    "Reaction_system": "HEK293T mCherry-STOP-GFP lentiviral mature-tRNA screen",
    "Modification": "TAA>CTA anticodon edit",
    "Measuring_of_efficiency": "GFP+ fold enrichment",
}

for ensure_id, gene, origin, sup, aa_origin, aa_sup, fe, location in [
    ("1206", "tRNA-Leu-TAA-4-1", human_leu4_origin, human_leu4_sup, "Leu(UAA)", "Leu(CUA)", "hU6=227.768, minU6=156.824, none=22.588", "Supplementary Table 3; text lines 418-431"),
    ("1207", "tRNA-Leu-TAA-3-1", human_leu3_origin, human_leu3_sup, "Leu(UAA)", "Leu(CUA)", "hU6=167.731, minU6=140.325, none=52.832", "Supplementary Table 3; text lines 418-431"),
    ("1208", "tRNA-Leu-TAA-2-1", human_leu2_origin, human_leu2_sup, "Leu(UAA)", "Leu(CUA)", "hU6=28.115, minU6=49.860, none=30.814", "Supplementary Table 3; text lines 418-431"),
    ("1209", "tRNA-Tyr-GTA-7-1", human_tyr7_origin, human_tyr7_sup, "Tyr(GUA)", "Tyr(CUA)", "hU6=26.375, minU6=216.399, none=179.446", "Supplementary Table 3; text lines 418-431"),
]:
    add(
        "insert",
        ensure_id,
        "Nature 2025 Supplementary Table 3",
        location,
        notes="Included because the main text explicitly highlights this mature-tRNA screen hit/promoter behavior.",
        **lentiviral_common,
        **{
            "aa_and_anticodon_of_origin_tRNA": aa_origin,
            "aa_and_anticodon_of_sup-tRNA": aa_sup,
            "tRNAscan-SE_ID_of_origin_tRNA": gene,
            "Species_source_of_origin_tRNA": "Homo sapiens",
            "Sequence_of_origin_tRNA": rna(origin),
            "Sequence_of_sup-tRNA": rna(sup),
            "sup-tRNA_gene": gene,
            "Reading_through_efficiency": "Fold enrichment GFP+ vs plasmid pool: " + fe,
        },
    )

mouse_common = {
    "Species_source_of_PTC_gene": "Mus musculus",
    "Delivery_as_vector_or_IVT_tRNA": "dual-AAV9 prime editing",
    "aa_and_anticodon_of_origin_tRNA": "Leu(UAA)",
    "tRNAscan-SE_ID_of_origin_tRNA": "tRNA-Leu-TAA-2-1",
    "Species_source_of_origin_tRNA": "Mus musculus",
    "Sequence_of_origin_tRNA": rna(mouse_leu2_origin),
}

add(
    "insert",
    "1210",
    "Nature 2025 main text + Supplementary Tables 1 and 20",
    "epegRNA_00001; Fig. 5b; text lines 1877-1896",
    notes="Mouse equivalent of human Leu-TAA-1-1; in vivo TAG GFP reporter.",
    **mouse_common,
    **{
        "Related_disease": "In vivo GFP reporter",
        "PTC_gene": "eGFP",
        "PTC(mutation_site)": "eGFP TAG reporter",
        "PTC_site": "TAG reporter",
        "PTC_codon": "UAG",
        "aa_and_anticodon_of_sup-tRNA": "Leu(CUA)",
        "Sequence_of_sup-tRNA": rna(mouse_leu2_tag),
        "sup-tRNA_gene": "mouse tRNA-Leu-TAA-2-1",
        "Modification": "TAA>CTA anticodon-only edit",
        "Reading_through_efficiency": "Mean brain edit 11%; relative GFP yield 24% of WT (Fig. 5b mean 23.55%).",
        "Measuring_of_efficiency": "relative GFP yield",
        "Reaction_system": "C57BL/6 neonatal brain eGFP TAG reporter, AAV9 ICV injection",
        "Safety": "No NTC readthrough detected; body weight unchanged",
    },
)

add(
    "insert",
    "1211",
    "Nature 2025 main text + Supplementary Tables 1 and 20",
    "epegRNA_00002; Fig. 5b; text lines 1877-1896",
    notes="Mouse equivalent of human Leu-TAA-1-1; in vivo TGA GFP reporter.",
    **mouse_common,
    **{
        "Related_disease": "In vivo GFP reporter",
        "PTC_gene": "eGFP",
        "PTC(mutation_site)": "eGFP TGA reporter",
        "PTC_site": "TGA reporter",
        "PTC_codon": "UGA",
        "aa_and_anticodon_of_sup-tRNA": "Leu(UCA)",
        "Sequence_of_sup-tRNA": rna(mouse_leu2_tga),
        "sup-tRNA_gene": "mouse tRNA-Leu-TAA-2-1",
        "Modification": "TAA>TCA anticodon-only edit",
        "Reading_through_efficiency": "Mean brain edit 23%; relative GFP yield 26% of WT (Fig. 5b mean 25.88%).",
        "Measuring_of_efficiency": "relative GFP yield",
        "Reaction_system": "C57BL/6 neonatal brain eGFP TGA reporter, AAV9 ICV injection",
        "Safety": "No NTC readthrough detected",
    },
)

add(
    "insert",
    "1212",
    "Nature 2025 main text + Supplementary Tables 1 and 20",
    "epegRNA_00003; Fig. 5d; text lines 1917-1929",
    notes="Therapeutic in vivo Hurler syndrome model, mouse Idua W392X.",
    **mouse_common,
    **{
        "Related_disease": "Hurler syndrome",
        "PTC_gene": "Idua",
        "PTC(mutation_site)": "Idua p.W392X",
        "PTC_site": "Idua W392X",
        "Origin_aa_and_codon_of_PTC_site": "Trp(UGG)",
        "PTC_codon": "UAG",
        "aa_and_anticodon_of_sup-tRNA": "Leu(CUA)",
        "Sequence_of_sup-tRNA": rna(mouse_leu2_engineered),
        "sup-tRNA_gene": "mouse tRNA-Leu-TAA-2-1+hp13gc>ta+mut38a>t",
        "Modification": "TAA>CTA; hp13gc>ta; mut38a>t",
        "Reading_through_efficiency": "Desired edit cortex/heart/liver/kidney 6.3/6.1/6.8/0.05%; IDUA activity 6.3/7.6/1.7/0.31% WT.",
        "Measuring_of_efficiency": "edit; IDUA activity",
        "Reaction_system": "IduaW392X neonatal mouse, AAV9 ICV injection",
        "Safety": "Near-complete pathology rescue reported",
    },
)

ids = [r["ENSURE_ID"] for r in rows]
assert len(ids) == len(set(ids)), ids
for row in rows:
    assert row["evidence_source"] and row["evidence_location"] and row["confidence"]
    if row["PTC_codon"] == "UAG":
        assert "(CUA)" in row["aa_and_anticodon_of_sup-tRNA"]
    if row["PTC_codon"] == "UGA":
        assert "(UCA)" in row["aa_and_anticodon_of_sup-tRNA"]
    for col in ["Related_disease", "PTC_gene", "Species_source_of_PTC_gene", "Delivery_as_vector_or_IVT_tRNA", "Measuring_of_efficiency", "Safety"]:
        value = row.get(col, "") or ""
        limit = 128 if col == "Safety" else 50
        assert len(value) <= limit, (col, len(value), value)

out_tsv = BASE / "extractions" / "41261131_effective_candidates.tsv"
out_tsv.parent.mkdir(parents=True, exist_ok=True)
with out_tsv.open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()), delimiter="\t")
    writer.writeheader()
    writer.writerows(rows)

db_cols = [
    "Related_disease",
    "PTC_gene",
    "Species_source_of_PTC_gene",
    "NCBI_ref_ID",
    "PTC(mutation_site)",
    "PTC_site",
    "Origin_aa_and_codon_of_PTC_site",
    "PTC_codon",
    "Delivery_as_vector_or_IVT_tRNA",
    "aa_and_anticodon_of_origin_tRNA",
    "aa_and_anticodon_of_sup-tRNA",
    "rnacentral_ID_of_origin_tRNA",
    "tRNAscan-SE_ID_of_origin_tRNA",
    "Species_source_of_origin_tRNA",
    "ENSURE_ID",
    "Sequence_of_origin_tRNA",
    "Sequence_of_sup-tRNA",
    "sup-tRNA_gene",
    "Modification",
    "Engineered_aaRS",
    "Reading_through_efficiency",
    "Measuring_of_efficiency",
    "Reaction_system",
    "Safety",
    "PMID",
    "Secondary structure",
    "Secondary structure of sup-trna",
    "js_origin_tRNA",
    "js_sup_tRNA",
    "pdbid",
]


def qident(col):
    return "`" + col.replace("`", "``") + "`"


def qval(value):
    if value is None or value == "":
        return "NULL"
    s = str(value)
    return "'" + s.replace("\\", "\\\\").replace("'", "''") + "'"


sql = [
    "-- Curated update for PMID 41261131 / DOI 10.1038/s41586-025-09732-2",
    "-- Generated from field-curation-workdir/extractions/41261131_effective_candidates.tsv",
    "START TRANSACTION;",
]

for row in rows:
    values = {col: row.get(col, "") for col in db_cols}
    values["PMID"] = PMID
    if row["action"] == "update":
        assignments = ",\n  ".join(
            f"{qident(col)} = {qval(values[col])}"
            for col in db_cols
            if col not in ("ENSURE_ID", "PMID")
        )
        sql.append(
            f"\nUPDATE Engineered_sup_tRNA\nSET\n  {assignments}\nWHERE ENSURE_ID = {qval(row['ENSURE_ID'])} AND PMID = {PMID};"
        )
    else:
        cols = ", ".join(qident(col) for col in db_cols)
        vals = ", ".join(qval(values[col]) for col in db_cols)
        sql.append(
            f"\nINSERT INTO Engineered_sup_tRNA ({cols})\nSELECT {vals}\nWHERE NOT EXISTS (SELECT 1 FROM Engineered_sup_tRNA WHERE ENSURE_ID = {qval(row['ENSURE_ID'])});"
        )

sql.append("\nCOMMIT;")
out_sql = BASE / "sql" / "41261131_effective_candidates.sql"
out_sql.parent.mkdir(parents=True, exist_ok=True)
out_sql.write_text("\n".join(sql) + "\n")

review = BASE / "notes" / "41261131_update_review.md"
review.write_text(
    f"""# PMID 41261131 curation review

Source: Nature 2025, DOI {DOI}. The article is open access and the downloaded supplementary files are in `field-curation-workdir/papers/41261131_supplementary/`.

Included for upload:

- 3 existing records updated to the human Leu-TAA-1-1 PERT variants that were advanced/validated: ac-only, hp12ta>cg+hp13gc>ta, hp12ta>cg+hp13gc>cg.
- 4 mature-tRNA lentiviral screen hits explicitly highlighted in the main text: Leu-TAA-4-1, Leu-TAA-3-1, Leu-TAA-2-1, Tyr-GTA-7-1. Leu-TAA-1-1 is represented by the ac-only PERT record and includes its mature-screen fold enrichment.
- 3 mouse in vivo records: Leu-TAA-2-1 TAG reporter, Leu-TAA-2-1 TGA reporter, and engineered Leu-TAA-2-1+hp13gc>ta+mut38a>t in the Hurler syndrome model.

Excluded from upload:

- The full 17,579-epegRNA screens per stop codon, all 418 mature tRNA constructs, negative controls, and ineffective TAA screen hits.
- Saturation-mutagenesis variants that were not advanced or validated in later disease/animal models.
- ClinVar/CFTR sequence contexts as separate rows, because they test PTC context rather than new sup-tRNA sequences.

Sequence note:

The human PERT sup-tRNA sequences were reconstructed from the wild-type/control mature tRNA sequence and Supplementary Table 1 epegRNA RTT edits (TAA>CTA plus named hairpin edits). This avoids copying unadvanced or internally inconsistent Table 8 cassette-only rows and keeps the uploaded rows aligned with the variants explicitly advanced in the main text.
"""
)

print(out_tsv)
print(out_sql)
print(review)
print(f"rows={len(rows)} updates={sum(r['action'] == 'update' for r in rows)} inserts={sum(r['action'] == 'insert' for r in rows)}")
