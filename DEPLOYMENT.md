# Docker 镜像部署指南

本文档说明如何通过 GitHub Actions 自动构建 Docker 镜像并推送到阿里云镜像仓库。

## 一、准备阿里云镜像仓库

### 1. 登录阿里云容器镜像服务
访问：https://cr.console.aliyun.com/

### 2. 创建命名空间
- 进入"命名空间"页面
- 点击"创建命名空间"
- 输入命名空间名称（例如：`ai-travel`）
- 记录此命名空间名称，后续需要使用

### 3. 设置访问凭证
- 进入"访问凭证"页面
- 点击"设置固定密码"
- 设置并记录用户名和密码
- 用户名格式通常为：`你的阿里云账号@你的企业别名`

## 二、配置 GitHub Secrets

### 1. 进入 GitHub 仓库设置
- 打开你的 GitHub 仓库
- 点击 `Settings` → `Secrets and variables` → `Actions`

### 2. 添加以下 Secrets
点击 `New repository secret`，分别添加：

| Secret 名称 | 说明 | 示例值 |
|------------|------|--------|
| `ALIYUN_REGISTRY_USERNAME` | 阿里云镜像仓库用户名 | `your-account@company` |
| `ALIYUN_REGISTRY_PASSWORD` | 阿里云镜像仓库密码 | `your-password` |
| `ALIYUN_REGISTRY_NAMESPACE` | 阿里云镜像仓库命名空间 | `ai-travel` |

## 三、触发自动构建

### 方式 1：推送代码触发
```bash
git add .
git commit -m "Update code"
git push origin main
```
推送到 `main` 或 `master` 分支会自动触发构建。

### 方式 2：手动触发
- 进入 GitHub 仓库的 `Actions` 页面
- 选择 `Build and Push Docker Images` workflow
- 点击 `Run workflow` 按钮
- 选择分支并运行

## 四、查看构建状态

### 1. 在 GitHub 查看
- 进入仓库的 `Actions` 页面
- 查看最新的 workflow 运行状态
- 点击可查看详细日志

### 2. 在阿里云查看
- 登录阿里云容器镜像服务
- 进入"镜像仓库"页面
- 查看新推送的镜像：
  - `ai-travel-planner-backend:latest`
  - `ai-travel-planner-frontend:latest`

## 五、使用构建的镜像

### 1. 拉取镜像
```bash
# 拉取后端镜像
docker pull registry.cn-hangzhou.aliyuncs.com/你的命名空间/ai-travel-planner-backend:latest

# 拉取前端镜像
docker pull registry.cn-hangzhou.aliyuncs.com/你的命名空间/ai-travel-planner-frontend:latest
```

### 2. 运行容器
参考 README.md 中的"使用阿里云镜像仓库部署"章节。

## 六、常见问题

### Q1: GitHub Actions 构建失败？
**检查项**：
- Secrets 是否正确配置
- 阿里云镜像仓库密码是否正确
- 命名空间是否存在

### Q2: 无法拉取镜像？
**解决方案**：
- 确认镜像仓库设置为"公开"（或配置访问凭证）
- 检查镜像名称和标签是否正确

### Q3: 如何查看镜像版本？
每次构建会生成两个标签：
- `latest`: 最新版本
- `<git-commit-sha>`: 特定提交版本

## 七、本地测试 Docker 构建

在推送到 GitHub 之前，可以本地测试：

```bash
# 构建后端镜像
docker build -t ai-travel-backend ./backend

# 构建前端镜像
docker build -t ai-travel-frontend ./frontend

# 使用 docker-compose 测试
docker-compose up
```

## 八、镜像仓库地址格式

完整的镜像地址格式：
```
registry.cn-hangzhou.aliyuncs.com/[命名空间]/[镜像名称]:[标签]
```

示例：
```
registry.cn-hangzhou.aliyuncs.com/ai-travel/ai-travel-planner-backend:latest
```
