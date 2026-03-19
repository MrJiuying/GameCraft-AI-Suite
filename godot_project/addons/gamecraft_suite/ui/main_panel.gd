@tool
extends Control

# 绑定 UI 节点
@onready var chat_history = $VBoxContainer/ChatHistory
@onready var input_edit = $VBoxContainer/InputEdit
@onready var chat_btn = $VBoxContainer/ButtonRow/ChatBtn
@onready var compile_btn = $VBoxContainer/ButtonRow/CompileBtn
@onready var output_label = $VBoxContainer/OutputLabel
@onready var build_btn = $VBoxContainer/BuildBtn
@onready var http_request = $HTTPRequest

# 状态变量
var chat_messages = [] # 用来保存你们的对话历史
var current_request_type = "" # 记录当前是在"聊天"还是在"编译"

func _ready():
	chat_btn.pressed.connect(_on_chat_pressed)
	compile_btn.pressed.connect(_on_compile_pressed)
	build_btn.pressed.connect(_on_build_pressed)
	http_request.request_completed.connect(_on_http_request_completed)
	
	# 初始化欢迎语
	chat_history.text = "🤖 [主策划]：你好！我是 GameCraft 首席策划。请用一句话告诉我你想做个什么游戏？\n"

# ================= 阶段一：共创探讨 =================
func _on_chat_pressed():
	var text = input_edit.text.strip_edges()
	if text == "": return
	
	# 1. 更新 UI 表现
	chat_history.text += "\n👤 [你]: " + text + "\n"
	input_edit.text = "" # 清空输入框
	chat_btn.disabled = true
	chat_btn.text = "策划思考中..."
	
	# 2. 保存到上下文
	chat_messages.append({"role": "user", "content": text})
	
	# 3. 发送请求给后端的"聊天"接口
	current_request_type = "chat"
	var url = "http://127.0.0.1:8001/api/brain/chat"
	var body = JSON.stringify({"messages": chat_messages})
	http_request.request(url, ["Content-Type: application/json"], HTTPClient.METHOD_POST, body)

# ================= 阶段二：编译蓝图 =================
func _on_compile_pressed():
	if chat_messages.size() == 0:
		output_label.text = "⚠️ 请先和策划讨论游戏设定！"
		return
		
	compile_btn.disabled = true
	compile_btn.text = "🧠 杠精与架构师正在编译蓝图 (需1-3分钟)..."
	output_label.text = "正在将讨论记录转化为严谨的 JSON 蓝图，请等待..."
	
	# 将所有的聊天记录打包，发给后端的"编译"接口
	current_request_type = "compile"
	var url = "http://127.0.0.1:8001/api/brain/compile"
	var body = JSON.stringify({"messages": chat_messages})
	http_request.request(url, ["Content-Type: application/json"], HTTPClient.METHOD_POST, body)

# ================= 统一的网络回调 =================
func _on_http_request_completed(_result, response_code, _headers, body):
	var response_text = body.get_string_from_utf8()
	
	# 处理聊天的回复
	if current_request_type == "chat":
		chat_btn.disabled = false
		chat_btn.text = "💬 发送讨论"
		if response_code == 200:
			var res = JSON.parse_string(response_text)
			var reply = res.get("reply", "出错了...")
			chat_history.text += "\n🤖 [主策划]: " + reply + "\n"
			# 把 AI 的回复也存入上下文
			chat_messages.append({"role": "assistant", "content": reply})
		else:
			chat_history.text += "\n❌ [网络错误] 请确保 Python 后端已启动且接口正确。\n"
			
	# 处理编译的回复
	elif current_request_type == "compile":
		compile_btn.disabled = false
		compile_btn.text = "✨ 敲定创意并编译蓝图"
		if response_code == 200:
			var res = JSON.parse_string(response_text)
			output_label.text = JSON.stringify(res.get("data", {}), "\t")
		else:
			output_label.text = "❌ 编译失败，状态码: " + str(response_code) + "\n" + response_text

# ================= 阶段三：资产具现化 =================
func _on_build_pressed():
	var json_text = output_label.text
	if json_text == "" or json_text.begins_with("❌") or json_text.begins_with("⚠️") or json_text.begins_with("正在"):
		output_label.text = "⚠️ 请先成功编译蓝图！"
		return
		
	var data = JSON.parse_string(json_text)
	if typeof(data) != TYPE_DICTIONARY:
		output_label.text = "❌ 蓝图格式错误！"
		return
		
	build_btn.text = "🧱 正在自动构建游戏资产..."
	build_btn.disabled = true
	
	var target_dir = "res://CoreSystems"
	if not DirAccess.dir_exists_absolute(target_dir):
		DirAccess.make_dir_absolute(target_dir)
	
	# 保存蓝图
	var json_file = FileAccess.open(target_dir + "/blueprint.json", FileAccess.WRITE)
	if json_file:
		json_file.store_string(json_text)
		json_file.close()

	# 生成脚本
	var script_code = "extends Node2D\n\n# 🤖 AI 自动生成脚本\n\n"
	if data.has("RequiredVariables"):
		for v in data["RequiredVariables"].keys():
			var safe_val = JSON.stringify(data["RequiredVariables"][v])
			var safe_var_name = str(v).replace(" ", "_")
			script_code += "var " + safe_var_name + " = " + safe_val + "\n"
	
	script_code += "\nfunc _ready():\n"
	script_code += "\tprint(\"✅ " + str(data.get("GameName", "游戏")) + " 场景已加载！\")\n"
	
	var gd_file_path = target_dir + "/GameManager.gd"
	var gd_file = FileAccess.open(gd_file_path, FileAccess.WRITE)
	gd_file.store_string(script_code)
	gd_file.close()

	# 生成场景
	var tscn_path = target_dir + "/MainGame.tscn"
	var tscn_code = "[gd_scene load_steps=2 format=3]\n\n"
	tscn_code += "[ext_resource type=\"Script\" path=\"" + gd_file_path + "\" id=\"1_script\"]\n\n"
	tscn_code += "[node name=\"MainGame\" type=\"Node2D\"]\n"
	tscn_code += "script = ExtResource(\"1_script\")\n"
	
	var tscn_file = FileAccess.open(tscn_path, FileAccess.WRITE)
	tscn_file.store_string(tscn_code)
	tscn_file.close()
	
	if Engine.is_editor_hint():
		EditorInterface.get_resource_filesystem().scan()
	
	output_label.text = "🎉 具现化全流程完成！(文件已在 res://CoreSystems 目录生成)"
	build_btn.text = "✨ 具现化蓝图 (自动生成脚本与节点)"
	build_btn.disabled = false
