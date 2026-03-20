import chromadb
import os

print("🚀 开始初始化本地向量记忆库...")

# 1. 创建或连接到本地数据库文件夹 (它会在你当前目录下生成一个 lore_db 文件夹)
client = chromadb.PersistentClient(path="./lore_db")

# 2. 创建一个名为 "novel_worldview" 的集合 (Collection)
# 如果已经存在，就直接获取
collection = client.get_or_create_collection(name="novel_worldview")

# 3. 读取设定集
file_path = "worldview.txt"
if not os.path.exists(file_path):
    print("❌ 找不到 worldview.txt，请检查文件是否存在！")
    exit()

with open(file_path, "r", encoding="utf-8") as f:
    text_content = f.read()

# 4. 极简分块逻辑 (按双换行符切分段落)
# 在真实的复杂小说里我们会用 LangChain 切片，但现在为了极简，我们按段落切
chunks = [chunk.strip() for chunk in text_content.split('\n\n') if chunk.strip()]

# 5. 准备写入数据库的数据格式
documents = []
ids = []

for i, chunk in enumerate(chunks):
    documents.append(chunk)
    ids.append(f"lore_chunk_{i}") # 给每个记忆块打上唯一 ID

print(f"📦 成功将设定集切分为 {len(documents)} 个记忆块，准备进行向量化注入...")

# 6. 写入数据库 (Chroma 会自动在后台调用默认的 embedding 模型把文字变向量)
collection.add(
    documents=documents,
    ids=ids
)

print("✅ 记忆库构建完成！《金陵求生记》的世界观已永久刻入向量空间。")