import os
import requests
import json
import re

# ==========================================
# 0. 配置你的大模型 API (持久化配置版)
# ==========================================
CONFIG_FILE = "config.json"

def load_config():
    """加载或初始化多模型配置文件"""
    if not os.path.exists(CONFIG_FILE):
        default_config = {
            "active_provider": "deepseek",  # 当前正在使用的模型供应商
            "providers": {
                "deepseek": {
                    "api_key": "sk-请在这里填入你的DeepSeek_API_Key",
                    "base_url": "https://api.deepseek.com/chat/completions",
                    "model": "deepseek-chat"
                },
                "local_ollama": {
                    "api_key": "ollama",
                    "base_url": "http://127.0.0.1:11434/v1/chat/completions",
                    "model": "qwen2.5:7b"
                },
                "custom_model": {
                    "api_key": "sk-填入其他的API_Key",
                    "base_url": "https://api.openai.com/v1/chat/completions",
                    "model": "gpt-4o"
                }
            }
        }
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(default_config, f, indent=4, ensure_ascii=False)
        print(f"⚠️ 注意: 已在当前目录下自动生成 {CONFIG_FILE} 配置文件。")
        print(f"请打开 {CONFIG_FILE} 填入真实的 API Key 后重新运行！")
        # 第一次生成配置后直接退出，提醒用户去填 Key
        exit(1)
        
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# 初始化并加载配置
app_config = load_config()
active_provider_name = app_config.get("active_provider", "deepseek")
provider_config = app_config.get("providers", {}).get(active_provider_name, {})

# 提取当前激活的配置信息
API_KEY = provider_config.get("api_key", "").strip()
BASE_URL = provider_config.get("base_url", "").strip()
MODEL = provider_config.get("model", "").strip()

def ask_ai(system_prompt: str, user_prompt: str, temperature=0.7):
    """封装请求大模型的基础函数"""
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"}
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": temperature
    }
    response = requests.post(BASE_URL, headers=headers, json=payload, timeout=60)
    response.raise_for_status()
    return response.json()['choices'][0]['message']['content']


# ==========================================
# 核心：智能体辩论推演管线
# ==========================================
def run_brain_pipeline(user_idea: str):
    print(f"\n🚀 [宏观大脑] 收到玩家点子：{user_idea}")
    print(f"🔌 当前使用模型：[{active_provider_name}] -> {MODEL}")
    print("-" * 50)

    # ------------------------------------------------
    # 第一步：主策划出草案
    # ------------------------------------------------
    print("👨‍🎨 [主策划 Agent] 正在思考游戏核心机制...")
    creator_sys = "你是一个资深游戏主策划。请根据玩家的点子，设计一个包含【核心资源】、【核心循环(怎么获取/怎么消耗)】、【胜负条件】的初步草案。不要写代码，只写逻辑设定。"
    draft = ask_ai(creator_sys, user_idea)
    print(f"📜 草案生成完毕 (字数: {len(draft)})")
    
    # ------------------------------------------------
    # 第二步：杠精挑刺与沙盒推演
    # ------------------------------------------------
    print("\n🕵️‍♂️ [逻辑杠精 Agent] 正在进行沙盒推演与挑刺...")
    critic_sys = """你是一个极其严苛的数值与逻辑策划。你的任务是审查主策划的草案。
    请强制检查：1. 资源是否有获取和消耗的完美闭环？ 2. 胜负条件是否可能卡死？
    如果你发现了漏洞（比如只给玩家钱没地方花），请严厉指出，并直接给出【修正后的完整逻辑】。"""
    
    refined_draft = ask_ai(critic_sys, f"请审查以下草案，指出漏洞并给出最终修正版：\n{draft}", temperature=0.3)
    print("⚔️ 杠精推演完毕！已修补潜在逻辑漏洞。")

    # ------------------------------------------------
    # 第三步：架构师输出 JSON 蓝图
    # ------------------------------------------------
    print("\n👷‍♂️ [架构总工 Agent] 正在将最终逻辑编译为结构化 JSON 蓝图...")
    architect_sys = """你是一个 Godot 游戏架构师。请将输入的游戏逻辑，严格转化为以下 JSON 格式（不要输出任何 Markdown 标记或多余文字，只输出纯 JSON）：
    {
        "GameName": "游戏英文名",
        "CoreSystems": ["系统1(如 EconomySystem)", "系统2"],
        "RequiredVariables": {"变量1": "初始值"},
        "RequiredSlots": ["插槽1(如 赚钱行为)", "插槽2"]
    }"""
    
    final_json_str = ask_ai(architect_sys, f"请把这份经过严密推演的文档转化为 JSON 蓝图：\n{refined_draft}", temperature=0.1)
    
    # 清洗可能带有的 Markdown 格式
    match = re.search(r'\{.*\}', final_json_str, re.DOTALL)
    clean_json = match.group(0) if match else final_json_str.strip()

    print("-" * 50)
    print("\n✅ [宏观大脑] 终极 JSON 蓝图生成成功！")
    print(clean_json)
    
    return clean_json

# ==========================================
# 执行测试
# ==========================================
if __name__ == "__main__":
    # 我们的零号测试用例
    my_idea = "我要做一款2D生存模拟游戏《金陵求生记》。玩家初始资金 1700，需要在古金陵城生存 30 天。玩家每天会消耗饥饿度，可以通过去秦淮河抄书等方式赚钱。"
    
    try:
        run_brain_pipeline(my_idea)
    except Exception as e:
        print(f"❌ 大脑运行崩溃: {e}")