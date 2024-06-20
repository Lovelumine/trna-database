const express = require('express');
const { exec } = require('child_process');
const fs = require('fs');
const app = express();
const port = 3457;

app.use(express.json());

app.post('/align', (req, res) => {
    const { sequence1, sequence2 } = req.body;

    const fastaContent = `>Seq1\n${sequence1}\n>Seq2\n${sequence2}\n`;
    fs.writeFileSync('query.fasta', fastaContent);

    exec('blastn -query query.fasta -subject query.fasta -outfmt 0', (error, stdout, stderr) => {
        if (error) {
            res.status(500).json({ error: stderr });
            return;
        }

        // 解析比对部分，只提取第一个比对结果
        const alignmentRegex = /Query\s+\d+.*\n.*\nSbjct\s+\d+.*/g;
        const alignments = stdout.match(alignmentRegex);
        const alignment = alignments ? alignments[0].replace(/\n/g, '<br>') : 'No alignment found';

        // 提取E值、得分和缺口数
        const eValueMatch = stdout.match(/Expect\s*=\s*([\d.e-]+)/);
        const scoreMatch = stdout.match(/Score\s*=\s*([\d.e-]+)\s*bits/);
        const gapsMatch = stdout.match(/Gaps\s*=\s*(\d+\/\d+\s*\(\d+%\))/);

        const eValue = eValueMatch ? eValueMatch[1] : '';
        const score = scoreMatch ? scoreMatch[1] : '';
        const gaps = gapsMatch ? gapsMatch[1] : '';

        res.json({ alignment, eValue, score, gaps });
    });
});

app.listen(port, () => {
    console.log(`BLAST service running at http://localhost:${port}`);
});
