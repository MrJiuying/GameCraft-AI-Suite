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

✨ 核心特性
1. 💬 共创讨论室 (Co-creation Workshop)
对话式推演：与 AI 主策划 像聊天一样讨论游戏设定。

记忆能力：支持多轮对话，AI 会主动反问并引导你完善世界观。

2. 🧠 三智能体协作管线 (Agent Pipeline)
系统会自动启动“三方会审”：

主策划 (Creator)：整理对话记录，形成初步草案。

逻辑杠精 (Critic)：进行数值推演，修补机制漏洞。

架构总工 (Architect)：将最终共识编译为严谨的 JSON 蓝图。

3. 🧱 资产具现化 (Asset Instantiation)
一键将 JSON 蓝图转化为 Godot 原生资产：

代码注入：自动生成 GameManager.gd，并将 AI 设定的变量直接写入代码。

场景组装：自动生成 MainGame.tscn 场景并挂载对应脚本。

🚀 快速开始
1. 配置环境
在根目录的 config.json 中填入你的 SiliconFlow API Key。

2. 启动后端大脑
双击根目录下的 start.bat。脚本会自动检查依赖并启动本地 8001 端口服务。

3. 启动 Godot 插件
使用 Godot 4.x 打开 godot_project 文件夹。

前往 项目 -> 项目设置 -> 插件，启用 GameCraft AI Suite。

在编辑器底部点击 GameCraft AI 标签页，开启共创之旅！

🗺️ V2.0 路线图 (即将到来)
[ ] 可视化 UI 自动生成：AI 将根据蓝图自动创建 Label、ProgressBar 等 UI 节点。

[ ] 行为逻辑合成：根据机制说明自动编写按钮点击事件代码。

[ ] 一键 Git 备份：在插件内直接集成 Git 提交功能。