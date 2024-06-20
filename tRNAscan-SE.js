import express from 'express';
import multer from 'multer';
import { exec } from 'child_process';
import path from 'path';
import fs from 'fs';

const app = express();
const upload = multer({ dest: 'uploads/' });

// 通用 tRNAscan-SE 接口
app.post('/scan', upload.single('file'), (req, res) => {
  const filePath = path.join(path.resolve(), req.file.path);
  const options = req.body.options || ''; // 从请求中获取 tRNAscan-SE 参数选项

  exec(`tRNAscan-SE ${options} ${filePath}`, (error, stdout, stderr) => {
    if (error) {
      console.error(`Error: ${stderr}`);
      res.status(500).send(stderr);
      return;
    }
    res.send(stdout);

    // 删除上传的文件
    fs.unlink(filePath, (err) => {
      if (err) {
        console.error(err);
      }
    });
  });
});

console.log("ok");

const PORT = process.env.PORT || 3456;
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
