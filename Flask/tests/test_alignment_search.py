from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd


FLASK_ROOT = Path(__file__).resolve().parents[1]
if str(FLASK_ROOT) not in sys.path:
    sys.path.insert(0, str(FLASK_ROOT))

from app.logic.align import (  # noqa: E402
    _pick_sequence_columns,
    alignment_result,
    normalize_sequence,
    search_in_csvs,
)


def test_normalize_sequence_maps_trna_modifications_to_canonical_bases():
    assert normalize_sequence("G U T P D Ψ I #") == "GUUUUUN"


def test_alignment_result_labels_database_sequence_as_target():
    result = alignment_result("AAA", "GGGAAA", 2.0, -0.5, -2.0, -1.0, "auto")

    assert result["alignment_mode"] == "local"
    assert result["identity"] == 100.0
    assert result["query_coverage"] == 100.0
    assert result["target_coverage"] == 50.0
    assert result["alignment"].splitlines() == [
        "target AAA",
        "       |||",
        "query  AAA",
    ]


def test_default_sequence_columns_exclude_non_nucleotide_fields():
    assert _pick_sequence_columns(
        "coding_variation_cancer",
        ["MUTATION_CDS", "MUTATION_AA"],
    ) == ["MUTATION_CDS"]
    assert _pick_sequence_columns(
        "Engineered_sup_tRNA",
        [
            "Sequence_of_origin_tRNA",
            "aa_and_anticodon_of_origin_tRNA",
            "Secondary structure of sup-trna",
            "PTC_codon",
        ],
    ) == ["Sequence_of_origin_tRNA", "PTC_codon"]


def test_search_in_csvs_uses_kmer_candidates_and_returns_metrics(tmp_path: Path):
    csv_path = tmp_path / "Engineered sup-tRNA.csv"
    pd.DataFrame(
        [
            {
                "ENSURE_ID": "ENSURE_1",
                "Sequence_of_sup-tRNA": "GGGAAACCCUUU",
                "PTC_codon": "UAG",
            },
            {
                "ENSURE_ID": "ENSURE_2",
                "Sequence_of_sup-tRNA": "GGGGGGUUUUUU",
                "PTC_codon": "UGA",
            },
        ]
    ).to_csv(csv_path, index=False)

    results = search_in_csvs(
        {
            "query_seq": "AAACCC",
            "csv_paths": [str(csv_path)],
            "number": 1,
            "match": 2.0,
            "mismatch": -0.5,
            "gap_open": -2.0,
            "gap_extend": -1.0,
        }
    )

    assert len(results) == 1
    hit = results[0]
    assert hit["row_data"]["ENSURE_ID"] == "ENSURE_1"
    assert hit["column"] == "Sequence_of_sup-tRNA"
    assert hit["method"] == "k-mer candidate search + pairwise alignment"
    assert hit["kmer_hits"] > 0
    assert hit["identity"] == 100.0
    assert hit["query_coverage"] == 100.0
