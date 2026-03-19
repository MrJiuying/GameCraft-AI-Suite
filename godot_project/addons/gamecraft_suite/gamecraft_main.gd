@tool
extends EditorPlugin

var dock_panel: Control

func _enter_tree() -> void:
	# 关键修改：加载我们刚刚制作的 UI 场景！
	dock_panel = preload("res://addons/gamecraft_suite/ui/MainPanel.tscn").instantiate()
	
	# 将面板添加到 Godot 底部区域
	add_control_to_bottom_panel(dock_panel, "GameCraft AI")

func _exit_tree() -> void:
	if dock_panel:
		remove_control_from_bottom_panel(dock_panel)
		dock_panel.queue_free()
