#!/bin/sh
set -e

# 等待 MySQL 就绪
echo "⏳ 等待 MySQL ..."
python - <<'PY'
import os, time, socket
url = os.environ.get("DATABASE_URL", "")
host = "mysql"
port = 3306
if "@" in url:
    after = url.split("@", 1)[1]
    host = after.split(":")[0]
    if ":" in after.split("/")[0]:
        port = int(after.split(":")[1].split("/")[0])
for i in range(60):
    try:
        with socket.create_connection((host, port), 2):
            print(f"✅ MySQL {host}:{port} 已就绪")
            break
    except OSError:
        time.sleep(1)
else:
    print("❌ MySQL 等待超时")
    raise SystemExit(1)
PY

# 灌种子数据（已存在则自动跳过）
echo "🌱 初始化数据库 + seed ..."
python seed.py || echo "⚠️ seed 跳过/失败，继续启动"

# 启动服务
echo "🚀 启动 FastAPI ..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
