import os
import requests
import json
import re
import sys
import chromadb

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
# 🧰 架构师工具箱 (Function Calling Schemas)
# ==========================================
gamecraft_tools = [
    {
        "type": "function",
        "function": {
            "name": "generate_text_rpg_blueprint",
            "description": "当玩家需要进行战斗、炼丹、买卖、多选一决策或数值扣除时，调用此工具生成文字RPG蓝图。",
            "parameters": {
                "type": "object",
                "properties": {
                    "GameName": {"type": "string", "description": "游戏名称"},
                    "GameMode": {"type": "string", "enum": ["TextRPG"]},
                    "RequiredUI": {
                        "type": "array",
                        "description": "UI节点列表，包含按钮和数值标签",
                        "items": {
                            "type": "object",
                            "properties": {
                                "NodeName": {"type": "string", "description": "节点英文名，如 AttackBtn"},
                                "NodeType": {"type": "string", "enum": ["Button", "Label", "ProgressBar"]},
                                "Text": {"type": "string", "description": "按钮或标签上显示的中文文本"},
                                "BindVariable": {"type": "string", "description": "绑定的全局变量名，如 HP"},
                                "Requires": {
                                    "type": "object", 
                                    "description": "前置条件，例如 {'HP': '>= 50'}"
                                },
                                "OnClick": {
                                    "type": "object", 
                                    "description": "数值变化，值必须是带正负号的纯数字，严禁使用公式！例如 {'HP': '-50'}"
                                },
                                "SuccessMessage": {"type": "string"},
                                "FailMessage": {"type": "string"}
                            },
                            "required": ["NodeName", "NodeType", "Text"]
                        }
                    }
                },
                "required": ["GameName", "GameMode", "RequiredUI"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_visual_novel_blueprint",
            "description": "当玩家需要纯剧情演出、角色对话、不涉及复杂数值交互时，调用此工具生成视觉小说蓝图。",
            "parameters": {
                "type": "object",
                "properties": {
                    "GameName": {"type": "string"},
                    "GameMode": {"type": "string", "enum": ["VisualNovel"]},
                    "Background": {"type": "string", "description": "场景背景描述，如 '秦淮河畔_夜晚'"},
                    "Dialogues": {
                        "type": "array",
                        "description": "角色对话列表",
                        "items": {
                            "type": "object",
                            "properties": {
                                "Speaker": {"type": "string", "description": "说话人名字，如 '苏星梦'"},
                                "Text": {"type": "string", "description": "对话内容"},
                                "Emotion": {"type": "string", "enum": ["Normal", "Angry", "Smile", "Sad"]}
                            },
                            "required": ["Speaker", "Text", "Emotion"]
                        }
                    },
                    "NextScene": {"type": "string", "description": "对话结束后的下一步跳转"}
                },
                "required": ["GameName", "GameMode", "Background", "Dialogues"]
            }
        }
    }
]

# ==========================================
# 1. 核心 AI 请求函数 (纯净版)
# ==========================================
def ask_ai_raw(messages: list, temperature=0.7):
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
    
    timeout_sec = 300 if temperature < 0.5 else 60 
    response = requests.post(BASE_URL, headers=headers, json=payload, timeout=timeout_sec)
    
    if response.status_code != 200:
        err = response.json() if response.text else response.reason
        raise RuntimeError(f"API 拒绝访问 ({response.status_code}): {err}")
        
    return response.json()['choices'][0]['message'].get('content', '')

# ==========================================
# 2. 阶段一：头脑风暴 (搭载 RAG 记忆引擎的主策划)
# ==========================================
def chat_with_creator(chat_history: list):
    # 从聊天记录中抓取玩家最后说的一句话，作为搜索词
    user_input = chat_history[-1]["content"] if chat_history else ""
    
    print(f"\n🔍 正在检索玉简记忆，搜索关键词：[{user_input[:15]}...]")
    # 核心：去记忆库里把相关的设定捞出来！
    relevant_lore = search_lore(user_input)
    print(f"💡 检索到相关设定：\n{relevant_lore}\n")
    
    # 将捞出来的记忆动态注入给主策划
    system_prompt = (
        "你是一个顶级的游戏主策划，负责将小说设定转化为游戏玩法。\n"
        "【以下是从记忆库中检索到的相关小说设定，请严格遵守】：\n"
        "------------------\n"
        f"{relevant_lore}\n"
        "------------------\n"
        "请基于以上设定，与用户探讨设计方案。回复要简短专业，并且必须准确使用上述设定里的专有名词（如角色、武器、属性）。"
    )
    
    print("🤖 [主策划] 正在结合小说记忆思考你的点子...")
    messages = [{"role": "system", "content": system_prompt}] + chat_history
    reply = ask_ai_raw(messages, temperature=0.7)
    
    print(f"💬 策划回复: {reply}")
    return reply

import json

# ==========================================
# 3. 阶段二：蓝图编译 (断绝闲聊的终极剥离版)
# ==========================================
def compile_blueprint(chat_history: list):
    print("🧠 架构总工正在提取聊天材料并强行生成 JSON...")
    
    architect_sys = (
        "你是一个神级游戏架构总工。你的唯一任务是将策划方案编译为严格的JSON蓝图。\n"
        "【绝对指令】：不要打招呼！不要问问题！不要确认！绝对不要输出任何思考过程或 ```json 标记！必须且只能输出一个纯JSON字典！\n\n"
        "【模板一：TextRPG (适用战斗、炼丹、数值判定)】\n"
        "{\n"
        '  "GameName": "游戏",\n'
        '  "GameMode": "TextRPG",\n'
        '  "RequiredUI": [\n'
        '    {"NodeName": "ActionBtn", "NodeType": "Button", "Text": "动作", "Requires": {"HP": ">= 50"}, "OnClick": {"HP": "-50"}, "SuccessMessage": "成功", "FailMessage": "失败"}\n'
        '  ]\n'
        "}\n\n"
        "【模板二：VisualNovel (适用纯剧情、对话)】\n"
        "{\n"
        '  "GameName": "游戏",\n'
        '  "GameMode": "VisualNovel",\n'
        '  "Background": "秦淮河畔_夜晚",\n'
        '  "Dialogues": [\n'
        '    {"Speaker": "苏星梦", "Text": "笨蛋！", "Emotion": "Angry"}\n'
        '  ],\n'
        '  "NextScene": "TextRPG"\n'
        "}\n"
    )
    
    # 🌟 核心杀招：把聊天记录压扁成一段“死”文本，彻底切断它的聊天惯性！
    transcript = ""
    for msg in chat_history:
        role_name = "玩家" if msg["role"] == "user" else "策划"
        transcript += f"[{role_name}]: {msg['content']}\n"
        
    user_prompt = (
        f"【以下是你们刚才的讨论记录材料】：\n"
        f"------------------\n"
        f"{transcript}\n"
        f"------------------\n"
        f"【强制任务】：请阅读上述材料，提炼出最终确定的方案，直接输出符合上述模板的 JSON 代码。立刻开始输出，第一字符必须是 {{"
    )
    
    # 把它变成一个干净的两回合问答
    messages = [
        {"role": "system", "content": architect_sys},
        {"role": "user", "content": user_prompt}
    ]
    
    try:
        # 温度调到 0.3，不冷不热，最适合这种信息提取任务
        raw_output = ask_ai_raw(messages=messages, temperature=0.3)
        
        # 暴力清洗
        start = raw_output.find('{')
        end = raw_output.rfind('}')
        
        if start != -1 and end != -1:
            clean_json_str = raw_output[start:end+1]
            try:
                json.loads(clean_json_str) 
                print("✅ 成功截获完美 JSON 蓝图！")
                return clean_json_str
            except json.JSONDecodeError as e:
                print(f"❌ JSON 语法瑕疵: {e}")
                return json.dumps({"GameName": "Error", "GameMode": "TextRPG", "RequiredUI": [{"NodeName": "Error", "NodeType": "Button", "Text": "JSON解析失败"}]})
        else:
            print(f"❌ 未找到有效的 JSON 结构。原始回复:\n{raw_output}")
            return json.dumps({"GameName": "Error", "GameMode": "TextRPG", "RequiredUI": [{"NodeName": "Error", "NodeType": "Button", "Text": "AI未按格式输出"}]})

    except Exception as e:
        print(f"❌ 编译蓝图异常: {e}")
        return json.dumps({"GameName": "Error", "GameMode": "TextRPG", "RequiredUI": [{"NodeName": "Error", "NodeType": "Button", "Text": "后端异常"}]})


# ==========================================
# 🔍 记忆检索工具 (RAG)
# ==========================================
def search_lore(query_text: str, n_results: int = 2) -> str:
    """根据用户的输入，去本地向量库检索最相关的小说设定"""
    try:
        client = chromadb.PersistentClient(path="./lore_db")
        collection = client.get_collection(name="novel_worldview")
        
        # 向量相似度搜索
        results = collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        
        if results['documents'] and results['documents'][0]:
            # 将搜到的相关记忆块拼合起来
            return "\n".join(results['documents'][0])
        return "未找到相关的详细设定。"
    except Exception as e:
        return f"记忆检索失败: {str(e)}"