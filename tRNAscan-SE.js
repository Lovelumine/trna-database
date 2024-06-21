import express from 'express';
import { exec } from 'child_process';
import fs from 'fs';
import path from 'path';
import crypto from 'crypto';
import os from 'os';

const app = express();
const port = 3456;

app.use(express.json());

app.post('/scan', (req, res) => {
    const { sequence } = req.body;

    if (!sequence) {
        res.status(400).send('序列不能为空');
        return;
    }

    // 将非A、U、G、C的碱基替换为N
    const cleanedSequence = sequence.replace(/[^AUGC]/gi, 'N');

    // 生成哈希值作为文件名的一部分
    const hash = crypto.createHash('md5').update(cleanedSequence).digest('hex');

    // 创建临时文件夹
    const tempDir = path.join(os.tmpdir(), 'trnascan_temp');
    if (!fs.existsSync(tempDir)) {
        fs.mkdirSync(tempDir);
    }

    const inputFilePath = path.join(tempDir, `input_${hash}.fasta`);
    const outputFilePath = path.join(tempDir, `output_${hash}.txt`);
    const fastaContent = `>input_sequence\n${cleanedSequence}\n`;
    
    fs.writeFileSync(inputFilePath, fastaContent);

    exec(`tRNAscan-SE -E -f ${outputFilePath} ${inputFilePath}`, (error, stdout, stderr) => {
        if (error) {
            res.status(500).send(stderr);
            return;
        }

        fs.readFile(outputFilePath, 'utf8', (err, data) => {
            if (err) {
                res.status(500).send(err.message);
                return;
            }

            // 解析 output.txt 文件，提取 Str 部分
            const strMatch = data.match(/Str: (.+)/);
            let str = strMatch ? strMatch[1] : 'Unable to obtain secondary structure through tRNAscan SE';

            // 检查是否因为替换了碱基而导致错误
            if (!strMatch) {
                str = 'Unable to obtain secondary structure through tRNAscan SE after replacing non-AUGC bases with N';
            }

            // 替换括号
            const formattedStr = str.replace(/>/g, '(').replace(/</g, ')');
            res.json({ str: formattedStr });

            // 删除临时文件
            fs.unlink(inputFilePath, (err) => {
                if (err) console.error(`删除文件 ${inputFilePath} 失败:`, err);
            });

            fs.unlink(outputFilePath, (err) => {
                if (err) console.error(`删除文件 ${outputFilePath} 失败:`, err);
            });
        });
    });
});

app.listen(port, () => {
    console.log(`tRNAscan-SE service running at http://localhost:${port}`);
});
