extends Node3D

const SKINS := ["Night","Day","Felt"]
const SHOPS := [Vector3(-3.9,0,-1.58),Vector3(3.9,0,-1.58)]
var avatar := Node3D.new()
var camera := Camera3D.new()
var sun := DirectionalLight3D.new()
var style_nodes: Array[Node] = []
var clips: Array[AnimationPlayer] = []
var env := Environment.new()
var status := Label.new()
var sheet := PanelContainer.new()
var form := VBoxContainer.new()
var style_index := 0
var progress := 0
var awarded := false
var misses := [0,0]
var scores := [0,0]
var air_speed := 0.0
var elapsed := 0.0
var visit_until := 0.0

func spawn_model(file: String, parent: Node3D) -> Node3D:
	var doc := GLTFDocument.new()
	var state := GLTFState.new()
	var err := doc.append_from_buffer(FileAccess.get_file_as_bytes("res://"+file+".glb"),"",state)
	assert(err == OK)
	var result := doc.generate_scene(state) as Node3D
	parent.add_child(result)
	for obj in result.find_children("*","Node3D",true,false):
		for tag in SKINS:
			if str(obj.name).begins_with(tag+"_"):
				style_nodes.append(obj)
	return result

func _ready() -> void:
	add_child(avatar)
	var market := spawn_model("village",self)
	var model := spawn_model("courier",avatar)
	avatar.position=Vector3(0,0,3.35)
	for animator in model.find_children("*","AnimationPlayer",true,false):
		clips.append(animator)
	for i in range(2):
		var vendor := spawn_model("courier",self)
		vendor.position=Vector3(SHOPS[i].x,0,-4.45)
		vendor.scale=Vector3.ONE*.83
		for ap in vendor.find_children("*","AnimationPlayer",true,false):
			if ap.has_animation("HeadRig"):
				ap.play("HeadRig")
	var surroundings := WorldEnvironment.new()
	env.background_mode=Environment.BG_COLOR
	env.ambient_light_source=Environment.AMBIENT_SOURCE_COLOR
	env.fog_enabled=true
	env.fog_density=.026
	surroundings.environment=env
	add_child(surroundings)
	add_child(sun)
	sun.rotation_degrees=Vector3(-52,-33,0)
	sun.shadow_enabled=true
	add_child(camera)
	camera.current=true
	camera.position=Vector3(0,3.3,8.7)
	var hud:=CanvasLayer.new()
	add_child(hud)
	var bar:=VBoxContainer.new()
	hud.add_child(bar)
	bar.position=Vector2(16,16)
	bar.add_child(status)
	var styles:=HBoxContainer.new()
	bar.add_child(styles)
	for i in range(3):
		add_button(styles,["雪夜燈火","晴空競技場","微縮雪村"][i],set_style.bind(i))
	hud.add_child(sheet)
	sheet.position=Vector2(30,170)
	sheet.add_child(form)
	sheet.hide()
	set_style(0)
	market.set_meta("source","Blender")

func add_button(parent: Container, caption: String, action: Callable) -> void:
	var btn:=Button.new()
	btn.text=caption
	btn.pressed.connect(action)
	parent.add_child(btn)

func set_style(i:int) -> void:
	style_index=i
	for obj in style_nodes:
		obj.visible=str(obj.name).begins_with(SKINS[i]+"_")
	env.background_color=[Color("#536786"),Color("#81c2ef"),Color("#dfada0")][i]
	env.fog_light_color=env.background_color
	env.ambient_light_color=[Color("#b7cee9"),Color("#eefbff"),Color("#ffddc8")][i]
	env.ambient_light_energy=.85
	sun.light_color=[Color("#ffc288"),Color("#fff1c8"),Color("#ffcead")][i]
	sun.light_energy=[1.1,1.8,1.35][i]
	get_viewport().gui_release_focus()

func can_walk(p:Vector3)->bool:
	if abs(p.x)>7.7 or p.z < -6.4 or p.z>7.2:return false
	for s in SHOPS:
		if abs(p.x-s.x)<1.95 and p.z < -1.96 and p.z > -4.95:return false
	return true

func _physics_process(dt:float)->void:
	elapsed+=dt
	var v:=Vector3.ZERO
	if not sheet.visible:
		v.x=float(Input.is_physical_key_pressed(KEY_D))-float(Input.is_physical_key_pressed(KEY_A))
		v.z=float(Input.is_physical_key_pressed(KEY_S))-float(Input.is_physical_key_pressed(KEY_W))
	v=v.normalized()
	var next:=avatar.position+v*3.8*dt
	if can_walk(Vector3(next.x,0,avatar.position.z)):avatar.position.x=next.x
	if can_walk(Vector3(avatar.position.x,0,next.z)):avatar.position.z=next.z
	if v.length_squared()>0:avatar.rotation.y=lerp_angle(avatar.rotation.y,atan2(v.x,v.z),minf(1,dt*13))
	air_speed-=14*dt
	avatar.position.y=maxf(0,avatar.position.y+air_speed*dt)
	if avatar.position.y==0:air_speed=0
	var section:=3 if elapsed<visit_until else 2 if avatar.position.y>0 else 1 if v.length_squared()>0 else 0
	var sample:=(1.0+section*24+fmod(elapsed*(38 if section==1 else 22),23.0))/24.0
	for ap in clips:
		for act in ap.get_animation_list():
			if act!="RESET":
				ap.play(act)
				ap.seek(sample,true)
		ap.pause()
	camera.position=camera.position.lerp(Vector3(avatar.position.x*.69,3.25,avatar.position.z+5.35),1-exp(-6*dt))
	camera.look_at(Vector3(avatar.position.x*.88,1.3+avatar.position.y*.28,avatar.position.z-.58))
	var name_text: String=["旅行補給攤","雙攤投資所","理財寶庫"][progress]
	var distance:=avatar.position.distance_to(SHOPS[mini(progress,1)])
	status.text="%s　｜　%d 分　｜　鑰匙 %d / 2\nWASD 移動　空白鍵跳躍　%s" % [name_text,scores[0]+scores[1],mini(2,progress+int(awarded)),("Enter 互動" if distance<2.15 or progress==2 else "距離 %d 公尺" % ceili(distance))]

func _unhandled_key_input(e:InputEvent)->void:
	if not e is InputEventKey or not e.pressed or e.echo:return
	if sheet.visible:
		if e.keycode==KEY_ESCAPE:sheet.hide()
		return
	if e.keycode==KEY_SPACE and avatar.position.y==0:air_speed=5.6
	if e.keycode==KEY_ENTER and (progress==2 or avatar.position.distance_to(SHOPS[progress])<2.15 and avatar.position.y==0):
		visit_until=elapsed+1
		show_shop()

func show_shop(message:String="")->void:
	for n in form.get_children():
		form.remove_child(n)
		n.queue_free()
	sheet.show()
	var label:=Label.new()
	form.add_child(label)
	if progress==2:
		label.text="兩把鑰匙到手！預算 %d 分（修正 %d 次），投資 %d 分（修正 %d 次）。" % [scores[0],misses[0],scores[1],misses[1]]
		add_button(form,"再玩一次",func(): get_tree().reload_current_scene())
	elif awarded:
		label.text="取得鑰匙！本關 %d / 50 分。" % scores[progress]
		add_button(form,"繼續",advance)
	else:
		label.text=["100 枚預算：今天午餐 35 枚、明天車票 25 枚，該選哪袋？","100 枚預算：先留至少 40 枚餐費，剩下分給兩攤。"][progress]+"\n"+message
		var plans:Array=[["午餐 35＋煙火 65","午餐 35＋車票 25＋貼紙 15","午餐 35＋車票 25＋雪橇 55"],["餐費 20／熱湯 40／冰果 40","餐費 40／熱湯 30／冰果 30","餐費 40／熱湯 60／冰果 0"]][progress]
		for i in range(3):add_button(form,plans[i],answer.bind(i))
	add_button(form,"返回市集",sheet.hide)

func answer(i:int)->void:
	if i!=1:
		misses[progress]+=1
		show_shop("檢查明天要用的金額，再算算總和。")
		return
	scores[progress]=maxi(30,50-5*misses[progress])
	awarded=true
	show_shop()

func advance()->void:
	progress+=1
	awarded=false
	if progress==2:show_shop()
	else:sheet.hide()
