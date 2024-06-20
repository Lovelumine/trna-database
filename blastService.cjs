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

    exec('blastn -query query.fasta -subject query.fasta -outfmt "6 qseqid sseqid pident length evalue bitscore gaps"', (error, stdout, stderr) => {
        if (error) {
            res.status(500).json({ error: stderr });
            return;
        }
        
        const [qseqid, sseqid, pident, length, evalue, bitscore, gaps] = stdout.split('\t');
        res.json({ alignment: stdout, eValue: evalue, score: bitscore, gaps });
    });
});

app.listen(port, () => {
    console.log(`BLAST service running at http://localhost:${port}`);
});
