#!/bin/sh

# 前端容器启动脚本
# 将环境变量注入到运行时配置文件

CONFIG_FILE="/usr/share/nginx/html/config.js"

echo "=========================================="
echo "正在生成运行时配置文件..."
echo "=========================================="

# 检查环境变量是否设置
if [ -z "$VITE_AMAP_KEY" ] || [ "$VITE_AMAP_KEY" = "" ]; then
  echo "警告: VITE_AMAP_KEY 环境变量未设置！"
  echo "请使用 docker run -e VITE_AMAP_KEY=your_key 或在 docker-compose.yml 中配置"
else
  echo "✓ VITE_AMAP_KEY 已设置"
fi

if [ -z "$VITE_API_BASE_URL" ] || [ "$VITE_API_BASE_URL" = "" ]; then
  echo "警告: VITE_API_BASE_URL 环境变量未设置，使用默认值"
  VITE_API_BASE_URL="http://localhost:8000"
fi

# 生成 config.js 文件
cat > $CONFIG_FILE << EOF
// 运行时配置文件
// 此文件在容器启动时由环境变量生成
window.__APP_CONFIG__ = {
  VITE_AMAP_KEY: '${VITE_AMAP_KEY}',
  VITE_API_BASE_URL: '${VITE_API_BASE_URL}'
}
EOF

echo "=========================================="
echo "运行时配置文件已生成："
echo "  VITE_AMAP_KEY: ${VITE_AMAP_KEY:0:10}..."
echo "  VITE_API_BASE_URL: ${VITE_API_BASE_URL}"
echo "=========================================="

# 启动 nginx
echo "启动 Nginx..."
nginx -g 'daemon off;'
