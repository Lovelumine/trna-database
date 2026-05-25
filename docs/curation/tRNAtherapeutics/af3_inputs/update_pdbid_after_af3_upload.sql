-- Run only after AF3 CIF files are uploaded to MinIO and verified.
START TRANSACTION;
UPDATE Engineered_sup_tRNA SET `pdbid` = 'PRF' WHERE PMID = 30778053 AND ENSURE_ID = 'ensure-364';
UPDATE Engineered_sup_tRNA SET `pdbid` = 'PRA' WHERE PMID = 41261131 AND ENSURE_ID = '1200';
UPDATE Engineered_sup_tRNA SET `pdbid` = 'PRB' WHERE PMID = 41261131 AND ENSURE_ID = '1204';
UPDATE Engineered_sup_tRNA SET `pdbid` = 'PRC' WHERE PMID = 41261131 AND ENSURE_ID = '1210';
UPDATE Engineered_sup_tRNA SET `pdbid` = 'PRD' WHERE PMID = 41261131 AND ENSURE_ID = '1211';
UPDATE Engineered_sup_tRNA SET `pdbid` = 'PRE' WHERE PMID = 41261131 AND ENSURE_ID = '1212';
COMMIT;
