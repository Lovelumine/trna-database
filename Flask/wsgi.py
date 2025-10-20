# -*- coding: utf-8 -*-
from app import create_app

# 供 Gunicorn 使用的入口
app = create_app()

# 便于本地直接运行（仅开发用）
if __name__ == "__main__":
    # 单进程、禁线程（Biopython 在多线程下有时不稳定）
    app.run(host="0.0.0.0", port=8000, threaded=False)
