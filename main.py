from app import app

def create_app():
    """用于生产环境的应用工厂函数"""
    return app

if __name__ == "__main__":
    print("Starting the application...listen on 0.0.0.0:5050")
    app.run(host="0.0.0.0", port=5050, debug=False)
