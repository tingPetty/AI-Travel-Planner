# 作业提交指南

## 📋 提交清单

本项目已完成以下配置，满足作业提交要求：

### ✅ 已完成项目
- [x] Docker 配置（前端 + 后端）
- [x] GitHub Actions 自动构建配置
- [x] 环境变量管理（API Key 不在代码中）
- [x] README 文档（项目说明 + 运行指南）
- [x] 部署文档（Docker 镜像发布流程）

## 📦 提交内容

### 1. GitHub 仓库
- **仓库地址**: https://github.com/tingPetty/AI-Travel-Planner
- **包含内容**:
  - 完整源代码
  - Dockerfile 配置
  - GitHub Actions 工作流
  - 详细的 README 文档

### 2. Docker 镜像
通过 GitHub Actions 自动构建并推送到阿里云镜像仓库：
- 后端镜像: `registry.cn-hangzhou.aliyuncs.com/[命名空间]/ai-travel-planner-backend:latest`
- 前端镜像: `registry.cn-hangzhou.aliyuncs.com/[命名空间]/ai-travel-planner-frontend:latest`

### 3. 文档说明
- **README.md**: 项目功能介绍 + 完整运行指南
- **DEPLOYMENT.md**: GitHub Actions + 阿里云镜像仓库配置详解
- **QUICKSTART.md**: 助教快速开始指南

## 🔑 API Key 说明

本项目使用**阿里云 API Key**，包括：

1. **通义千问 API** - 用于 AI 对话和行程规划
2. **阿里云语音识别** - 用于语音输入功能
3. **阿里云访问密钥** - 用于调用阿里云服务
4. **高德地图 API** - 用于地图展示

### API Key 配置方式
所有 API Key 通过环境变量配置，**不在代码中硬编码**：
- 统一配置文件: `.env`（项目根目录）

### 提供给助教的 API Key
请在提交时将你的 API Key 填写在 README.md 的专门章节中，格式如下：

```markdown
## 助教使用的 API Key

复制以下内容到项目根目录的 `.env` 文件：

# 后端配置
DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxx
ALIYUN_APP_KEY=xxxxxxxxxxxxx
ALIYUN_TOKEN=xxxxxxxxxxxxx
ALIYUN_AK_ID=xxxxxxxxxxxxx
ALIYUN_AK_SECRET=xxxxxxxxxxxxx

# 前端配置
VITE_AMAP_KEY=xxxxxxxxxxxxx

**有效期**: 至 2025 年 2 月 11 日
```

## 🚀 下一步操作

### 步骤 1: 配置阿里云镜像仓库

1. 访问 https://cr.console.aliyun.com/
2. 创建命名空间（例如：`ai-travel`）
3. 设置访问凭证（用户名和密码）

### 步骤 2: 配置 GitHub Secrets

在 GitHub 仓库设置中添加以下 Secrets：
- `ALIYUN_REGISTRY_USERNAME`: 阿里云镜像仓库用户名
- `ALIYUN_REGISTRY_PASSWORD`: 阿里云镜像仓库密码
- `ALIYUN_REGISTRY_NAMESPACE`: 阿里云命名空间名称

详细步骤见 `DEPLOYMENT.md`

### 步骤 3: 推送代码触发构建

```bash
git add .
git commit -m "feat: add Docker and CI/CD configuration"
git push origin main
```

推送后会自动触发 GitHub Actions，构建并推送 Docker 镜像到阿里云。

### 步骤 4: 更新 README 中的镜像地址

构建成功后，在 README.md 中更新实际的镜像地址：
```
registry.cn-hangzhou.aliyuncs.com/你的命名空间/ai-travel-planner-backend:latest
```

### 步骤 5: 添加 API Key 到 README

在 README.md 中添加一个新章节，提供给助教使用的所有 API Key（确保有效期 3 个月）。
所有 Key 统一放在项目根目录的 `.env` 文件中。

## 📝 提交检查清单

提交前请确认：

- [ ] GitHub 仓库代码已推送
- [ ] Docker 镜像已成功构建并推送到阿里云
- [ ] README.md 包含完整的运行说明
- [ ] README.md 包含助教使用的 API Key
- [ ] API Key 有效期至少 3 个月
- [ ] .env 文件已添加到 .gitignore（不提交到 GitHub）
- [ ] 提供了 .env.example 模板文件
- [ ] 有详细的 Git 提交记录

## 🎯 助教运行项目的方式

助教可以通过以下两种方式运行项目：

### 方式 1: 使用 Docker Compose（推荐）
```bash
git clone https://github.com/tingPetty/AI-Travel-Planner.git
cd AI-Travel-Planner
# 配置 .env 文件
docker-compose up -d
```

### 方式 2: 直接使用 Docker 镜像
```bash
docker pull registry.cn-hangzhou.aliyuncs.com/命名空间/ai-travel-planner-backend:latest
docker pull registry.cn-hangzhou.aliyuncs.com/命名空间/ai-travel-planner-frontend:latest
# 运行容器
```

详细步骤见 `QUICKSTART.md`

## 📚 相关文档

- **README.md**: 项目完整说明
- **DEPLOYMENT.md**: Docker 镜像部署详解
- **QUICKSTART.md**: 快速开始指南（助教专用）
- **.env.example**: 环境变量模板

## ⚠️ 注意事项

1. **不要**将 API Key 提交到 GitHub 代码中
2. **确保** .env 文件在 .gitignore 中
3. **提供**有效期至少 3 个月的 API Key
4. **保持**详细的 Git 提交记录
5. **测试** Docker 镜像能否正常运行
