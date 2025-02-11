# 应用部署指南

## 前置要求
- Docker 20.10+
- 或 Python 3.9+

## Docker部署
```bash
# 构建镜像
docker build -t sqlread-app .

# 运行容器（后台模式）
docker run -d \\
  -p 8081:8081 \\
  -v ./webui.db:/app/webui.db \\
  --name sqlread-container \\
  sqlread-app
```

## 本地运行
```bash
# 安装依赖
pip install -r requirements.txt

# 启动应用
python app.py

# 访问地址
http://localhost:8081
```

## 注意事项
1. 数据库文件webui.db会持久化在宿主机当前目录
2. 生产环境建议设置FLASK_ENV=production
3. 容器日志查看：docker logs sqlread-container