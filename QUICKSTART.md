# 快速开始指南（助教使用）

本文档为助教提供最简单的项目运行方式。

## 方式一：使用 Docker Compose（推荐）

### 1. 准备环境
确保已安装：
- Docker
- Docker Compose

### 2. 配置 API Key

复制环境变量模板：
```bash
cp .env.example .env
```

编辑 `.env` 文件，填入所有 API Key：
```
# 后端配置
DASHSCOPE_API_KEY=你的通义千问密钥
ALIYUN_APP_KEY=你的阿里云AppKey
ALIYUN_TOKEN=你的阿里云Token
ALIYUN_AK_ID=你的AccessKeyId
ALIYUN_AK_SECRET=你的AccessKeySecret

# 前端配置
VITE_AMAP_KEY=你的高德地图密钥
```

### 3. 启动项目
```bash
docker-compose up -d
```

### 4. 访问应用
- 前端：http://localhost
- 后端 API：http://localhost:8000/docs

### 5. 停止项目
```bash
docker-compose down
```

## 方式二：使用阿里云镜像（如果已发布）

### 1. 拉取镜像
```bash
# 拉取后端镜像
docker pull crpi-8u01t7hyb4lecond.cn-hangzhou.personal.cr.aliyuncs.com/zt-ai-travel-planner/ai-travel-planner-backend:latest

# 拉取前端镜像
docker pull crpi-8u01t7hyb4lecond.cn-hangzhou.personal.cr.aliyuncs.com/zt-ai-travel-planner/ai-travel-planner-frontend:latest
```

### 2. 配置环境变量
参考方式一的步骤 2

### 3. 运行容器
```bash
# 创建网络
docker network create travel-planner-network

# 运行后端（需要配置 .env 文件）
docker run -d \
  --name backend \
  --network travel-planner-network \
  -p 8000:8000 \
  --env-file .env \
  -v $(pwd)/backend/data:/app/data \
  crpi-8u01t7hyb4lecond.cn-hangzhou.personal.cr.aliyuncs.com/zt-ai-travel-planner/ai-travel-planner-backend:latest

# 运行前端
docker run -d \
  --name frontend \
  --network travel-planner-network \
  -p 80:80 \
  crpi-8u01t7hyb4lecond.cn-hangzhou.personal.cr.aliyuncs.com/zt-ai-travel-planner/ai-travel-planner-frontend:latest
```

## 方式三：本地开发模式

### 后端
```bash
cd backend
pip install -r requirements.txt
python start.py
```

### 前端
```bash
cd frontend
npm install
npm run dev
```

## 常见问题

### Q: 端口被占用？
修改 `docker-compose.yml` 中的端口映射：
```yaml
ports:
  - "8080:80"  # 将前端改为 8080 端口
```

### Q: API Key 无效？
检查 `.env` 文件中的密钥是否正确，确保没有多余的空格或引号。

### Q: 数据库错误？
首次运行会自动创建数据库，如遇问题可删除 `backend/data` 目录重新启动。
