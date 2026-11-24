"""Build the snow market and its animated flying squirrel. Run with Blender -b -P."""
import bpy as B, math as M, random, gzip, pathlib
from mathutils import Vector
from functools import lru_cache
out=pathlib.Path(__file__).resolve().parents[1]/"market3d"
rng=random.Random(74)
colors=dict(fur="#aa542c",cream="#f6deb6",tip="#613023",ink="#242124",iris="#784425",shine="#fff4ce",brass="#e5a64d",cape="#206368",stitch="#ffe2a2",scarf="#b4433c",wood="#704734",plank="#af7951",oak="#523a31",stone="#77858d",snow="#dfedf1",fir="#32655e",pine="#214a49",awning="#247779",stripe="#f4db97",glass="#ffb85d",blue="#46688c",roof="#516777",tile="#795746",ice="#96c3cf",mountain="#8099af",berry="#c54b4b",jade="#41aa93")
def reset():
 B.ops.wm.read_factory_settings(use_empty=True)
 material.cache_clear(); mesh.cache_clear()
@lru_cache(None)
def material(name):
 m=B.data.materials.new(name);s=colors[name].lstrip('#');rgb=[(int(s[i:i+2],16)/255)**2.2 for i in (0,2,4)]
 m.diffuse_color=(*rgb,1);m.use_nodes=True;p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*rgb,1);p.inputs['Roughness'].default_value=.36 if name in ('brass','iris') else .78
 if name=='brass':p.inputs['Metallic'].default_value=.48
 if name in ('glass','shine'):p.inputs['Emission Color'].default_value=(*rgb,1);p.inputs['Emission Strength'].default_value=.8
 return m
@lru_cache(None)
def mesh(kind,mat):
 if kind=='orb': B.ops.mesh.primitive_uv_sphere_add(segments=20,ring_count=12)
 elif kind=='box':B.ops.mesh.primitive_cube_add(size=2)
 elif kind=='spike':B.ops.mesh.primitive_cone_add(vertices=12,radius1=1,depth=2)
 elif kind=='disk':B.ops.mesh.primitive_cylinder_add(vertices=24,radius=1,depth=2)
 elif kind=='ring':B.ops.mesh.primitive_torus_add(major_segments=32,minor_segments=8,major_radius=.86,minor_radius=.14)
 o=B.context.object;d=o.data;d.materials.append(material(mat))
 for f in d.polygons:f.use_smooth=kind in ('orb','ring')
 B.data.objects.remove(o,do_unlink=True);return d
def node(name,loc,parent=None,data=None):
 o=B.data.objects.new(name,data);B.context.collection.objects.link(o);o.parent=parent;o.location=loc;return o
def part(kind,mat,loc,scale,parent=None,rot=(0,0,0)):
 o=node(mat,loc,parent,mesh(kind,mat));o.scale=scale;o.rotation_euler=rot;return o
def beam(a,b,r,mat,parent=None):
 a,b=Vector(a),Vector(b);o=part('disk',mat,(a+b)/2,(r,r,(b-a).length/2),parent);o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return o
def export(name,animated=False):
 B.context.scene.render.fps=24
 B.context.preferences.filepaths.save_version=0
 B.ops.wm.save_as_mainfile(filepath=str(out/(name+".blend")),compress=True)
 B.ops.export_scene.gltf(filepath=str(out/(name+'.glb')),export_format='GLB',export_animations=animated,export_animation_mode='SCENE',export_frame_range=True,export_force_sampling=True,export_cameras=False,export_lights=False)
def animal():
 reset();sc=B.context.scene;sc.frame_start=1;sc.frame_end=120
 root=node('BodyRig',(0,0,1.06));head=node('HeadRig',(0,-.13,.67),root);tail=node('PlumeRig',(0,.38,-.33),root);legs=[];arms=[]
 def orb(m,l,s,p=root,rot=(0,0,0)):return part('orb',m,l,s,p,rot)
 orb('fur',(0,0,0),(.49,.41,.69));orb('cream',(0,-.23,-.05),(.415,.24,.53))
 orb('fur',(0,0,.15),(.53,.43,.48),head)
 for sign in [-1,1]:
  x=sign;orb('cream',(x*.185,-.32,.05),(.23,.19,.18),head)
  orb('cream',(x*.37,-.14,.08),(.17,.16,.2),head)
  orb('fur',(x*.32,.025,.58),(.151,.115,.265),head,(0,x*.25,0));orb('tip',(x*.33,-.075,.59),(.085,.036,.18),head,(0,x*.25,0))
  part('spike','tip',(x*.39,.035,.84),(.085,.065,.16),head,(0,x*.24,0))
  orb('ink',(x*.252,-.346,.262),(.142,.098,.153),head)
  orb('iris',(x*.25,-.415,.262),(.101,.044,.114),head);orb('ink',(x*.24,-.448,.267),(.063,.016,.078),head);orb('shine',(x*.23-.026,-.465,.307),(.028,.012,.03),head)
  for j in range(3):beam((x*.26,-.455,.065-j*.026),(x*(.53+.027*j),-.46,.115-j*.064),.005,'tip',head)
  leg=node('HindLeg',(x*.267,0,-.46),root);legs.append(leg);orb('fur',(0,.04,-.12),(.212,.22,.30),leg);orb('tip',(0,-.12,-.38),(.157,.25,.095),leg)
  arm=node('ForePaw',(x*.39,-.035,.19),root);arms.append(arm);orb('fur',(0,-.055,-.17),(.123,.137,.254),arm);orb('tip',(0,-.12,-.34),(.105,.103,.125),arm)
 orb('tip',(0,-.485,.134),(.093,.065,.061),head)
 orb('cape',(0,0,.33),(.53,.47,.19));orb('brass',(0,-.464,.30),(.086,.035,.08));orb('cape',(0,.36,.02),(.48,.14,.49),root,(-.19,0,0))
 # Swept plume with tapered tip, curved spine and long contrasting guard hairs.
 centers=[(0,0,.0,.13),(.08,.28,.05,.22),(.16,.53,.23,.32),(.28,.67,.55,.39),(.38,.72,.88,.38),(.46,.67,1.16,.32),(.49,.53,1.39,.23),(.43,.36,1.52,.13),(.33,.24,1.54,.018)]
 vv=[];ff=[];n=24
 for x,y,z,r in centers:
  for i in range(n):
   ang=2*M.pi*i/n;vv.append((x+r*M.cos(ang),y+.76*r*M.sin(ang),z))
 for j in range(len(centers)-1):
  for i in range(n):ff.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
 d=B.data.meshes.new('Sculpted plume');d.from_pydata(vv,[],ff);d.materials.append(material('fur'));d.materials.append(material('cream'));o=node('Striped plume',(0,0,0),tail,d)
 for k,f in enumerate(d.polygons):f.use_smooth=True;f.material_index=int(k//n>=6 or k%n in (5,6))
 for style,mat in [('Night','brass'),('Day','scarf'),('Felt','stitch')]:
  g=node(style+'_costume',(0,0,0),root)
  if style=='Night':part('ring',mat,(0,-.49,.28),(.1,.1,.1),g,(M.pi/2,0,0))
  elif style=='Day':orb(mat,(-.18,.39,.16),(.13,.16,.43),g,(0,-.45,0))
  else:
   for j in range(9):orb(mat,(-.34+j*.084,.456,.03+abs(j-4)*.03),(.029,.026,.048),g)
 # Fine tapered guard hairs follow the sculpt. Dark roots and warm tips retain
 # a readable silhouette even when the player looks at the courier from behind.
 for parent,center,radii,count in [(head,(0,0,.15),(.53,.43,.48),1600),(root,(0,0,0),(.49,.41,.69),1050)]:
  verts=[];faces=[];inks=[]
  for j in range(count):
   u=rng.uniform(-1,1);a=rng.random()*M.tau;w=M.sqrt(1-u*u)
   normal=Vector((w*M.cos(a),w*M.sin(a),u))
   if normal.y<-.64 and parent==head:continue
   pt=Vector(center)+Vector(tuple(normal[k]*radii[k] for k in range(3)))
   tangent=Vector((-normal.y,normal.x,0)).normalized()*rng.uniform(.004,.009)
   down=Vector((0,.023,-.044));tip=pt+normal*.018+down
   k=len(verts);verts.extend((pt-tangent,pt+tangent,tip));faces.append((k,k+1,k+2));inks.append(j%7==0)
  d=B.data.meshes.new('Guard hair ribbons');d.from_pydata(verts,[],faces)
  d.materials.append(material('fur'));d.materials.append(material('plank'))
  for f,i in zip(d.polygons,inks):f.material_index=int(i)
  node('Fur fringes',(0,0,0),parent,d)
 # Tail fringe follows the curved plume instead of intersecting the face.
 verts=[];faces=[]
 for j in range(1250):
  t=rng.uniform(1,7.8);i=int(t);k=t-i
  x,y,z,r=[centers[i][q]*(1-k)+centers[i+1][q]*k for q in range(4)]
  a=rng.random()*M.tau;c,sn=M.cos(a),M.sin(a);p0=Vector((x+r*c,y+.76*r*sn,z));side=Vector((-sn,c,0))*.009
  n=len(verts);verts.extend((p0-side,p0+side,p0+Vector((c*.024,sn*.024,.063))));faces.append((n,n+1,n+2))
 d=B.data.meshes.new('Plume nap');d.from_pydata(verts,[],faces);d.materials.append(material('plank'));node('Plume fringe',(0,0,0),tail,d)
 for frame in range(1,121):
  section=(frame-1)//24;t=((frame-1)%24)/23;wave=M.sin(t*M.tau);lift=M.sin(t*M.pi)
  root.location.z=1.06+(.022*wave if section==0 else .058*abs(wave) if section==1 else -.10*lift if section==2 else .016*wave)
  root.keyframe_insert(data_path='location',frame=frame)
  for i,(leg,arm) in enumerate(zip(legs,arms)):
   leg.rotation_euler.x=(.64*wave*(-1)**i if section==1 else .74*lift if section==2 else 0)
   arm.rotation_euler.x=(-.60*wave*(-1)**i if section==1 else -.85*lift if section in (2,3) else .05*wave)
   for obj in [arm,leg]:obj.keyframe_insert(data_path='rotation_euler',frame=frame)
  tail.rotation_euler=(.10*wave+.15*lift*(section==2),.14*wave,0);head.rotation_euler=(.08*wave if section==3 else .022*wave,0,.07*wave)
  for obj in [tail,head]:obj.keyframe_insert(data_path='rotation_euler',frame=frame)
 for i,nm in enumerate(['Idle','Run','Jump','Visit','Rest']):sc.timeline_markers.new(nm,frame=1+i*24)
 sc.frame_set(1);export('courier',True)
def market():
 reset()
 P=part
 def box(m,x,y,z,a,b,c,p=None,rot=(0,0,0)):return P('box',m,(x,y,z),(a,b,c),p,rot)
 def orb(m,x,y,z,a,b,c,p=None):return P('orb',m,(x,y,z),(a,b,c),p)
 def cone(m,x,y,z,a,b,c,p=None):return P('spike',m,(x,y,z),(a,b,c),p)
 box('snow',0,3,-.3,36,40,.29)
 box('stone',0,1,-.024,5,10,.031)
 for row in range(22):
  for col in range(6):
   x=-4+col*1.58+(.36 if row%2 else 0);box(rng.choice(['ice','snow','ice']),x,-8+row*.8,.005,.77,.38,.024)
 for i in range(19):
  x=-40+i*4.5;y=rng.uniform(19,29);h=rng.uniform(5,13)
  cone('mountain',x,y,h/2,6.8,4.8,h/2);cone('snow',x,y,h*.775,3.18,2.23,h*.23)
 for i in range(88):
  x=rng.uniform(-31,31);y=rng.uniform(-10,22)
  if abs(x)<10 and y<12:continue
  h=rng.uniform(1.8,5)
  P('disk','wood',(x,y,.54),(.15,.15,.55))
  for j in range(3):
   z=h*(.37+j*.22);r=h*(.27-j*.059)
   cone('fir',x,y,z,r,r,h*.25);cone('snow',x,y,z+h*.08,r*.78,r*.78,h*.18)
 for j in range(7):
  x=-12+j*4;y=9+(j%2)*1.7
  box('plank',x,y,1.5,1.65,1.45,1.5)
  for k in [-1,1]:
   box('roof',x+k*.91,y,3.55,1.16,1.72,.12,rot=(0,k*.54,0))
   box('snow',x+k*.91,y,3.68,1.19,1.76,.11,rot=(0,k*.54,0))
   box('oak',x+k*1.49,y-1.46,1.5,.096,.1,1.5)
   box('glass',x+k*.94,y-1.48,1.65,.32,.03,.43);box('oak',x+k*.94,y-1.53,1.65,.035,.035,.44)
  box('oak',x,y-1.48,.96,.33,.1,.96);box('stone',x+.91,y+.52,3.97,.23,.23,.85)
 for index,x in enumerate([-3.9,3.9]):
  y=3.2
  for xx in [-1.45,1.45]:
   for yy in [-.83,.83]:beam((x+xx,y+yy,0),(x+xx,y+yy,2.72),.084,'oak')
  for k in range(8):
   box('plank',x-1.4+.4*k,y-.77,.54,.19,.10,.53)
   for side in [-1,1]:box(('awning' if index==0 else 'berry') if k%2==0 else 'stripe',x-1.49+k*.425,y+side*.55,2.98,.216,.66,.079,rot=(-side*.39,0,0))
   orb('stripe' if k%2 else 'awning',x-1.49+k*.425,y-1.13,2.64,.215,.065,.20)
  box('wood',x,y,1.1,1.62,.95,.093)
  for k in range(14):
   xx=x+rng.uniform(-1.24,1.24);yy=y+rng.uniform(-.5,.55)
   if index:orb('berry' if k%2 else 'jade',xx,yy,1.32,.148,.14,.14)
   else:orb('cream',xx,yy,1.31,.20,.13,.12)
  for side in [-1,1]:
   xx=x+side*1.42;beam((xx,y-.86,2.69),(xx,y-.86,2.37),.023,'brass');orb('glass',xx,y-.86,2.20,.155,.155,.205);cone('brass',xx,y-.86,2.42,.19,.19,.10)
 # Three independent prop sets and animated festival details.
 for tag in ['Night','Day','Felt']:
  p=node(tag+'_set',(0,0,0))
  for x in [-7,7]:
   if tag=='Night':
    for y in [-4,0,5]:
     beam((x,y,0),(x,y,2.8),.09,'oak',p);orb('glass',x,y,2.95,.27,.27,.32,p);cone('brass',x,y,3.32,.37,.37,.18,p)
   elif tag=='Day':
    beam((x,0,0),(x,0,4.5),.075,'brass',p)
    for j in range(3):box('awning' if j%2 else 'stripe',x+j*.33+.24,0,3.98,.17,.05,.42,p)
   else:
    for y in [-3,1,5]:
     orb('plank',x,y,.30,.23,.23,.38,p);orb('berry',x,y,.68,.64,.64,.31,p)
     for j in range(6):orb('cream',x+.41*M.cos(j),y+.41*M.sin(j),.89,.074,.074,.037,p)
  # The transverse strand gives the street a distinct foreground silhouette.
  for x in [-6.8,6.8]:beam((x,1.9,0),(x,1.9,5.25),.095,'wood',p)
  for j in range(16):
   x=-6.8+j*.85;z=4.35+.88*(x/6.8)**2
   beam((x,1.9,z),(x+.85,1.9,4.35+.88*((x+.85)/6.8)**2),.022,'oak',p)
   if tag=='Night' and j%2==0:
    beam((x,1.9,z),(x,1.9,z-.16),.018,'brass',p);orb('glass',x,1.9,z-.31,.115,.115,.15,p);cone('brass',x,1.9,z-.13,.14,.14,.071,p)
   elif tag=='Day':
    cone('awning' if j%2 else 'stripe',x,1.9,z-.21,.25,.05,.24,p).rotation_euler.x=M.pi
   elif tag=='Felt':orb('berry' if j%2 else 'cream',x,1.9,z-.16,.12,.12,.14,p)
  rotor=node('Spinner_'+tag,(0,7.2,4.4),p);beam((0,7.2,0),(0,7.2,4.42),.24,'wood',p)
  for j in range(4):
   a=j*M.pi/2;beam((0,0,0),(1.55*M.sin(a),0,1.55*M.cos(a)),.053,'brass',rotor)
   box('stripe' if tag!='Felt' else 'plank',.99*M.sin(a),0,.99*M.cos(a),.17,.04,.54,rotor,(0,a,0))
  for f,a in [(1,0),(97,2*M.pi)]:rotor.rotation_euler.y=a;rotor.keyframe_insert(data_path='rotation_euler',frame=f)
 B.context.scene.frame_end=97;B.context.scene.frame_set(1);export('village',True)
animal();market()
