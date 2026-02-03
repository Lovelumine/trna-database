### ENSURE API Reference (Quick)

Base URL: same origin as the web app. Unless noted, all endpoints are JSON.

#### Health
- `GET /health` → `OK`

#### Chat (AI Yingying)
- `GET /chat/api/application/profile` → `{ data: { id: "ollama-local" } }`
- `GET /chat/api/open?application_id=...` → `{ data: "<chat_id>" }`
- `POST /chat/api/title` → `{ title: "..." }`
- `POST /chat/api/chat_message/<chat_id>` → SSE stream

Example:
```json
{ "message": "What is a natural sup-tRNA?", "model": "qwen3:32b", "stream": true }
```

#### Tables & Data
- `GET /table_info?table=Engineered_sup_tRNA`
- `POST /table_rows`
- `POST /table_stats`

`POST /table_rows` example:
```json
{
  "table": "coding_variation_cancer",
  "page": 1,
  "page_size": 10,
  "search_text": "TP53",
  "search_column": "GENE_NAME",
  "sort_by": "GENE_NAME",
  "sort_order": "asc",
  "case_insensitive": true
}
```

`POST /table_stats` example:
```json
{
  "table": "coding_variation_cancer",
  "stats": ["allele_heatmap", "disease_wordcloud"],
  "search_text": "TP53"
}
```

#### Sequence Alignment Search
- `POST /search`

Example (MySQL tables):
```json
{
  "query_seq": "ACGU...",
  "tables": ["Engineered_sup_tRNA"],
  "number": 5,
  "match": 2.0,
  "mismatch": -0.5,
  "gap_open": -2.0,
  "gap_extend": -1.0
}
```

Example (CSV URLs / local files):
```json
{
  "query_seq": "ACGU...",
  "csv_paths": ["https://.../file.csv"],
  "number": 5,
  "match": 2.0,
  "mismatch": -0.5,
  "gap_open": -2.0,
  "gap_extend": -1.0,
  "pmids": ["12345678"],
  "ensure_ids": ["ENSURE_0001"]
}
```

#### Download & Export
- `GET /download_table?table=...&format=csv|tsv&force=0&direct=0&async=0`
- `GET /download_table_status?table=...&format=csv|tsv`
- `GET /download_bundle_status?format=csv|tsv`
- `POST /export_warm` → `{ tables, formats }`

#### Fulltext Index
- `POST /table_fulltext_rebuild`

Example:
```json
{ "table": "coding_variation_cancer", "index_name": "ft_all", "columns": ["GENE_NAME", "ENSEMBL_ID"] }
```

#### External Literature (PubMed)
The AI assistant can call PubMed E-utilities when enabled (server-side tool, not a public HTTP endpoint).
Key parameters: `query`, `retmax`, `sort`, `mindate`, `maxdate`, or `pmids`.
When needed, it can also fetch abstracts via PubMed EFetch for specific PMIDs.
