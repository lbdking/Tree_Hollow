# Tree Hollow K8s 部署清单

```
00-namespace.yaml        创建 tree-hollow 命名空间
01-config.yaml           ConfigMap（非敏感配置）+ Secret（JWT/DeepSeek key）
02-mysql.yaml            MySQL StatefulSet + Service（5Gi PVC 持久化）
03-redis.yaml            Redis Deployment + Service
04-backend.yaml          后端 Deployment + NodePort:30800
05-frontend.yaml         移动端 + 管理后台 NodePort:30517 / 30518
```

## 端口映射

| 服务 | 集群内 Service | NodePort（公网访问） |
|---|---|---|
| 移动端 | frontend-mobile:80 | http://180.184.78.22:30517 |
| 管理后台 | frontend-admin:80 | http://180.184.78.22:30518 |
| 后端 API | backend:8000 | http://180.184.78.22:30800 |
| MySQL | mysql:3306 | 仅集群内（不暴露） |
| Redis | redis:6379 | 仅集群内（不暴露） |

## 镜像名（必须先在节点上构建/导入）

- `tree-hollow-backend:1.0`
- `tree-hollow-mobile:1.0`
- `tree-hollow-admin:1.0`

## 部署流程

见项目根目录的 README.md 或 deploy/ 下的脚本。
