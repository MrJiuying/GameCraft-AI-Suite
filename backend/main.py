from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import json

# 导入刚才在 brain_test 里写好的两个新函数
from brain_test import chat_with_creator, compile_blueprint

app = FastAPI()

# 定义接收的数据结构（接收一个由字典组成的列表）
class ChatRequest(BaseModel):
    messages: list

@app.post("/api/brain/chat")
async def api_chat(req: ChatRequest):
    """接收上帝视角(Godot)发来的聊天记录，返回主策划的回答"""
    try:
        reply = chat_with_creator(req.messages)
        return {"reply": reply}
    except Exception as e:
        print(f"❌ 聊天接口报错: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/brain/compile")
async def api_compile(req: ChatRequest):
    """接收完整聊天记录，触发杠精和架构师编译最终 JSON 蓝图"""
    try:
        blueprint_str = compile_blueprint(req.messages)
        # 尝试将字符串解析为真正的 JSON 字典发回给 Godot
        blueprint_dict = json.loads(blueprint_str)
        return {"data": blueprint_dict}
    except json.JSONDecodeError as e:
        print(f"❌ JSON解析失败: {blueprint_str}")
        raise HTTPException(status_code=500, detail="AI 返回的不是合法 JSON 格式")
    except Exception as e:
        print(f"❌ 编译接口报错: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    print("\n" + "="*50)
    print("🚀 GameCraft AI Suite 极客共创版 后端启动中...")
    print("📡 监听地址: http://127.0.0.1:8001")
    print("🛠️ 已挂载路由: /api/brain/chat, /api/brain/compile")
    print("="*50 + "\n")
    
    uvicorn.run(app, host="127.0.0.1", port=8001)