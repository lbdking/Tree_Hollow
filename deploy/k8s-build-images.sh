#!/bin/bash
# 本地执行：构建 3 个 Docker 镜像并打包成 tar 文件，方便上传到服务器
# 用法: bash deploy/k8s-build-images.sh
set -e

cd "$(dirname "$0")/.."
ROOT=$(pwd)
OUT_DIR="/tmp/tree-hollow-images"
mkdir -p "$OUT_DIR"

if ! command -v docker &>/dev/null; then
    echo "❌ 本地未安装 Docker，无法 build 镜像"
    echo "   请先 brew install --cask docker 并启动 Docker Desktop"
    exit 1
fi

build_and_save() {
    local name=$1
    local context=$2
    local image="tree-hollow-${name}:1.0"
    echo ""
    echo "🏗️  构建 $image ..."
    docker build -t "$image" "$context"
    echo "💾 导出 $OUT_DIR/${name}.tar ..."
    docker save -o "$OUT_DIR/${name}.tar" "$image"
}

build_and_save "backend"  "$ROOT/backend"
build_and_save "mobile"   "$ROOT/frontend-mobile"
build_and_save "admin"    "$ROOT/frontend-admin"

echo ""
echo "📦 打包 K8s manifests + 镜像 ..."
PACK="/tmp/tree-hollow-k8s-pack.tar.gz"
tar -czf "$PACK" \
    -C "$ROOT" k8s deploy \
    -C "$OUT_DIR" backend.tar mobile.tar admin.tar

ls -lh "$PACK"
echo ""
echo "✅ 完成！下一步把 $PACK 传到服务器："
echo ""
echo "   scp $PACK root@180.184.78.22:/opt/"
echo ""
echo "   ssh root@180.184.78.22"
echo "   mkdir -p /opt/tree-hollow && tar -xzf /opt/tree-hollow-k8s-pack.tar.gz -C /opt/tree-hollow"
echo "   cd /opt/tree-hollow && bash deploy/k8s-apply.sh"
