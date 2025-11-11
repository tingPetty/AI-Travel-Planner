FROM node:20-alpine as builder

WORKDIR /app

# 复制依赖文件
COPY package*.json ./

# 安装依赖
RUN npm install

# 复制应用代码
COPY . .

# 构建参数（从 docker-compose 或 docker build 传入）
ARG VITE_API_BASE_URL=http://localhost:8000
ARG VITE_AMAP_KEY

# 设置环境变量供 Vite 构建使用
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
ENV VITE_AMAP_KEY=$VITE_AMAP_KEY

# 构建应用（跳过类型检查以加快 Docker 构建）
RUN npm run build:docker

# 生产环境
FROM nginx:alpine

# 复制构建产物到 nginx
COPY --from=builder /app/dist /usr/share/nginx/html

# 复制 nginx 配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
