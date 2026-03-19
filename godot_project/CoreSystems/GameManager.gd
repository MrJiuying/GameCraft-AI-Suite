extends Node2D

# 🤖 AI V2.2 自动生成脚本

var CommonPill = 0.0
var Health = 100.0
var PremiumPill = 0.0
var SpiritStone = 100.0

@onready var ui_layout = $UILayer/UILayout

func _ready():
	print("✅ 炼丹模拟器 V2.2 场景已加载！")
	ui_layout.get_node("AlchemyButton").pressed.connect(_on_AlchemyButton_pressed)

func _process(delta):
	ui_layout.get_node("SpiritStoneLabel").text = "灵石: 100: " + str(SpiritStone)
	ui_layout.get_node("HealthLabel").text = "气血: 100: " + str(Health)
	ui_layout.get_node("CommonPillLabel").text = "普通丹药: 0: " + str(CommonPill)
	ui_layout.get_node("PremiumPillLabel").text = "极品丹药: 0: " + str(PremiumPill)
	ui_layout.get_node("HealthBar").value = Health

func _on_AlchemyButton_pressed():
	print("触发动作: AlchemyButton")
	CommonPill += (+1)
	Health += (-30)
	PremiumPill += (+1)
	SpiritStone += (-20)
