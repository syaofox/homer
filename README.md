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

- 服务器默认运行在0.0.0.0:80（所有网络接口的80端口）
- 如需修改端口，请编辑run_prod.bat和install_service.bat文件中的相应配置
- 生产环境使用Waitress作为WSGI服务器，这是一个纯Python实现的高性能服务器
- 项目使用uv工具来运行应用程序，提供更快的依赖解析和环境隔离

### 安全注意事项

1. 确保设置了强壮的SECRET_KEY（在app/__init__.py中）
2. 考虑在前端使用Nginx等反向代理
3. 如果暴露到公网，建议配置SSL证书以启用HTTPS

### 日志

- Windows服务的日志可在Windows事件查看器中找到
- 应用程序日志可配置输出到文件系统（需额外配置）
