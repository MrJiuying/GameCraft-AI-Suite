# 🛠️ GameCraft AI Suite 
> **Version:** `V0.0.1-Alpha`  
> **"让 AI 成为你的游戏副驾，而非外包。"** —— 由 **MrJiuying** 与 **Gemini** 联手打造。

`GameCraft AI Suite` 是一款专为 **Godot 4** 设计的“工业母机”级 AI 游戏开发插件。它实现了从“点子沟通”到“引擎资产自动化生成”的全链路闭环。

---

## 📂 项目结构 (Monorepo)
本仓库采用单体仓库结构，统一管理后端大脑与前端插件：

```plaintext
GameCraft-AI-Suite/
├── backend/                # Python 异步后端 (FastAPI)
│   ├── main.py             # API 网关 (路由: /chat, /compile)
│   ├── brain_test.py       # 多智能体调度引擎 (Creator/Critic/Architect)
│   └── requirements.txt    # 后端依赖清单
├── godot_project/          # Godot 4.x 完整开发工程
│   ├── addons/             # GameCraft AI 核心插件
│   ├── CoreSystems/        # AI 具现化生成的蓝图与脚本
│   └── project.godot       # Godot 项目文件
├── config.json             # API 供应商配置 (需填入 SiliconFlow Key)
├── start.bat               # Windows 一键启动脚本
└── .gitignore              # 工业级 Git 忽略规则 (保护 API Key)