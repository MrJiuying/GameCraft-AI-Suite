import os
import requests
import json
import re
import sys

# ==========================================
# 0. 配置加载 (保持不变)
# ==========================================
def load_config():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(current_dir)
    root_config = os.path.join(root_dir, "config.json")
    backend_config = os.path.join(current_dir, "config.json")
    config_path = root_config if os.path.exists(root_config) else backend_config

    if not os.path.exists(config_path):
        print(f"❌ 找不到配置文件！预期路径: {config_path}")
        sys.exit(1)
        
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f), config_path

app_config, ACTUAL_CONFIG_PATH = load_config()
p_name = app_config.get("active_provider", "none")
p_cfg = app_config.get("providers", {}).get(p_name, {})

def clean_val(val):
    if not val: return ""
    return "".join(c for c in str(val).strip().replace('"', '').replace("'", "") if ord(c) < 128)

API_KEY = clean_val(p_cfg.get("api_key", ""))
BASE_URL = clean_val(p_cfg.get("base_url", ""))
MODEL = clean_val(p_cfg.get("model", ""))

# ==========================================
# 1. 核心 AI 请求函数 (升级支持多轮对话)
# ==========================================
def ask_ai_raw(messages: list, temperature=0.7):
    """直接接收 OpenAI 格式的 messages 数组"""
    if not API_KEY or "请填入" in API_KEY:
        raise ValueError(f"API Key 未配置！检查文件: {ACTUAL_CONFIG_PATH}")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": temperature
    }
    
    # 聊天 60 秒足够，编译 JSON 给 300 秒防止超时
    timeout_sec = 300 if temperature < 0.5 else 60 
    response = requests.post(BASE_URL, headers=headers, json=payload, timeout=timeout_sec)
    
    if response.status_code != 200:
        err = response.json() if response.text else response.reason
        raise RuntimeError(f"API 拒绝访问 ({response.status_code}): {err}")
        
    return response.json()['choices'][0]['message']['content']

def ask_ai(system_prompt: str, user_prompt: str, temperature=0.7):
    """单轮请求的快捷封装"""
    msgs = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    return ask_ai_raw(msgs, temperature)

# ==========================================
# 2. 阶段一：共创探讨 (主策划单飞)
# ==========================================
def chat_with_creator(chat_history: list):
    print("\n👨‍🎨 [主策划] 正在思考你的点子...")
    system_prompt = "你是一个资深游戏主策划。请基于用户的点子进行探讨，给出核心机制建议，并主动抛出一个问题引导用户完善设定。请用精炼的中文回答，像聊天一样自然，不要输出冗长的列表。"
    
    # 把系统提示词塞进对话最前面
    messages = [{"role": "system", "content": system_prompt}] + chat_history
    reply = ask_ai_raw(messages, temperature=0.7)
    print(f"✅ 回复完成：{reply[:20]}...")
    return reply

# ==========================================
# 3. 阶段二：编译蓝图 (杠精 + 架构师)
# ==========================================
def compile_blueprint(chat_history: list):
    print("\n🚀 开始锁定创意，准备编译蓝图...")
    
    # 1. 整理对话上下文，让后面的 Agent 知道你们聊了啥
    context = "\n".join([f"[{m['role']}]: {m['content']}" for m in chat_history])
    
    # 2. 逻辑杠精出场
    print("🕵️‍♂️ 逻辑杠精正在审阅聊天记录，修补漏洞...")
    critic_sys = "你是一个严苛的数值策划。请阅读以下探讨记录，找出逻辑漏洞，并给出修正后的完整游戏机制设定（不需要抛出问题，直接给出最终设定结论）。"
    refined = ask_ai(critic_sys, f"【讨论记录】:\n{context}", temperature=0.3)
    
    # 3. 架构总工出场
    print("👷 架构总工正在将其转化为 JSON...")
    architect_sys = "将以下完整设定转化为纯 JSON 蓝图。格式必须包含: {\"GameName\":\"\", \"CoreSystems\":[{\"SystemName\":\"\", \"Components\":[{\"ComponentName\":\"\", \"Description\":\"\"}]}], \"RequiredVariables\":{}}。只输出JSON，绝对不要任何Markdown标记。"
    final_json = ask_ai(architect_sys, refined, temperature=0.1)
    
    match = re.search(r'\{.*\}', final_json, re.DOTALL)
    result = match.group(0) if match else final_json.strip()
    
    print("✅ 蓝图编译大功告成！")
    return result