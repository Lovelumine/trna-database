const express = require('express');
const fs = require('fs');
const { exec } = require('child_process');
const crypto = require('crypto');
const app = express();
const port = 3945;

app.use(express.json());

app.post('/run-blast', (req, res) => {
  const { expect, wordSize, database, sequenceFormat, querySequence } = req.body;

  // 生成唯一哈希值
  const hash = crypto.createHash('sha256').update(querySequence + Date.now().toString()).digest('hex');
  const queryFile = `query_${hash}.fasta`;
  const resultFileTmp = `results_${hash}.tmp`;
  const resultFile = `results_${hash}.txt`;

  // 将查询序列写入临时文件
  fs.writeFileSync(queryFile, querySequence);

  // 运行 BLAST 命令
  exec(`blastn -query ${queryFile} -db /home/yingying/WebstormProjects/trna-database/src/assets/data/blast_db/all_db -out ${resultFileTmp} -outfmt "6 qseqid sseqid pident length mismatch gapopen qstart qend sstart send evalue bitscore qseq sseq stitle"`, (error, stdout, stderr) => {
    if (error) {
      console.error(`Error executing BLAST: ${error}`);
      return res.status(500).send('Error running BLAST');
    }

    // 添加输出格式说明到结果文件的第一行
    const resultHeader = "qseqid\tsseqid\tpident\tlength\tmismatch\tgapopen\tqstart\tqend\tsstart\tsend\tevalue\tbitscore\tqseq\tsseq\tstitle\n";
    const resultContent = fs.readFileSync(resultFileTmp, 'utf-8');
    const finalResult = resultHeader + resultContent;

    // 删除临时文件
    fs.unlinkSync(queryFile);
    fs.unlinkSync(resultFileTmp);

    // 返回结果
    res.send(finalResult);
  });
});

app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});
