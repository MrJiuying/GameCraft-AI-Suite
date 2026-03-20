extends Node2D

# 🎭 AI V3.0 视觉小说系统

var dialogues = [{"Emotion":"Angry","OnShow":{"怒气值":"+10"},"Speaker":"苏星梦","Text":"真是个笨蛋！"},{"OnShow":{"苏星梦_灵力":"-30%"},"Speaker":"系统","Text":"苏星梦进入掩护状态，为你生成了临时护盾。"},{"IsChoice":true,"OnSelect":{"NextDialogue":"沉默","苏星梦_辅助效果":"-20%"},"Speaker":"主角","Text":"多管闲事"},{"IsChoice":true,"OnSelect":{"NextDialogue":"感谢","全队_气血恢复速度":"+15%","持续":"60秒","激活天赋":"心软"},"Speaker":"主角","Text":"多谢"},{"Emotion":"Sad","Speaker":"苏星梦","Tag":"沉默","Text":"……（沉默不语）"},{"Emotion":"Tsundere","Speaker":"苏星梦","Tag":"感谢","Text":"哼，下次可没这么好运了。"}]
var current_idx = 0

@onready var name_label = $UILayer/VBox/NameLabel
@onready var text_label = $UILayer/VBox/TextLabel

func _ready():
	$UILayer/VBox/NextBtn.pressed.connect(_on_next_pressed)
	_show_dialogue()

func _show_dialogue():
	if current_idx < dialogues.size():
		var d = dialogues[current_idx]
		name_label.text = "【" + str(d.get("Speaker", "")) + "】"
		text_label.text = str(d.get("Text", ""))
	else:
		name_label.text = "【系统】"
		text_label.text = "剧情结束，等待下一步指示。"

func _on_next_pressed():
	current_idx += 1
	_show_dialogue()
