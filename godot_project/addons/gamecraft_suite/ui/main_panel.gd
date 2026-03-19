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

# ================= 阶段三：资产具现化 (V2.0 可视化升级版) =================
func _on_build_pressed():
	# 1. 获取 JSON 数据并校验
	var json_text = output_label.text
	if json_text == "" or json_text.begins_with("❌") or json_text.begins_with("⚠️") or json_text.begins_with("正在"):
		output_label.text = "⚠️ 请先成功编译蓝图！"
		return
		
	var data = JSON.parse_string(json_text)
	if typeof(data) != TYPE_DICTIONARY:
		output_label.text = "❌ 蓝图格式错误！"
		return
		
	build_btn.text = "🧱 正在自动构建 2.0 可视化资产..."
	build_btn.disabled = true
	
	var target_dir = "res://CoreSystems"
	if not DirAccess.dir_exists_absolute(target_dir):
		DirAccess.make_dir_absolute(target_dir)
	
	# 2. 保存蓝图文件
	var json_file = FileAccess.open(target_dir + "/blueprint.json", FileAccess.WRITE)
	if json_file:
		json_file.store_string(json_text)
		json_file.close()

	# ==========================================
	# 3. 生成脚本 (GameManager.gd) - 🤖 V2.2 动态逻辑版
	# ==========================================
	var script_code = "extends Node2D\n\n# 🤖 AI V2.2 自动生成脚本\n\n"
	if data.has("RequiredVariables"):
		for v in data["RequiredVariables"].keys():
			var safe_val = JSON.stringify(data["RequiredVariables"][v])
			var safe_var_name = str(v).replace(" ", "_")
			script_code += "var " + safe_var_name + " = " + safe_val + "\n"
	
	script_code += "\n@onready var ui_layout = $UILayer/UILayout\n"
	
	script_code += "\nfunc _ready():\n"
	script_code += "\tprint(\"✅ " + str(data.get("GameName", "游戏")) + " V2.2 场景已加载！\")\n"
	
	if data.has("RequiredUI"):
		for ui in data["RequiredUI"]:
			if ui.get("NodeType") == "Button":
				var node_name = str(ui.get("NodeName")).replace(" ", "_")
				script_code += "\tui_layout.get_node(\"" + node_name + "\").pressed.connect(_on_" + node_name + "_pressed)\n"

	script_code += "\nfunc _process(delta):\n"
	if data.has("RequiredUI"):
		for ui in data["RequiredUI"]:
			var node_name = str(ui.get("NodeName")).replace(" ", "_")
			var bind_var = str(ui.get("BindVariable", "")).replace(" ", "_")
			if bind_var != "":
				if ui.get("NodeType") == "Label":
					script_code += "\tui_layout.get_node(\"" + node_name + "\").text = \"" + ui.get("Text") + ": \" + str(" + bind_var + ")\n"
				elif ui.get("NodeType") == "ProgressBar":
					script_code += "\tui_layout.get_node(\"" + node_name + "\").value = " + bind_var + "\n"

	# --- ⚠️ 核心修复区：确保按钮点击逻辑只生成一次 ---
	if data.has("RequiredUI"):
		for ui in data["RequiredUI"]:
			if ui.get("NodeType") == "Button":
				var node_name = str(ui.get("NodeName")).replace(" ", "_")
				script_code += "\nfunc _on_" + node_name + "_pressed():\n"
				script_code += "\tprint(\"触发动作: " + node_name + "\")\n"
				
				# 读取 AI 动态生成的 OnClick 字典
				if ui.has("OnClick") and typeof(ui["OnClick"]) == TYPE_DICTIONARY:
					var clicks = ui["OnClick"]
					for var_name in clicks.keys():
						var safe_var = str(var_name).replace(" ", "_")
						var change_val = str(clicks[var_name]).replace("%", "")
						script_code += "\t" + safe_var + " += (" + change_val + ")\n"
				else:
					script_code += "\tpass # AI 未配置数值逻辑\n"
	
	# 保存生成的 GameManager.gd
	var gd_file_path = target_dir + "/GameManager.gd"
	var gd_file = FileAccess.open(gd_file_path, FileAccess.WRITE)
	gd_file.store_string(script_code)
	gd_file.close()

	# 4. 生成场景并自动拼装 UI (V2.0 核心逻辑)
	var tscn_path = target_dir + "/MainGame.tscn"
	var tscn_code = "[gd_scene load_steps=2 format=3]\n\n"
	tscn_code += "[ext_resource type=\"Script\" path=\"" + gd_file_path + "\" id=\"1_script\"]\n\n"
	tscn_code += "[node name=\"MainGame\" type=\"Node2D\"]\n"
	tscn_code += "script = ExtResource(\"1_script\")\n\n"
	
	# 自动创建 UI 画布层
	tscn_code += "[node name=\"UILayer\" type=\"CanvasLayer\" parent=\".\"]\n\n"
	
	# 自动创建垂直排版容器
	tscn_code += "[node name=\"UILayout\" type=\"VBoxContainer\" parent=\"UILayer\"]\n"
	tscn_code += "offset_left = 30.0\n"
	tscn_code += "offset_top = 30.0\n"
	tscn_code += "offset_right = 350.0\n"
	tscn_code += "offset_bottom = 500.0\n"
	tscn_code += "theme_override_constants/separation = 15\n\n"
	
	# 动态解析蓝图中的 UI 需求并生成控件
	if data.has("RequiredUI"):
		for ui_info in data["RequiredUI"]:
			var node_name = str(ui_info.get("NodeName", "Node")).replace(" ", "_").replace("-", "_")
			var node_type = ui_info.get("NodeType", "Label")
			var text = ui_info.get("Text", "")
			
			tscn_code += "[node name=\"" + node_name + "\" type=\"" + node_type + "\" parent=\"UILayer/UILayout\"]\n"
			tscn_code += "layout_mode = 2\n"
			
			if node_type == "Label" or node_type == "Button":
				tscn_code += "text = \"" + text + "\"\n"
			elif node_type == "ProgressBar":
				tscn_code += "value = 100.0\n"
			tscn_code += "\n"
	
	var tscn_file = FileAccess.open(tscn_path, FileAccess.WRITE)
	tscn_file.store_string(tscn_code)
	tscn_file.close()
	
	# 刷新编辑器文件系统
	if Engine.is_editor_hint():
		EditorInterface.get_resource_filesystem().scan()
	
	output_label.text = "🎉 V2.0 具现化完成！请双击 MainGame.tscn 查看效果！"
	build_btn.text = "✨ 具现化蓝图 (自动生成脚本与节点)"
	build_btn.disabled = false
	
	
	
# ================= 极客功能：JSON 蓝图直接具现化 =================

# 1. 允许放置 (控制台疯狂刷屏说明这步 OK 了)
func _can_drop_data(_at_position, data):
	return typeof(data) == TYPE_DICTIONARY and data.get("type") == "files"

# 2. 执行放置 (松手瞬间触发)
func _drop_data(_at_position, data):
	var files = data.get("files", [])
	if files.size() > 0:
		var path = files[0]
		print("🚀 [系统] 捕获到松手动作，准备处理文件: ", path)
		
		var file = FileAccess.open(path, FileAccess.READ)
		if not file:
			print("❌ [错误] 无法读取文件: ", path)
			return
			
		var content = file.get_as_text()
		file.close()
		
		if path.get_extension().to_lower() == "json":
			print("📦 [系统] 检测到 JSON 蓝图，准备自动具现化...")
			output_label.text = content # 填充中间黑框
			_on_build_pressed() # 👈 关键：直接触发你的生成按钮逻辑
		else:
			print("📝 [系统] 检测到文本文件，填充输入框")
			input_edit.text = content
