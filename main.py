from app import app
from app.config import config as app_config

def create_app():
    """用于生产环境的应用工厂函数"""
    return app

if __name__ == "__main__":
    print(f"Starting the application...listen on {app_config.host}:{app_config.port}")
    print(f"Environment: {app_config.environment}")
    print(f"Debug mode: {app_config.debug}")
    print(f"Timezone: {app_config.timezone}")
    
    app.run(
        host=app_config.host, 
        port=app_config.port, 
        debug=app_config.debug
    )
