# -*- coding: utf-8 -*-
import os

from app import create_app

# 供 Gunicorn 使用的入口
app = create_app()

# 便于本地直接运行（仅开发用）
if __name__ == "__main__":
    # 单进程、禁线程（Biopython 在多线程下有时不稳定）
    host = os.getenv("ENSURE_BACKEND_HOST", "0.0.0.0")
    port = int(os.getenv("ENSURE_BACKEND_PORT", "8010"))
    app.run(host=host, port=port, threaded=False)
