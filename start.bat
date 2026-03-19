@echo off
echo ==========================================
echo 🚀 GameCraft AI Suite - 本地超算中心启动
echo ==========================================

cd backend

echo 📦 正在检查并安装必要的 Python 依赖...
pip install -r requirements.txt -q

echo 🧠 正在启动 FastAPI 后端...
python main.py

pause