# 第一阶段：构建阶段
FROM python:3.13.3-slim-bullseye AS builder

WORKDIR /app

# 安装 uv 包管理器
RUN pip install --no-cache-dir uv

# 复制依赖文件
COPY pyproject.toml .

# 使用 uv 创建虚拟环境并安装依赖，同时清理缓存
RUN uv venv /.venv && \
    uv pip install --python /.venv/bin/python --no-cache . && \
    find /.venv -type f -name "*.pyc" -delete && \
    find /.venv -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# 第二阶段：运行阶段
FROM python:3.13.3-alpine

WORKDIR /

# 从构建阶段复制虚拟环境
COPY --from=builder /.venv /.venv

# 复制源代码
COPY app/ ./app/
COPY main.py .

# 暴露端口
EXPOSE 80

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV PATH="/.venv/bin:$PATH"

# 创建非root用户并设置适当权限
RUN adduser -D appuser && \
    chown -R appuser:appuser /app && \
    chown -R appuser:appuser /.venv
USER appuser

# 运行命令
CMD ["waitress-serve", "--host=0.0.0.0", "--port=80", "--call", "main:create_app"]