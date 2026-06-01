#!/bin/bash
# 在你的 Mac 本地执行，把整个项目（含 Dockerfile）打包成一个 tar.gz
# 用法: bash deploy/build-and-pack.sh
set -e

cd "$(dirname "$0")/.."
ROOT=$(pwd)
NAME="tree-hollow"
OUT="/tmp/${NAME}-deploy.tar.gz"

echo "📦 打包项目（不含 node_modules / .venv / dist / data）..."
tar --exclude='./.git' \
    --exclude='./*/node_modules' \
    --exclude='./*/dist' \
    --exclude='./backend/.venv' \
    --exclude='./backend/data' \
    --exclude='./backend/__pycache__' \
    --exclude='./*/__pycache__' \
    --exclude='./.DS_Store' \
    -czf "$OUT" \
    -C "$ROOT" \
    backend frontend-mobile frontend-admin docker-compose.yml .env.example deploy

ls -lh "$OUT"
echo "✅ 已生成: $OUT"
echo ""
echo "下一步：把它传到服务器（替换 root@your-server-ip）"
echo "  scp $OUT root@your-server-ip:/opt/"
echo "然后在服务器上执行："
echo "  ssh root@your-server-ip"
echo "  cd /opt && tar -xzf ${NAME}-deploy.tar.gz -C ${NAME} --strip-components=0"
echo "  # 或者更简单："
echo "  mkdir -p /opt/${NAME} && tar -xzf /opt/${NAME}-deploy.tar.gz -C /opt/${NAME}"
echo "  cd /opt/${NAME} && bash deploy/server-setup.sh"
