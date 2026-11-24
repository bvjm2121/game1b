extends VBoxContainer

var art := TextureRect.new()
var status := Label.new()
var choices := HBoxContainer.new()
var stage := 0
var misses := 0
var scores: Array[int] = []
var award := TextureRect.new()
var font := SystemFont.new()

func _ready() -> void:
	font.font_names = PackedStringArray(["PingFang TC", "Microsoft JhengHei", "Noto Sans CJK TC"])
	theme = Theme.new()
	theme.default_font = font
	theme.default_font_size = 19
	add_child(art)
	art.custom_minimum_size.y = 350
	art.size_flags_vertical = Control.SIZE_EXPAND_FILL
	art.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	art.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
	show_art("a")
	var styles := HBoxContainer.new()
	add_child(styles)
	for pair in [["雪夜燈火","a"],["晴空競技場","b"],["微縮雪村","c"]]:
		button(styles,pair[0],show_art.bind(pair[1]))
	add_child(status)
	status.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	add_child(choices)
	add_child(award)
	award.texture = texture_for("res://quest-key.png")
	award.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	award.custom_minimum_size.y = 64
	award.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	play_stage()

func show_art(key: String) -> void:
	art.texture = texture_for("res://%s.jpg" % key)

func button(parent: Container, caption: String, action: Callable) -> void:
	var item := Button.new()
	item.text = caption
	item.pressed.connect(action)
	parent.add_child(item)

func clear_choices() -> void:
	for child in choices.get_children():
		choices.remove_child(child)
		child.queue_free()

func play_stage() -> void:
	clear_choices()
	award.hide()
	misses = 0
	if stage == 0:
		status.text = "第一關｜100 枚金幣要買 35 元午餐，明天還需要 25 元車票。挑一袋！"
		for plan in [["午餐 35 ＋ 煙火 65",false],["午餐 35 ＋ 車票 25 ＋ 貼紙 15",true],["午餐 35 ＋ 車票 25 ＋ 雪橇 55",false]]:
			button(choices,plan[0],submit.bind(plan[1]))
	elif stage == 1:
		status.text = "第二關｜100 枚金幣先留至少 40 枚餐費，其餘分給兩家攤位。"
		for plan in [["餐費 20／熱湯 40／冰果 40",false],["餐費 40／熱湯 60／冰果 0",false],["餐費 40／熱湯 30／冰果 30",true]]:
			button(choices,plan[0],submit.bind(plan[1]))
	else:
		status.text = "寶庫開啟！預算 %d / 50 分，投資分配 %d / 50 分。共取得兩把鑰匙。" % scores
		button(choices,"再玩一次",restart)

func submit(correct: bool) -> void:
	if not correct:
		misses += 1
		status.text = "再看看：午餐、車票都要留，而且總額最多 100。" if stage == 0 else "先留足餐費，兩家攤位都要分到金幣。"
		return
	scores.append(maxi(30,50-5*misses))
	status.text = "取得鑰匙！本關 %d / 50 分，調整了 %d 次。" % [scores.back(), misses]
	stage += 1
	clear_choices()
	award.show()
	button(choices,"繼續",play_stage)

func restart() -> void:
	stage = 0
	scores.clear()
	play_stage()

func texture_for(path: String) -> Texture2D:
	if ResourceLoader.exists(path):
		return load(path)
	return ImageTexture.create_from_image(Image.load_from_file(path))
