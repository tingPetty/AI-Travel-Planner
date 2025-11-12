# AI 旅行规划助手

基于阿里云大模型的智能旅行规划系统，支持语音交互、自然语言理解和个性化行程推荐。

**GitHub 仓库**: https://github.com/tingPetty/AI-Travel-Planner

## 项目功能

- **智能对话**：使用阿里云通义千问大模型进行自然语言交互
- **语音识别**：集成阿里云语音服务，支持语音输入旅行需求
- **行程规划**：根据预算、时间、偏好自动生成个性化旅行方案
- **地图展示**：集成高德地图展示景点位置
- **用户管理**：支持用户注册/登录

## 技术栈

- **前端**: Vue 3 + TypeScript + Element Plus + 高德地图
- **后端**: FastAPI + SQLAlchemy + SQLite
- **AI服务**: 阿里云通义千问 + 阿里云语音识别
- **部署**: Docker + Docker Compose

## 部署方式

本项目提供两种部署方式，请根据实际情况选择：

### 方式一：本地构建部署

适用场景：需要修改代码或首次部署

#### 前置要求
- 安装 Docker 和 Docker Compose
- 准备阿里云 API Key（通义千问、语音识别、访问密钥）

#### 步骤 1：克隆项目
```bash
git clone https://github.com/tingPetty/AI-Travel-Planner.git
cd AI-Travel-Planner
```

#### 步骤 2：配置环境变量

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

#### 步骤 3：启动服务
启动 Docker 容器：
```bash
docker-compose up -d
```

#### 步骤 4：访问应用
- **前端页面**: http://localhost
- **后端 API 文档**: http://localhost:8000/docs

#### 停止服务
```bash
docker-compose down
```

### 方式二：拉取镜像快速部署（推荐用于快速体验）

适用场景：直接使用已构建的镜像，无需本地构建，快速启动

#### 步骤 1：创建项目目录和配置文件
```bash
# 创建空项目目录
mkdir AI-Travel-Planner
cd AI-Travel-Planner

# 创建 .env 文件
```

创建 `.env` 文件，内容参考如下（请替换为你的实际 API Key）：
```bash
# ========================================
# AI 旅行规划助手 - 环境变量配置
# ========================================
# 说明：
# 1. 复制此文件为 .env（项目根目录）
# 2. 所有 API Key 请替换为你自己的密钥
# 3. 前后端环境变量已统一在此文件中
# 4. 使用 Docker 运行时，必须通过 -e 或 --env-file 传入环境变量
# ========================================

# ============ 后端环境变量 ============

# 通义千问API配置
DASHSCOPE_API_KEY=your-dashscope-api-key

# 阿里云语音识别配置
ALIYUN_APP_KEY=your-aliyun-appkey
ALIYUN_TOKEN=your-aliyun-token

# 阿里云访问密钥
ALIYUN_AK_ID=your-aliyun-access-key-id
ALIYUN_AK_SECRET=your-aliyun-access-key-secret

# ============ 前端环境变量 ============

# 高德地图 API Key（前端使用）
# 获取地址: https://console.amap.com/dev/key/app
VITE_AMAP_KEY=your-amap-key

# API 基础地址（可选，默认为 http://localhost:8000）
VITE_API_BASE_URL=http://localhost:8000
```

#### 步骤 2：拉取镜像
```bash
# 拉取后端镜像
docker pull crpi-8u01t7hyb4lecond.cn-hangzhou.personal.cr.aliyuncs.com/zt-ai-travel-planner/ai-travel-planner-backend:latest

# 拉取前端镜像
docker pull crpi-8u01t7hyb4lecond.cn-hangzhou.personal.cr.aliyuncs.com/zt-ai-travel-planner/ai-travel-planner-frontend:latest
```

#### 步骤 3：运行容器
```bash
# 创建网络
docker network create travel-planner-network

# 运行后端（如果在 Powershell 中运行命令的话行继续符为反引号`）
docker run -d \
  --name backend \
  --network travel-planner-network \
  -p 8000:8000 \
  --env-file .env \
  -v $(pwd)/backend/data:/app/data \
  crpi-8u01t7hyb4lecond.cn-hangzhou.personal.cr.aliyuncs.com/zt-ai-travel-planner/ai-travel-planner-backend:latest

# 运行前端（如果在 Powershell 中运行命令的话行继续符为反引号`）
## 直接传入环境变量
docker run -d \
  --name frontend \
  --network travel-planner-network \
  -p 80:80 \
  -e VITE_AMAP_KEY=你的高德地图API密钥 \
  -e VITE_API_BASE_URL=http://localhost:8000 \
  crpi-8u01t7hyb4lecond.cn-hangzhou.personal.cr.aliyuncs.com/zt-ai-travel-planner/ai-travel-planner-frontend:latest

## 或者使用 .env 文件
docker run -d \
  --name frontend \
  --network travel-planner-network \
  -p 80:80 \
  --env-file .env \
  crpi-8u01t7hyb4lecond.cn-hangzhou.personal.cr.aliyuncs.com/zt-ai-travel-planner/ai-travel-planner-frontend:latest
```

#### 步骤 4：访问应用
容器启动成功后，即可访问应用：
- **前端页面**: http://localhost
- **后端 API 文档**: http://localhost:8000/docs

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

## API Key 获取指南

本项目使用阿里云服务和高德地图服务，需要以下 API Key：

### 1. 通义千问 API Key (`DASHSCOPE_API_KEY`)
- **用途**: AI 对话和行程规划
- **获取地址**: https://bailian.console.aliyun.com/?spm=5176.12818093_47.resourceCenter.3.31fe2cc9CIqiHW&tab=model#/api-key
- **官方文档**: https://bailian.console.aliyun.com/?spm=5176.12818093_47.resourceCenter.3.31fe2cc9CIqiHW&tab=api#/api

### 2. 阿里云语音服务 (`ALIYUN_APP_KEY`, `ALIYUN_TOKEN`)
- **用途**: 语音识别功能
- **获取地址**: https://nls-portal.console.aliyun.com/applist
- **官方文档**: https://help.aliyun.com/zh/isi/getting-started/start-here?spm=a2c4g.11174283.help-menu-30413.d_1_0.232effd9sZqZ38&scm=20140722.H_72138._.OR_help-T_cn~zh-V_1
- **注意事项**: TOKEN 可以使用“通过控制台获取临时 Token”或者“通过 SDK 获取 Token”的方式获取。

### 3. 阿里云访问密钥 (`ALIYUN_AK_ID`, `ALIYUN_AK_SECRET`)
- **用途**: 调用阿里云 API
- **获取地址**: https://ram.console.aliyun.com/manage/ak
- **官方文档**: https://help.aliyun.com/zh/ram/user-guide/create-an-accesskey-pair 

### 4. 高德地图 API Key (`VITE_AMAP_KEY`)
- **用途**: 地图展示和地理位置服务
- **获取地址**: https://console.amap.com/dev/key/app
- **官方文档**: https://lbs.amap.com/api/javascript-api-v2/guide/abc/prepare
- **注意事项**: 需要申请“Web 服务”的密钥，不是“Web 端（JS API）”的密钥

### 配置说明
1. 所有 API Key 均通过环境变量配置，**不会**写入代码中。请在项目根目录的 `.env` 文件中配置所有密钥。
2. 请确保**获取到的阿里云 AccessKey ID、AccessKey Secret、服务鉴权 Token、项目 Appkey 的值归属于同一阿里云账号或同一RAM用户**。

## 使用说明

### 首次使用
1. **注册账号**: 首次访问应用时，请先点击「注册」按钮创建一个账号
2. **登录系统**: 使用注册的账号登录系统
3. **开始规划**: 登录后即可开始使用 AI 旅行规划功能

### 重要提示
- **AI 生成时间**: AI 生成行程规划需要 20-30 秒，请耐心等待，不要重复提交
- **语音识别**: 使用语音输入时，请在安静环境下清晰发音
- **地图显示**: 如果地图无法显示，请检查 `VITE_AMAP_KEY` 环境变量是否正确配置

## 注意事项

- 确保 `.env` 文件中的 API Key 有效且有足够的调用额度
- 首次启动可能需要几分钟来构建 Docker 镜像
- 如遇到问题，请查看容器日志：`docker logs frontend` 或 `docker logs backend`
