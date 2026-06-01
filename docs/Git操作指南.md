# Git 操作指南

本文档介绍如何使用 Git 管理和维护本项目。

## 目录
- [Git 配置](#git-配置)
- [日常操作流程](#日常操作流程)
- [分支管理](#分支管理)
- [代码同步](#代码同步)
- [常见问题](#常见问题)

---

## Git 配置

### 首次使用配置
```bash
# 设置用户名和邮箱
git config --global user.name "你的名字"
git config --global user.email "你的邮箱"

# 查看配置
git config --list
```

### 配置 SSH Key（推荐）
```bash
# 生成 SSH Key（一路回车即可）
ssh-keygen -t ed25519 -C "你的邮箱"

# 查看公钥
cat ~/.ssh/id_ed25519.pub
```
将公钥内容复制到 GitHub 账号的 SSH Keys 设置中。

---

## 日常操作流程

### 1. 克隆项目
```bash
git clone git@github.com:lbdking/Tree_Hollow.git
cd Tree_Hollow
```

### 2. 查看状态
```bash
# 查看当前状态
git status

# 查看修改内容
git diff
```

### 3. 添加文件
```bash
# 添加单个文件
git add 文件名

# 添加所有修改
git add .

# 添加指定类型文件
git add *.py
```

### 4. 提交代码
```bash
# 提交并填写提交信息
git commit -m "feat: 添加新功能"

# 修改最后一次提交
git commit --amend
```

### 5. 推送到远程
```bash
# 推送到 main 分支
git push origin main

# 推送并设置上游分支
git push -u origin main
```

### 6. 拉取更新
```bash
# 拉取远程更新
git pull origin main

# 先拉取再推送（推荐）
git pull --rebase origin main
git push origin main
```

---

## 分支管理

### 创建分支
```bash
# 创建新分支
git branch feature-xxx

# 创建并切换到新分支
git checkout -b feature-xxx
```

### 切换分支
```bash
# 切换到指定分支
git checkout main

# 查看所有分支
git branch -a
```

### 合并分支
```bash
# 切换到 main 分支
git checkout main

# 合并 feature 分支
git merge feature-xxx

# 删除已合并的分支
git branch -d feature-xxx
```

### 推送分支
```bash
# 推送本地分支到远程
git push origin feature-xxx
```

---

## 代码同步

### 解决冲突
```bash
# 拉取远程更新时可能会有冲突
git pull origin main

# 手动解决冲突后
git add .
git commit -m "fix: 解决合并冲突"
git push origin main
```

### 查看历史
```bash
# 查看提交历史
git log

# 查看简化历史
git log --oneline --graph

# 查看最近 5 条
git log -5
```

### 回退版本
```bash
# 回退到上一个版本（保留修改）
git reset --soft HEAD~1

# 回退到上一个版本（丢弃修改）
git reset --hard HEAD~1

# 回退到指定提交
git reset --hard 提交ID
```

---

## 常用提交信息规范

- `feat`: 新功能
- `fix`: 修复 bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建/工具相关

示例：
```bash
git commit -m "feat: 添加 RAG 检索功能"
git commit -m "fix: 修复登录接口 bug"
git commit -m "docs: 更新使用文档"
```

---

## 常见问题

### 1. 如何撤销本地修改？
```bash
# 撤销工作区修改
git checkout -- 文件名

# 撤销暂存区修改
git reset HEAD 文件名
```

### 2. 如何修改已提交的信息？
```bash
git commit --amend -m "新的提交信息"
git push --force origin main
```

### 3. 如何忽略某些文件？
确保 `.gitignore` 文件已包含需要忽略的文件：
```
node_modules/
.venv/
.env.local
*.log
```

### 4. 如何查看远程仓库地址？
```bash
git remote -v
```

### 5. 如何更换远程仓库地址？
```bash
git remote set-url origin git@github.com:用户名/仓库名.git
```

---

## 项目当前状态

- 远程仓库：`git@github.com:lbdking/Tree_Hollow.git`
- 当前分支：`main`
- 最新提交：`e30830e docs: 在新同学指南里说明 .venv/node_modules 故意不入库`
