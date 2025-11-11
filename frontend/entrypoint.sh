#!/bin/sh

# 前端容器启动脚本
# 将环境变量注入到运行时配置文件

CONFIG_FILE="/usr/share/nginx/html/config.js"

echo "正在生成运行时配置文件..."

# 生成 config.js 文件
cat > $CONFIG_FILE << EOF
// 运行时配置文件
// 此文件在容器启动时由环境变量生成
window.__APP_CONFIG__ = {
  VITE_AMAP_KEY: '${VITE_AMAP_KEY}',
  VITE_API_BASE_URL: '${VITE_API_BASE_URL}'
}
EOF

echo "运行时配置文件已生成："
echo "  VITE_AMAP_KEY: ${VITE_AMAP_KEY:0:10}..."
echo "  VITE_API_BASE_URL: ${VITE_API_BASE_URL}"

# 启动 nginx
echo "启动 Nginx..."
nginx -g 'daemon off;'
