FROM python:3.11-slim

WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建数据目录（用于持久化数据库文件）
RUN mkdir -p /app/data

# 暴露端口
EXPOSE 8000

# 启动命令（应用会在启动时自动初始化数据库）
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
