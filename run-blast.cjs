const express = require('express');
const fs = require('fs');
const { exec } = require('child_process');
const crypto = require('crypto');
const app = express();
const port = 3945;

app.use(express.json());

// 添加日志中间件，用于记录所有请求
app.use((req, res, next) => {
  console.log(`[${new Date().toISOString()}] Received ${req.method} request at ${req.url}`);
  next();
});

app.post('/run-blast', (req, res) => {
  const { expect, wordSize, database, sequenceFormat, querySequence } = req.body;

  console.log(`[INFO] Received /run-blast request with body:`, req.body);

  if (!querySequence) {
    console.error('[ERROR] Missing querySequence in request body');
    return res.status(400).send('Missing querySequence in request body');
  }

  // 生成唯一哈希值
  const hash = crypto.createHash('sha256').update(querySequence + Date.now().toString()).digest('hex');
  const queryFile = `query_${hash}.fasta`;
  const resultFileTmp = `results_${hash}.tmp`;

  console.log(`[INFO] Generated unique file names: queryFile=${queryFile}, resultFileTmp=${resultFileTmp}`);

  try {
    // 将查询序列写入临时文件
    fs.writeFileSync(queryFile, querySequence);
    console.log(`[INFO] Query sequence written to ${queryFile}`);
  } catch (writeError) {
    console.error(`[ERROR] Failed to write query sequence to file: ${writeError}`);
    return res.status(500).send('Failed to process query sequence');
  }

  // 运行 BLAST 命令
  const blastCommand = `blastn -query ${queryFile} -db /home/yingying/Documents/trna-database/src/assets/data/blast_db/all_db -out ${resultFileTmp} -outfmt "6 qseqid sseqid pident length mismatch gapopen qstart qend sstart send evalue bitscore qseq sseq stitle"`;
  console.log(`[INFO] Executing BLAST command: ${blastCommand}`);

  exec(blastCommand, (error, stdout, stderr) => {
    if (error) {
      console.error(`[ERROR] Error executing BLAST: ${error}`);
      return res.status(500).send('Error running BLAST');
    }

    console.log(`[INFO] BLAST command executed successfully`);

    try {
      // 添加输出格式说明到结果文件的第一行
      const resultHeader = "qseqid\tsseqid\tpident\tlength\tmismatch\tgapopen\tqstart\tqend\tsstart\tsend\tevalue\tbitscore\tqseq\tsseq\tstitle\n";
      const resultContent = fs.readFileSync(resultFileTmp, 'utf-8');
      const finalResult = resultHeader + resultContent;

      // 打印结果到控制台
      console.log(`[INFO] BLAST result content:\n${finalResult}`);

      console.log(`[INFO] Result file read successfully`);

      // 删除临时文件
      fs.unlinkSync(queryFile);
      fs.unlinkSync(resultFileTmp);

      console.log(`[INFO] Temporary files deleted: ${queryFile}, ${resultFileTmp}`);

      // 返回结果
      res.send(finalResult);
    } catch (resultError) {
      console.error(`[ERROR] Failed to process BLAST results: ${resultError}`);
      return res.status(500).send('Failed to process BLAST results');
    }
  });
});

app.listen(port, () => {
  console.log(`[INFO] Server running at http://localhost:${port}`);
});