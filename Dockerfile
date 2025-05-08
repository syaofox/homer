FROM python:3.13.3-slim-bullseye

WORKDIR /app

# 先复制依赖文件
COPY requirements.txt .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制其余项目文件
COPY . .

# 暴露端口
EXPOSE 80

# 设置环境变量
ENV PYTHONUNBUFFERED=1

# 创建非root用户并设置适当权限
RUN useradd -m appuser && \
    chown -R appuser:appuser /app
USER appuser

# 健康检查
HEALTHCHECK --interval=30s --timeout=5s CMD curl -f http://localhost:80/ || exit 1

# 运行命令
CMD ["waitress-serve", "--host=0.0.0.0", "--port=80", "--call", "main:create_app"]