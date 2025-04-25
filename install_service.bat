@echo off
echo 正在安装Windows服务...

:: 检查是否以管理员身份运行
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo 请以管理员身份运行此脚本
    pause
    exit /b 1
)

:: 安装NSSM（Non-Sucking Service Manager）
:: 注意：您需要先下载NSSM并放置在正确的位置
set NSSM_PATH=%~dp0tools\nssm.exe
if not exist "%NSSM_PATH%" (
    echo 错误：找不到NSSM工具
    echo 请从 https://nssm.cc/download 下载NSSM，并放置在 %~dp0tools 目录中
    pause
    exit /b 1
)

:: 获取当前目录的绝对路径
set APP_PATH=%~dp0
set APP_PATH=%APP_PATH:~0,-1%

:: 设置服务信息
set SERVICE_NAME=HomerFlaskApp
set PYTHON_PATH=%APP_PATH%\.venv\Scripts\python.exe
set UV_PATH=%APP_PATH%\.venv\Scripts\uv.exe

:: 安装服务
echo 正在安装 %SERVICE_NAME% 服务...
"%NSSM_PATH%" install %SERVICE_NAME% "%UV_PATH%" run waitress-serve --host=0.0.0.0 --port=80 --call "main:create_app"
"%NSSM_PATH%" set %SERVICE_NAME% DisplayName "Homer Flask Application"
"%NSSM_PATH%" set %SERVICE_NAME% Description "Flask Web应用的生产环境服务"
"%NSSM_PATH%" set %SERVICE_NAME% AppDirectory "%APP_PATH%"
"%NSSM_PATH%" set %SERVICE_NAME% AppEnvironmentExtra PATH=%PATH%;%APP_PATH%\.venv\Scripts

:: 设置服务自启动
"%NSSM_PATH%" set %SERVICE_NAME% Start SERVICE_AUTO_START

echo 服务已安装。您可以通过以下命令启动服务：
echo sc start %SERVICE_NAME%
echo.
echo 或者通过Windows服务管理器启动服务。

pause 