#!/usr/bin/env bash
#
# restart_searchservice.sh
#
# 启动并每隔 1800 秒（半小时）重启一次 searchservice.py。
# 使用方法：
#   chmod +x restart_searchservice.sh
#   ./restart_searchservice.sh

# ==== 配置区 ====
PYTHON_BIN=python
SERVICE_SCRIPT="./searchservice.py"
RESTART_INTERVAL=180

# 启动函数
start_service() {
  echo "[$(date +"%F %T")] 启动服务：$PYTHON_BIN $SERVICE_SCRIPT"
  $PYTHON_BIN $SERVICE_SCRIPT &
  SERVICE_PID=$!
  echo "  -> PID = $SERVICE_PID"
}

# 停止函数（用 fuser -k 直接干掉占 8000/tcp 的进程）
stop_service() {
  echo "[$(date +"%F %T")] 停止服务：清理 8000/tcp 端口"
  if fuser -k 8000/tcp 2>/dev/null; then
    echo "  -> 已杀掉占用 8000 端口的进程"
  else
    echo "  -> 未检测到占用 8000 端口的进程"
  fi
}

# 主循环
while true; do
  start_service

  # 等待指定时间后重启
  for ((i=RESTART_INTERVAL; i>0; i--)); do
    sleep 1
    # 如果服务意外退出，立即跳出循环，马上重启
    if ! kill -0 "$SERVICE_PID" 2>/dev/null; then
      echo "[$(date +"%F %T")] 服务已退出，准备重启"
      break
    fi
  done

  stop_service
  echo "[$(date +"%F %T")] 等待 1 秒后重启..."
  sleep 1
done