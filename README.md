# Homer Flask 应用

Homer 是一个基于 Flask 的 Web 应用，提供简洁的导航页面和配置管理功能。

## 快速开始

### 方法一：使用 Docker 部署（推荐）

这是最简单快捷的部署方式，适合大多数用户。

#### 使用预构建镜像

```bash
# 拉取最新版本
docker pull ghcr.io/syaofox/homer:latest

# 运行容器
docker run -d \
  --name homer \
  -p 8080:8080 \
  -v ./config:/config \
  ghcr.io/syaofox/homer:latest
```

#### 使用 docker-compose

修改 `docker-compose.yml` 使用预构建镜像：

```yaml
services:
  web:
    image: ghcr.io/syaofox/homer:latest
    ports:
      - "8080:8080"
    restart: unless-stopped
    volumes:
      - ./config:/config
```

然后运行：

```bash
docker-compose up -d
```

### 方法二：使用 Python 直接运行

如果您的环境没有 Docker，可以直接使用 Python 运行。

#### 环境要求

- Python 3.13+
- 虚拟环境（推荐）

#### 安装和运行

1. 创建虚拟环境：
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # 或
   venv\Scripts\activate     # Windows
   ```

2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
   
   或使用 uv（推荐）：
   ```bash
   uv pip install -e .
   ```

3. 运行应用：
   ```bash
   python main.py
   ```

## 访问应用

应用启动后，在浏览器中访问：

- 主页：http://localhost:8080
- 配置页：http://localhost:8080/config

## 配置说明

### 基本配置

- **端口**：默认运行在 8080 端口
- **配置目录**：`./config`（Docker）或项目根目录的 `config` 文件夹
- **数据目录**：配置文件和图标保存在配置目录中

### 环境变量（可选）

```bash
# 服务器配置
export HOST=0.0.0.0          # 监听主机地址
export PORT=8080             # 监听端口
export ENVIRONMENT=production # 运行环境 (development/production)

# 日志配置
export LOG_LEVEL=INFO        # 日志级别 (DEBUG/INFO/WARNING/ERROR)
export FLASK_DEBUG=false     # Flask调试模式

# 文件上传
export MAX_CONTENT_LENGTH=16777216  # 最大上传文件大小(字节)，默认16MB

# 缓存配置
export CACHE_TTL=30          # 配置缓存时间(秒)

# 时区设置
export TZ=Asia/Shanghai      # 时区设置

# Docker环境标识
export DOCKER_CONTAINER=true # 标识在Docker中运行
```

## 安全注意事项

- 适用于内网使用
- 文件上传大小限制为 16MB
