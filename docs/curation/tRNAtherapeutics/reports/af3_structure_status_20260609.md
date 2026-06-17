# AF3 Structure Status

Review date: 2026-06-09

Scope: `/tRNAtherapeutics` / `Engineered_sup_tRNA` AF3 tertiary-structure status.

## Summary

- Latest local live snapshot checked: `field-curation-workdir/full_tRNAtherapeutics/snapshots/Engineered_sup_tRNA_20260608_085056.tsv`.
- Total rows in snapshot: 1136.
- Rows with blank `pdbid`: 0.
- Existing AF3 plan rows: 6.
- Local AF3 output directory: `field-curation-workdir/af3_outputs/ensure-trna-missing-pdbid/`.
- Public MinIO URL pattern used by the frontend: `https://minio.lumoxuan.cn/ensure/ensure-af3/{pdbid_lower}fold/seed-1_sample-{0..4}/model.cif`.
- Public URL check: all 30 CIF URLs for `PRA` through `PRF` returned HTTP 200 on 2026-06-09.

## AF3 Plan Rows

| PMID | ENSURE_ID | pdbid | job | sequence length | status |
|---|---|---|---|---:|---|
| 30778053 | ensure-364 | PRF | PRFFOLD | 84 | Local CIFs present; all 5 public `model.cif` URLs return 200. |
| 41261131 | 1200 | PRA | PRAFOLD | 83 | Local CIFs present; all 5 public `model.cif` URLs return 200. |
| 41261131 | 1204 | PRB | PRBFOLD | 83 | Local CIFs present; all 5 public `model.cif` URLs return 200. |
| 41261131 | 1210 | PRC | PRCFOLD | 83 | Local CIFs present; all 5 public `model.cif` URLs return 200. |
| 41261131 | 1211 | PRD | PRDFOLD | 83 | Local CIFs present; all 5 public `model.cif` URLs return 200. |
| 41261131 | 1212 | PRE | PREFOLD | 83 | Local CIFs present; all 5 public `model.cif` URLs return 200. |

## Public URL Check

All URLs below returned HTTP 200:

- `https://minio.lumoxuan.cn/ensure/ensure-af3/prafold/seed-1_sample-{0,1,2,3,4}/model.cif`
- `https://minio.lumoxuan.cn/ensure/ensure-af3/prbfold/seed-1_sample-{0,1,2,3,4}/model.cif`
- `https://minio.lumoxuan.cn/ensure/ensure-af3/prcfold/seed-1_sample-{0,1,2,3,4}/model.cif`
- `https://minio.lumoxuan.cn/ensure/ensure-af3/prdfold/seed-1_sample-{0,1,2,3,4}/model.cif`
- `https://minio.lumoxuan.cn/ensure/ensure-af3/prefold/seed-1_sample-{0,1,2,3,4}/model.cif`
- `https://minio.lumoxuan.cn/ensure/ensure-af3/prffold/seed-1_sample-{0,1,2,3,4}/model.cif`

## Ranking Scores

Best sample by local `*_ranking_scores.csv`:

| pdbid | job | best sample | best ranking_score |
|---|---|---:|---:|
| PRA | PRAFOLD | 1 | 0.5338400099007742 |
| PRB | PRBFOLD | 1 | 0.5348510317847434 |
| PRC | PRCFOLD | 1 | 0.5212934939348133 |
| PRD | PRDFOLD | 1 | 0.5248246353878667 |
| PRE | PREFOLD | 2 | 0.5143650593626239 |
| PRF | PRFFOLD | 2 | 0.4662225391338133 |

The frontend currently loads sample 0 first and allows manual switching among samples 0-4.

## Server Connectivity

Attempted SSH target: `ouyangzhuo@192.168.236.2` using `~/.ssh/biko`.

Result on 2026-06-09:

- `ping 192.168.236.2`: 100% packet loss.
- `nc -vz -w 5 192.168.236.2 22`: timed out.
- `ssh -o BatchMode=yes -o ConnectTimeout=8 -i ~/.ssh/biko ouyangzhuo@192.168.236.2 ...`: timed out.
- Local route exists via `tun0` for `192.168.236.0/24`, so this is currently a remote/VPN reachability issue rather than an SSH-key rejection.

Because the six AF3 jobs already have local outputs and public CIF URLs, no new AF3 prediction was submitted in this pass.
