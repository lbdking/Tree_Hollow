# ===== Stage 1: 构建 Vue 静态资源 =====
FROM node:20-alpine AS builder

WORKDIR /build

# 利用层缓存
COPY package*.json ./
RUN npm config set registry https://registry.npmmirror.com && npm install

COPY . .
RUN npm run build

# ===== Stage 2: Nginx 托管 =====
FROM nginx:1.27-alpine

COPY --from=builder /build/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
