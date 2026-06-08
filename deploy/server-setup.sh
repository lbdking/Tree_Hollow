#!/bin/bash
# 在云服务器上执行（root 用户）
# 用法: bash deploy/server-setup.sh
set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'
log() { echo -e "${GREEN}[$(date +%H:%M:%S)]${NC} $1"; }
warn() { echo -e "${YELLOW}[!]${NC} $1"; }

cd "$(dirname "$0")/.."
ROOT=$(pwd)

# ---------- 1. 安装 Docker ----------
if ! command -v docker &>/dev/null; then
    log "🐳 安装 Docker ..."
    curl -fsSL https://get.docker.com | bash -s docker --mirror Aliyun
    systemctl enable --now docker
else
    log "Docker 已安装: $(docker --version)"
fi

if ! docker compose version &>/dev/null; then
    log "📦 安装 docker-compose-plugin ..."
    if command -v apt &>/dev/null; then
        apt-get update && apt-get install -y docker-compose-plugin
    elif command -v yum &>/dev/null; then
        yum install -y docker-compose-plugin
    fi
fi

# ---------- 2. 配置 Docker 镜像加速（中国服务器更快）----------
if [ ! -f /etc/docker/daemon.json ]; then
    log "⚡ 配置 Docker 国内镜像加速 ..."
    mkdir -p /etc/docker
    cat > /etc/docker/daemon.json <<'EOF'
{
  "registry-mirrors": [
    "https://docker.m.daocloud.io",
    "https://docker.1panel.live",
    "https://hub.rat.dev"
  ]
}
EOF
    systemctl restart docker
fi

# ---------- 3. 准备 .env ----------
if [ ! -f "$ROOT/.env" ]; then
    log "📝 生成 .env（请稍后编辑确认密钥）"
    cp "$ROOT/.env.example" "$ROOT/.env"
    # 自动生成强随机 JWT_SECRET
    RAND=$(head -c 48 /dev/urandom | base64 | tr -d '+/=' | head -c 48)
    sed -i "s|JWT_SECRET=.*|JWT_SECRET=${RAND}|" "$ROOT/.env"
    warn "已生成随机 JWT_SECRET。如需修改 DEEPSEEK_API_KEY，请编辑 $ROOT/.env"
fi

# ---------- 4. 防火墙：放开端口 ----------
if command -v ufw &>/dev/null && ufw status | grep -q "Status: active"; then
    log "🔓 开放端口 5173/5174/8000 ..."
    ufw allow 5173/tcp
    ufw allow 5174/tcp
    ufw allow 8000/tcp
fi
if command -v firewall-cmd &>/dev/null && systemctl is-active firewalld &>/dev/null; then
    firewall-cmd --permanent --add-port=5173/tcp
    firewall-cmd --permanent --add-port=5174/tcp
    firewall-cmd --permanent --add-port=8000/tcp
    firewall-cmd --reload
fi

# ---------- 5. 构建并启动 ----------
log "🏗️  开始构建镜像（首次约 3-5 分钟）..."
cd "$ROOT"
docker compose build

log "🚀 启动所有服务 ..."
docker compose up -d

log "⏳ 等待 30 秒让服务初始化 ..."
sleep 30

log "📊 服务状态："
docker compose ps

# ---------- 6. 输出访问信息 ----------
PUBLIC_IP=$(curl -s ifconfig.me 2>/dev/null || curl -s ip.sb 2>/dev/null || echo "你的公网IP")

echo ""
echo "════════════════════════════════════════════════════════"
echo -e "${GREEN}🎉 部署完成！${NC}"
echo "════════════════════════════════════════════════════════"
echo "  📱 移动端    http://${PUBLIC_IP}:5173"
echo "  💻 管理后台  http://${PUBLIC_IP}:5174"
echo "  🐍 后端 API  http://${PUBLIC_IP}:8000/docs"
echo ""
echo "  默认账号：admin / admin123"
echo "         2024001 / 123456"
echo ""
echo "  常用命令："
echo "    查看日志：cd $ROOT && docker compose logs -f backend"
echo "    重启服务：cd $ROOT && docker compose restart"
echo "    停止全部：cd $ROOT && docker compose down"
echo "════════════════════════════════════════════════════════"
echo ""
warn "⚠️  云服务器安全组也要放开 5173 / 5174 / 8000 端口（在云控制台配置）"
