# AI 旅行规划助手

基于阿里云大模型的智能旅行规划系统，支持语音交互、自然语言理解和个性化行程推荐。

## 项目功能

- **智能对话**：使用阿里云通义千问大模型进行自然语言交互
- **语音识别**：集成阿里云语音服务，支持语音输入旅行需求
- **行程规划**：根据预算、时间、偏好自动生成个性化旅行方案
- **地图展示**：集成高德地图展示景点位置和路线规划
- **用户管理**：支持用户注册、登录和历史记录管理

## 技术栈

- **前端**: Vue 3 + TypeScript + Element Plus + 高德地图
- **后端**: FastAPI + SQLAlchemy + SQLite
- **AI服务**: 阿里云通义千问 + 阿里云语音识别
- **部署**: Docker + Docker Compose

## 快速开始（使用 Docker）

### 前置要求
- 安装 Docker 和 Docker Compose
- 准备阿里云 API Key（通义千问、语音识别、访问密钥）

### 步骤 1：克隆项目
```bash
git clone https://github.com/tingPetty/AI-Travel-Planner.git
cd AI-Travel-Planner
```

### 步骤 2：配置环境变量

复制环境变量模板并填入你的 API Key：
```bash
cp .env.example .env
```

编辑 `.env` 文件，填入以下配置：
```bash
# 后端 - 通义千问API配置
DASHSCOPE_API_KEY=你的通义千问API密钥

# 后端 - 阿里云语音识别配置
ALIYUN_APP_KEY=你的阿里云AppKey
ALIYUN_TOKEN=你的阿里云Token

# 后端 - 阿里云访问密钥
ALIYUN_AK_ID=你的阿里云AccessKeyId
ALIYUN_AK_SECRET=你的阿里云AccessKeySecret

# 前端 - 高德地图 API Key
VITE_AMAP_KEY=你的高德地图API密钥
```

### 步骤 3：启动服务
启动 Docker 容器：
```bash
docker-compose up -d
```

### 步骤 4：访问应用
- **前端页面**: http://localhost
- **后端 API 文档**: http://localhost:8000/docs

### 停止服务
```bash
docker-compose down
```

## 使用阿里云镜像仓库部署

如果你想直接使用已构建的 Docker 镜像（无需本地构建）：

### 步骤 1：拉取镜像
```bash
# 拉取后端镜像
docker pull crpi-8u01t7hyb4lecond.cn-hangzhou.personal.cr.aliyuncs.com/zt-ai-travel-planner/ai-travel-planner-backend:latest

# 拉取前端镜像
docker pull crpi-8u01t7hyb4lecond.cn-hangzhou.personal.cr.aliyuncs.com/zt-ai-travel-planner/ai-travel-planner-frontend:latest
```

### 步骤 2：运行容器
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

## 本地开发

### 后端开发
```bash
cd backend
pip install -r requirements.txt
python start.py
```
访问: http://localhost:8000/docs

### 前端开发
```bash
cd frontend
npm install
npm run dev
```
访问: http://localhost:5173

## 项目结构
```
├── backend/              # FastAPI 后端
│   ├── app/             # 应用代码
│   ├── Dockerfile       # 后端 Docker 配置
│   ├── requirements.txt # Python 依赖
│   └── .env.example     # 环境变量模板
├── frontend/            # Vue 3 前端
│   ├── src/            # 源代码
│   ├── Dockerfile      # 前端 Docker 配置
│   └── nginx.conf      # Nginx 配置
├── .github/
│   └── workflows/
│       └── docker-publish.yml  # GitHub Actions 配置
├── docker-compose.yml   # Docker Compose 配置
└── README.md           # 项目说明
```

## API Key 说明

本项目使用阿里云服务，需要以下 API Key：

1. **通义千问 API Key** (`DASHSCOPE_API_KEY`): 用于 AI 对话和行程规划
2. **阿里云语音服务** (`ALIYUN_APP_KEY`, `ALIYUN_TOKEN`): 用于语音识别功能
3. **阿里云访问密钥** (`ALIYUN_AK_ID`, `ALIYUN_AK_SECRET`): 用于调用阿里云 API
4. **高德地图 API Key** (`VITE_AMAP_KEY`): 用于地图展示和地理位置服务

所有 API Key 均通过环境变量配置，**不会**写入代码中。请在项目根目录的 `.env` 文件中配置所有密钥。

## 注意事项

- 确保 `.env` 文件中的 API Key 有效且有足够的调用额度
- 首次启动可能需要几分钟来构建 Docker 镜像
- 数据库文件存储在 `backend/data` 目录下
- 生产环境建议使用 HTTPS 和更安全的数据库配置

## License

MIT License
