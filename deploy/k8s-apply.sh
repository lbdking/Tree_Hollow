#!/bin/bash
# 在服务器上执行：导入镜像 → 创建 Secret → kubectl apply
# 用法（服务器）: bash deploy/k8s-apply.sh
set -e

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
log()  { echo -e "${GREEN}[$(date +%H:%M:%S)]${NC} $1"; }
warn() { echo -e "${YELLOW}[!]${NC} $1"; }
die()  { echo -e "${RED}[ERR]${NC} $1"; exit 1; }

cd "$(dirname "$0")/.."
ROOT=$(pwd)

# ---------- 0. 检查工具 ----------
command -v kubectl &>/dev/null || die "未找到 kubectl，请先安装"
kubectl cluster-info &>/dev/null || die "kubectl 无法访问集群，请检查 ~/.kube/config"

# ---------- 1. 导入镜像（兼容 docker / containerd / k3s） ----------
import_image() {
    local tar=$1
    local img=$2
    [ -f "$tar" ] || { warn "$tar 不存在，跳过"; return; }
    log "📥 导入 $img ..."
    if command -v docker &>/dev/null; then
        docker load -i "$tar"
        # 若是 k3s/containerd，再额外导一份
        if command -v ctr &>/dev/null && [ -S /run/containerd/containerd.sock ]; then
            ctr -n k8s.io images import "$tar" 2>/dev/null || true
        fi
    elif command -v ctr &>/dev/null; then
        ctr -n k8s.io images import "$tar"
    elif command -v k3s &>/dev/null; then
        k3s ctr images import "$tar"
    else
        die "未找到 docker/ctr/k3s 任一镜像导入工具"
    fi
}

import_image "$ROOT/backend.tar" "tree-hollow-backend:1.0"
import_image "$ROOT/mobile.tar"  "tree-hollow-mobile:1.0"
import_image "$ROOT/admin.tar"   "tree-hollow-admin:1.0"

# ---------- 2. 应用 manifests ----------
log "📦 创建命名空间 + 配置 ..."
kubectl apply -f "$ROOT/k8s/00-namespace.yaml"
kubectl apply -f "$ROOT/k8s/01-config.yaml"

# ---------- 3. 用强随机 JWT 覆盖默认 Secret 占位符 ----------
RAND=$(head -c 48 /dev/urandom | base64 | tr -d '+/=' | head -c 48)
DEEPSEEK_KEY="${DEEPSEEK_API_KEY:-sk-请通过环境变量 DEEPSEEK_API_KEY 注入或修改 .env}"

log "🔐 注入随机 JWT_SECRET ..."
kubectl -n tree-hollow create secret generic backend-secret \
    --from-literal=JWT_SECRET="$RAND" \
    --from-literal=DEEPSEEK_API_KEY="$DEEPSEEK_KEY" \
    --dry-run=client -o yaml | kubectl apply -f -

log "🐬 部署 MySQL ..."
kubectl apply -f "$ROOT/k8s/02-mysql.yaml"

log "📮 部署 Redis ..."
kubectl apply -f "$ROOT/k8s/03-redis.yaml"

log "⏳ 等待 MySQL 就绪（最多 3 分钟）..."
kubectl -n tree-hollow rollout status statefulset/mysql --timeout=180s || warn "MySQL 启动较慢，继续..."

log "🐍 部署后端 ..."
kubectl apply -f "$ROOT/k8s/04-backend.yaml"

log "🎨 部署前端 ..."
kubectl apply -f "$ROOT/k8s/05-frontend.yaml"

log "⏳ 等待后端就绪 ..."
kubectl -n tree-hollow rollout status deployment/backend --timeout=120s || warn "后端启动较慢..."

# ---------- 4. 输出状态 ----------
echo ""
echo "════════════════════════════════════════════════════"
log "📊 当前状态"
echo "════════════════════════════════════════════════════"
kubectl -n tree-hollow get all
echo ""

NODE_IP=$(curl -s --max-time 5 ifconfig.me 2>/dev/null || hostname -I | awk '{print $1}')
echo "════════════════════════════════════════════════════"
echo -e "${GREEN}🎉 部署完成！${NC}"
echo "════════════════════════════════════════════════════"
echo "  📱 移动端    http://${NODE_IP}:30517"
echo "  💻 管理后台  http://${NODE_IP}:30518"
echo "  🐍 后端 API  http://${NODE_IP}:30800/docs"
echo ""
echo "  默认账号：admin / admin123"
echo "         2024001 / 123456"
echo ""
echo "  常用命令："
echo "    查看 Pod   ：kubectl -n tree-hollow get pods"
echo "    后端日志   ：kubectl -n tree-hollow logs -f deploy/backend"
echo "    重启后端   ：kubectl -n tree-hollow rollout restart deploy/backend"
echo "    进容器     ：kubectl -n tree-hollow exec -it deploy/backend -- bash"
echo "    清理一切   ：kubectl delete namespace tree-hollow"
echo "════════════════════════════════════════════════════"
warn "⚠️  云服务器安全组放开 30517 / 30518 / 30800 端口"
