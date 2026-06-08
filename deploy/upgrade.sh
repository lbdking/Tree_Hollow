#!/bin/bash
# 一键升级（拉新代码、重新构建、滚动重启）
# 用法（在服务器上）: bash deploy/upgrade.sh
set -e
cd "$(dirname "$0")/.."

echo "🔨 重新构建后端..."
docker compose build backend

echo "🚀 滚动重启..."
docker compose up -d --no-deps backend

echo "✅ 完成"
docker compose ps
