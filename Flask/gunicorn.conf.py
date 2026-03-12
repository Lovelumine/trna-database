# -*- coding: utf-8 -*-
import multiprocessing
import os

# 监听地址（改端口就改这里）
bind = "0.0.0.0:8010"

# worker 数量：CPU 密集 + Biopython 对齐较重，建议先用 1~2 做稳定性验证
# 生产里可按 CPU 调整，比如：workers = multiprocessing.cpu_count() // 2 or 2
workers = 2

# 同步 worker 对 CPU 密集更直观；若用 gevent 需要确保依赖兼容
worker_class = "sync"

# 每个 worker 的连接数上限（sync 下表示 backlog 队列大小）
backlog = 2048

# 超时设置
# AI 聊天请求可能串行经过 conversation router、retrieval judge、final critic、
# 最终回答生成等多个模型调用，总耗时会明显高于单次 llm_timeout。
# 如果这里和 llm_timeout 持平，gunicorn 会在 SSE 仍在进行时杀掉 worker，
# 前端/Vite 侧就会看到截断的 chunked 响应错误。
timeout = int(os.getenv("GUNICORN_TIMEOUT", "600"))
graceful_timeout = int(os.getenv("GUNICORN_GRACEFUL_TIMEOUT", "90"))

# 日志（按需调整）
accesslog = "-"
errorlog = "-"
loglevel = "info"

# 关闭线程（用多进程即可）
threads = 1
