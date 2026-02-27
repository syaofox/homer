# syntax=docker/dockerfile:1
# 启用 BuildKit 以使用缓存挂载

# 第一阶段：构建
FROM python:3.13-slim-bookworm AS builder
WORKDIR /app

# 使用缓存挂载加速重复构建
RUN --mount=type=cache,target=/root/.cache/uv \
    pip install --no-cache-dir uv

COPY pyproject.toml uv.lock* ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv venv /opt/venv && \
    uv pip install --python /opt/venv/bin/python --no-cache . && \
    find /opt/venv -type f -name "*.pyc" -delete && \
    find /opt/venv -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# 第二阶段：运行（与 builder 同基础镜像，保证兼容）
FROM python:3.13-slim-bookworm AS runtime
WORKDIR /app

# 仅安装运行时必需：tzdata，并清理 apt 缓存
RUN apt-get update && apt-get install -y --no-install-recommends tzdata \
    && rm -rf /var/lib/apt/lists/*

# 复制虚拟环境（使用 /opt/venv 便于与系统 Python 隔离）
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY app/ ./app/
COPY main.py .

# 创建非 root 用户（使用固定 UID/GID 便于卷权限）
RUN groupadd -r appuser -g 1000 && \
    useradd -r -u 1000 -g appuser appuser && \
    chown -R appuser:appuser /app

USER appuser
EXPOSE 8080
ENV PYTHONUNBUFFERED=1
CMD ["waitress-serve", "--host=0.0.0.0", "--port=8080", "--call", "main:create_app"]
