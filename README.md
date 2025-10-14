# Homer Flask 应用

## 生产环境部署指南

### 方法一：使用批处理脚本运行

1. 确保已安装Python 3.13+并创建了虚拟环境
2. 安装依赖：
   ```
   pip install -r requirements.txt
   ```
   或使用uv（推荐）：
   ```
   uv pip install -e .
   ```
3. 运行生产服务器：
   ```
   run_prod.bat
   ```
   
   > 注意：本项目使用uv工具来管理Python依赖和运行应用程序。生产环境脚本会自动检查并安装所需的waitress包。

### 方法二：将应用部署为Windows服务（推荐）

1. 下载NSSM工具（Non-Sucking Service Manager）：
   - 访问 https://nssm.cc/download 下载最新版本
   - 解压并将nssm.exe放置在项目根目录下的`tools`文件夹中

2. 确保已安装uv并配置好环境：
   ```
   pip install uv
   ```

3. 以管理员身份运行install_service.bat：
   - 右键点击install_service.bat
   - 选择"以管理员身份运行"

4. 服务将被安装并配置为自动启动
   - 服务名称：HomerFlaskApp
   - 可通过Windows服务管理器（services.msc）管理

5. 手动启动服务：
   ```
   sc start HomerFlaskApp
   ```

6. 停止服务：
   ```
   sc stop HomerFlaskApp
   ```

7. 删除服务：
   ```
   sc delete HomerFlaskApp
   ```

### 配置说明

- 服务器默认运行在0.0.0.0:8080（所有网络接口的8080端口）
- Docker容器内部使用8080端口，映射到宿主机的8080端口
- 如需修改端口，请编辑相应的配置文件
- 生产环境使用Waitress作为WSGI服务器，这是一个纯Python实现的高性能服务器
- 项目使用uv工具来运行应用程序，提供更快的依赖解析和环境隔离

### 安全注意事项

1. 项目已移除无用的SECRET_KEY配置，因为flash消息在前端AJAX场景下不起作用
2. 所有用户输入都经过验证和清理，防止XSS和注入攻击
3. 文件上传有大小限制（16MB）和格式验证
4. 考虑在前端使用Nginx等反向代理
5. 如果暴露到公网，建议配置SSL证书以启用HTTPS

### 代码优化

本项目已进行以下优化：
- 消除了配置文件操作的代码重复
- 添加了文件锁机制防止并发写入冲突
- 实现了配置缓存减少磁盘I/O
- 增强了错误处理和日志记录
- 优化了搜索功能移除冗余操作
- 改进了输入验证和安全性

### 日志

- Windows服务的日志可在Windows事件查看器中找到
- 应用程序日志可配置输出到文件系统（需额外配置）
