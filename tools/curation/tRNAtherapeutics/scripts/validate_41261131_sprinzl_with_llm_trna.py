import contextlib
import csv
import io
import json
import os
import sys
from pathlib import Path


BASE = Path(__file__).resolve().parents[4] / "field-curation-workdir"
LLM_TRNA_REPO = Path(
    os.environ.get("LLM_TRNA_REPO", str(BASE.parent.parent / "LLM-tRNAAlign"))
).expanduser()

CANDIDATE_TSV = BASE / "backups" / "Engineered_sup_tRNA_PMID41261131_structure_before.tsv"
CURRENT_TSV = BASE / "extractions" / "41261131_structure_updates.tsv"
OUT_DIR = BASE / "extractions" / "41261131_llm_trna_csv"
OUT_TSV = BASE / "extractions" / "41261131_llm_trna_local_sprinzl.tsv"
OUT_NOTE = BASE / "notes" / "41261131_llm_trna_sprinzl_check.md"
LOG_DIR = BASE / "logs" / "41261131_llm_trna"


def norm(seq: str) -> str:
    return (seq or "").strip().upper().replace("T", "U")


def load_tsv(path: Path):
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def parse_json_list(value: str):
    if not value or value == "NULL":
        return []
    return json.loads(value)


def non_gap_ids(items, key):
    return [str(item.get("id", "")) for item in items if str(item.get(key, "-")) != "-"]


def non_gap_seq(items, key):
    return "".join(str(item.get(key, "-")) for item in items if str(item.get(key, "-")) != "-")


def serious_diffs(current_items, current_key, local_nums, local_bases):
    current = {str(item.get("id", "")): str(item.get(current_key, "-")) for item in current_items}
    local = {str(num): str(base) for num, base in zip(local_nums, local_bases)}
    ids = list(dict.fromkeys(list(current.keys()) + list(local.keys())))
    diffs = []
    for coord in ids:
        cur = current.get(coord, "-")
        loc = local.get(coord, "-")
        if cur != loc and (cur != "-" or loc != "-"):
            diffs.append(f"{coord}:{cur}>{loc}")
    return diffs


def parse_alignment_csv(csv_text: str):
    rows = list(csv.reader(io.StringIO(csv_text)))
    rows = [row for row in rows if row]
    if len(rows) < 2:
        raise RuntimeError("alignment CSV has fewer than two rows")
    nums = [str(x).strip() for x in rows[0]]
    bases = [str(x).strip().upper().replace("T", "U") for x in rows[-1]]
    if len(nums) != len(bases):
        raise RuntimeError(f"alignment CSV width mismatch: {len(nums)} != {len(bases)}")
    return nums, bases


def run_local_alignment(perform_full_alignment, seq: str, label: str):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = OUT_DIR / f"{label}.csv"
    log_path = LOG_DIR / f"{label}.log"
    with log_path.open("w") as log_handle:
        with contextlib.redirect_stdout(log_handle), contextlib.redirect_stderr(log_handle):
            template_name, csv_text = perform_full_alignment(
                norm(seq),
                str(csv_path),
                anticode="",
                use_llm=False,
            )
    nums, bases = parse_alignment_csv(csv_text)
    reconstructed = "".join(base for base in bases if base != "-")
    if reconstructed != norm(seq):
        raise RuntimeError(
            f"{label}: base preservation failed, got {reconstructed}, expected {norm(seq)}"
        )
    return template_name, nums, bases


def main():
    if not LLM_TRNA_REPO.exists():
        raise RuntimeError(f"LLM-tRNAAlign repo not found: {LLM_TRNA_REPO}")

    os.environ["LLM_POSTCHECK"] = "0"
    os.environ.setdefault("TRNAALIGN_WORKERS", "4")

    sys.path.insert(0, str(LLM_TRNA_REPO))
    old_cwd = Path.cwd()
    os.chdir(LLM_TRNA_REPO)
    try:
        from pythonscript.align import perform_full_alignment

        candidate_rows = {row["ENSURE_ID"]: row for row in load_tsv(CANDIDATE_TSV)}
        current_rows = {row["ENSURE_ID"]: row for row in load_tsv(CURRENT_TSV)}

        summaries = []
        for ensure_id in sorted(candidate_rows, key=lambda x: int(x)):
            cand = candidate_rows[ensure_id]
            cur = current_rows[ensure_id]
            origin_seq = norm(cand["Sequence_of_origin_tRNA"])
            sup_seq = norm(cand["Sequence_of_sup-tRNA"])

            origin_tpl, origin_nums, origin_bases = run_local_alignment(
                perform_full_alignment, origin_seq, f"{ensure_id}_origin"
            )
            sup_tpl, sup_nums, sup_bases = run_local_alignment(
                perform_full_alignment, sup_seq, f"{ensure_id}_sup"
            )

            cur_origin = parse_json_list(cur["js_origin_tRNA"])
            cur_sup = parse_json_list(cur["js_sup_tRNA"])

            origin_label_equal = non_gap_ids(cur_origin, "base") == [
                coord for coord, base in zip(origin_nums, origin_bases) if base != "-"
            ]
            sup_label_equal = non_gap_ids(cur_sup, "sup_base") == [
                coord for coord, base in zip(sup_nums, sup_bases) if base != "-"
            ]

            origin_diffs = serious_diffs(cur_origin, "base", origin_nums, origin_bases)
            sup_diffs = serious_diffs(cur_sup, "sup_base", sup_nums, sup_bases)
            origin_extra_gap_coords = [
                coord
                for coord, base in zip(origin_nums, origin_bases)
                if base == "-" and coord not in {str(item.get("id", "")) for item in cur_origin}
            ]
            sup_extra_gap_coords = [
                coord
                for coord, base in zip(sup_nums, sup_bases)
                if base == "-" and coord not in {str(item.get("id", "")) for item in cur_sup}
            ]

            summaries.append(
                {
                    "ENSURE_ID": ensure_id,
                    "sup-tRNA_gene": cand.get("sup-tRNA_gene", ""),
                    "origin_template": origin_tpl,
                    "sup_template": sup_tpl,
                    "origin_current_items": len(cur_origin),
                    "origin_local_items": len(origin_nums),
                    "sup_current_items": len(cur_sup),
                    "sup_local_items": len(sup_nums),
                    "origin_sequence_ok": str(non_gap_seq(cur_origin, "base") == origin_seq),
                    "sup_sequence_ok": str(non_gap_seq(cur_sup, "sup_base") == sup_seq),
                    "origin_non_gap_labels_equal": str(origin_label_equal),
                    "sup_non_gap_labels_equal": str(sup_label_equal),
                    "origin_serious_diff_count": len(origin_diffs),
                    "sup_serious_diff_count": len(sup_diffs),
                    "origin_serious_diffs": ";".join(origin_diffs[:20]),
                    "sup_serious_diffs": ";".join(sup_diffs[:20]),
                    "origin_local_extra_gap_coords": ",".join(origin_extra_gap_coords),
                    "sup_local_extra_gap_coords": ",".join(sup_extra_gap_coords),
                }
            )
    finally:
        os.chdir(old_cwd)

    OUT_TSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_TSV.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(summaries[0].keys()), delimiter="\t")
        writer.writeheader()
        writer.writerows(summaries)

    serious_rows = [
        row for row in summaries
        if row["origin_serious_diff_count"] or row["sup_serious_diff_count"]
    ]
    all_origin_ok = all(row["origin_non_gap_labels_equal"] == "True" for row in summaries)
    all_sup_ok = all(row["sup_non_gap_labels_equal"] == "True" for row in summaries)

    OUT_NOTE.write_text(
        "\n".join(
            [
                "# PMID 41261131 LLM-tRNAAlign Sprinzl check",
                "",
                f"LLM-tRNAAlign repo: `{LLM_TRNA_REPO}`",
                "",
                "Online `https://llm-trna.lumoxuan.cn/api/*` returned nginx 504 during this check, so this run used the local repo implementation with `LLM_POSTCHECK=0`.",
                "",
                f"Rows checked: {len(summaries)}",
                f"Origin non-gap coordinate labels all equal current DB JSON: {all_origin_ok}",
                f"Sup non-gap coordinate labels all equal current DB JSON: {all_sup_ok}",
                f"Rows with non-gap coordinate/base differences: {len(serious_rows)}",
                "",
                "The local tool emits a fuller Sprinzl coordinate row that includes canonical gap-only labels such as `-1`, unused `V*` positions, and `74-76`. Current DB JSON is compact and omits many gap-only labels, but this does not change the non-gap base-to-coordinate assignment when the equality flags are true.",
                "",
                f"Detailed TSV: `{OUT_TSV}`",
                f"Raw CSV directory: `{OUT_DIR}`",
                f"Run logs: `{LOG_DIR}`",
            ]
        )
        + "\n"
    )

    print(OUT_TSV)
    print(OUT_NOTE)
    print("rows", len(summaries))
    print("origin_labels_all_equal", all_origin_ok)
    print("sup_labels_all_equal", all_sup_ok)
    print("serious_rows", len(serious_rows))


if __name__ == "__main__":
    main()
