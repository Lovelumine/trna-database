# -*- coding: utf-8 -*-
import multiprocessing

# 监听地址（改端口就改这里）
bind = "0.0.0.0:8000"

# worker 数量：CPU 密集 + Biopython 对齐较重，建议先用 1~2 做稳定性验证
# 生产里可按 CPU 调整，比如：workers = multiprocessing.cpu_count() // 2 or 2
workers = 2

# 同步 worker 对 CPU 密集更直观；若用 gevent 需要确保依赖兼容
worker_class = "sync"

# 每个 worker 的连接数上限（sync 下表示 backlog 队列大小）
backlog = 2048

# 超时设置
timeout = 120
graceful_timeout = 30

# 日志（按需调整）
accesslog = "-"
errorlog = "-"
loglevel = "info"

# 关闭线程（用多进程即可）
threads = 1
