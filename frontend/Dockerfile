FROM node:20-alpine as builder

WORKDIR /app

# 复制依赖文件
COPY package*.json ./

# 安装依赖
RUN npm install

# 复制应用代码
COPY . .

# 构建应用（跳过类型检查以加快 Docker 构建）
# 注意：不再需要构建时的环境变量，所有配置在运行时注入
RUN npm run build:docker

# 生产环境
FROM nginx:alpine

# 复制构建产物到 nginx
COPY --from=builder /app/dist /usr/share/nginx/html

# 复制 nginx 配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 复制启动脚本
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# 设置默认环境变量（可在运行时覆盖）
ENV VITE_AMAP_KEY=""
ENV VITE_API_BASE_URL="http://localhost:8000"

EXPOSE 80

# 使用启动脚本替代直接启动 nginx
ENTRYPOINT ["/entrypoint.sh"]
