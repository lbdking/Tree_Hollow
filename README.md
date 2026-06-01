# 🌳 校园心理健康互助与情绪树洞系统

匿名倾诉 · 互助陪伴 · 心理科普 · 预约咨询 · AI 倾听

---

## ⚡ 快速开始（新同学请直接看这里）

> **拉到项目想立刻跑起来？** 你只需要做这 3 步：

1. **克隆仓库**
   ```bash
   git clone git@github.com:lbdking/Tree_Hollow.git
   cd Tree_Hollow
   ```

2. **用 Trae 打开项目**（Trae 是基于 VSCode 的 AI IDE，支持 macOS / Windows / Linux）
   ```bash
   code .
   ```

3. **把 [docs/新同学上手指南.md](docs/新同学上手指南.md) 完整发给 Trae AI**，并说：
   > "请你按这个文档帮我把项目跑起来。"

   Trae 会自动：
   - ✅ 检测你的操作系统（macOS / Windows / Linux）
   - ✅ 安装 Python / Node / MySQL / Redis 等依赖
   - ✅ 初始化数据库 + 灌入测试数据
   - ✅ 启动后端 + 移动端 + 管理后台 3 个服务
   - ✅ 输出访问地址 + 测试账号清单

   **预计耗时**：5-10 分钟（视网络）

> 📖 完整执行 Runbook：[docs/新同学上手指南.md](docs/新同学上手指南.md)
>
> � 测试账号一览：[docs/测试账号.md](docs/测试账号.md)
>
> �💡 如果不用 AI Agent，也可以手动按指南里的 Step 0~8 执行，每步都有【验收】检查。

---

## ✨ 模块一览

| 模块 | 内容 |
|---|---|
| 用户与匿名身份 | 学号注册登录、JWT 鉴权、楼内一致的随机匿名昵称（如 `温柔的小猫#3829`） |
| 情绪树洞 | 匿名发帖、心情标签、回复、点赞、举报、危机词识别 |
| 心理科普 | 文章 / 视频内容、按分类筛选、浏览统计 |
| 情绪调节工具 | 4-4-4 呼吸训练（含动画）、月度情绪打卡日历 |
| 互助小组 | 主题小组、加入退出、活动报名（异步） |
| 预约咨询 | 咨询师列表、可约时段、提交预约、状态流转 |
| 消息通知 | 回复 / 活动 / 预约 / 危机系统提醒，未读计数 |
| AI 倾听 | DeepSeek 流式对话，进程内缓存 + 落盘历史 |
| 管理后台 | 数据看板（ECharts）、内容审核、举报处理、咨询师管理 |

## 🧱 技术栈

- 后端：Python 3.9 / FastAPI / SQLAlchemy 2 / MySQL 8 / Redis / DeepSeek
- 移动端：Vue 3 + Vite + Vant + Pinia + Vue Router
- 管理后台：Vue 3 + Vite + Element Plus + ECharts
- 数据库：≥10 张表（user / anonymous_profile / hollow_post / hollow_reply / hollow_like / report / article / mood_record / breathing_record / support_group / group_member / group_activity / activity_enrollment / counselor / appointment / notification / ai_chat_session / ai_chat_message）

## 🚀 本地启动

### 0. 安装基础环境（已装可跳过）

```bash
brew install mysql redis
# 初始化 MySQL（首次）
/opt/homebrew/opt/mysql/bin/mysqld --initialize-insecure \
  --user=$(whoami) \
  --basedir=/opt/homebrew/opt/mysql \
  --datadir=/opt/homebrew/var/mysql
```

### 1. 启动 MySQL & Redis

```bash
# 推荐 brew services（如有 LaunchAgents 权限）：
brew services start mysql
brew services start redis

# 或前台启动（任选其一）：
/opt/homebrew/opt/mysql/bin/mysqld_safe --datadir=/opt/homebrew/var/mysql &
/opt/homebrew/opt/redis/bin/redis-server /opt/homebrew/etc/redis.conf &
```

创建数据库：
```bash
/opt/homebrew/opt/mysql/bin/mysql -u root -e \
  "CREATE DATABASE IF NOT EXISTS tree_hollow DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

### 2. 启动后端

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 灌入测试数据（首次/重置时执行）
python seed.py

# 运行
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

接口文档：http://127.0.0.1:8000/docs

### 3. 启动移动端

```bash
cd frontend-mobile
npm install
npm run dev
# 访问 http://127.0.0.1:5173
```

> 浏览器调出移动端模拟（Chrome DevTools → Toggle device toolbar）效果最佳。

### 4. 启动管理后台

```bash
cd frontend-admin
npm install
npm run dev
# 访问 http://127.0.0.1:5174
```

## 👤 测试账号

| 角色 | 账号 | 密码 |
|---|---|---|
| 管理员 | `admin` | `admin123` |
| 学生 | `2024001` `2024002` `2024003` | `123456` |
| 咨询师 | `counselor01` `counselor02` | `123456` |

## 📁 目录结构

```
Tree_Hollow/
├── backend/              # FastAPI 后端
│   ├── app/
│   │   ├── api/v1/endpoints/   # 路由（auth/hollow/content/group/appointment/notification/ai/admin）
│   │   ├── core/               # 配置/数据库/安全/依赖
│   │   ├── models/             # SQLAlchemy 模型
│   │   ├── schemas/            # Pydantic
│   │   ├── services/           # 业务（identity/notify/ai_service）
│   │   ├── utils/              # 工具（anonymizer/crisis）
│   │   └── main.py
│   ├── seed.py                 # 测试数据
│   ├── requirements.txt
│   └── .env
├── frontend-mobile/      # Vue3 + Vant 移动端
└── frontend-admin/       # Vue3 + Element Plus 管理后台
```

## 💡 关键设计

- **匿名身份稳定性**：`anonymous_profile` 表按 `(user_id, post_id)` 持久化生成的随机昵称，同一用户在同一帖子下保持一致，跨帖无法关联。
- **危机词识别**：发帖 / AI 聊天检测高风险词，命中后系统自动推送热线 + 引导预约咨询。
- **AI 上下文**：进程内 `dict[session_id -> messages]` 内存缓存（窗口 20 条），同步落盘到 `data/ai_cache.json` 与 MySQL `ai_chat_message`，进程重启后懒加载。
- **流式 AI**：FastAPI `StreamingResponse` + DeepSeek 兼容 OpenAI SDK，前端使用 fetch 流式读取。

## 🔐 配置（backend/.env）

```env
DATABASE_URL=mysql+pymysql://root:@127.0.0.1:3306/tree_hollow?charset=utf8mb4
REDIS_URL=redis://127.0.0.1:6379/0
DEEPSEEK_API_KEY=sk-xxxxxx
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
```

---

愿这个小小的树洞，能成为更多人的温柔角落 💗
