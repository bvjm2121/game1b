"use strict";
const $=id=>document.getElementById(id), T=THREE;
const styles={
 Night:{sky:0x354e72,horizon:0xafb8ce,fog:0x71859a,sun:0xffc783,light:2.1,hemi:0xc1dcff,ground:0x6c5660,coat:0x186563,fur:0xb96c42,snow:0xafc3da},
 Day:{sky:0x448bc6,horizon:0xe8f6fb,fog:0xbad9e6,sun:0xffe6b0,light:2.55,hemi:0xdbf8ff,ground:0x8298a0,coat:0x247893,fur:0xe29147,snow:0xe8f5f7},
 Felt:{sky:0xc694a0,horizon:0xffdfb9,fog:0xd7bcb5,sun:0xffca96,light:2.15,hemi:0xffefd2,ground:0x99808d,coat:0x639087,fur:0xc48965,snow:0xf1dfe0}
};
const stalls=[{x:-3.9,z:-1.58,name:'旅行補給攤'},{x:3.9,z:-1.58,name:'雙攤投資所'}];
const keys=new Set(), points=[0,0],miss=[0,0],allocation=[0,0,0];
let style='Night',stage=0,passed=false,bag=null,ready=false,near=false,grounded=true,height=0,velocity=0,time=0,phase=0,anim='idle',visitTime=0;
let renderer,scene,camera,sky,sun,hemi,hero,village,clock,worldMixer,heroMixer,shadow,tag;
const lamps=[],actors=[],materials=new Set(),ornaments=[];
const player=new T.Group(), aim=new T.Vector3(), placard=new T.Vector3();
const modal=$('shop'), world=$('world');
function cloth(){const c=document.createElement('canvas');c.width=c.height=64;const g=c.getContext('2d');g.fillStyle='#fff';g.fillRect(0,0,64,64);for(let i=0;i<64;i+=4){g.fillStyle='#dad7d1';g.fillRect(i,0,1,64);g.fillStyle='#e5e2de';g.fillRect(0,i,64,1)}const t=new T.CanvasTexture(c);t.wrapS=t.wrapT=T.RepeatWrapping;t.repeat.set(9,9);return t}
let weave;
function decorate(obj){obj.traverse(n=>{if(/^(Night|Day|Felt)_/.test(n.name))ornaments.push(n);if(!n.isMesh)return;n.castShadow=true;n.receiveShadow=true;materials.add(n.material);if(!n.material.userData.base)n.material.userData.base=n.material.color.clone()})}
// Batch static scenery while retaining each style branch and moving mill.
function batch(root){
 root.updateWorldMatrix(true,true);
 const holders=[root,...ornaments.filter(n=>n.name.endsWith('_set'))];
 for(const holder of holders){let groups=new Map();const inverse=holder.matrixWorld.clone().invert();
  for(const n of [...holder.children]){if(!n.isMesh)continue;const key=n.geometry.uuid+n.material.uuid;if(!groups.has(key))groups.set(key,[]);groups.get(key).push(n)}
  for(const group of groups.values()){if(group.length<3)continue;const first=group[0],inst=new T.InstancedMesh(first.geometry,first.material,group.length);group.forEach((n,i)=>{inst.setMatrixAt(i,new T.Matrix4().multiplyMatrices(inverse,n.matrixWorld));holder.remove(n)});inst.castShadow=true;inst.receiveShadow=true;inst.frustumCulled=false;holder.add(inst)}
 }
}
function setStyle(next){style=next;document.querySelectorAll('[data-skin]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.skin===next)));if(!ready)return;
 const p=styles[next];scene.fog.color.setHex(p.fog);sky.material.uniforms.top.value.setHex(p.sky);sky.material.uniforms.low.value.setHex(p.horizon);sun.color.setHex(p.sun);sun.intensity=p.light;hemi.color.setHex(p.hemi);hemi.groundColor.setHex(p.ground);hemi.intensity=next==='Night'?1.05:1.4;sun.position.set(next==='Day'?-9:6,12,7);
 lamps.forEach(l=>l.intensity=next==='Night'?1.7:next==='Felt'?.55:.12);ornaments.forEach(n=>n.visible=n.name.startsWith(next+'_'));materials.forEach(m=>{m.color.copy(m.userData.base);const override={fur:p.fur,cape:p.coat,snow:p.snow}[m.name];if(override)m.color.setHex(override);m.map=next==='Felt'&&!['brass','glass','iris','ink','shine'].includes(m.name)?weave:null;m.needsUpdate=true});world.focus({preventScroll:true})
}
document.querySelectorAll('[data-skin]').forEach(b=>b.onclick=()=>setStyle(b.dataset.skin));
function mixCharacter(obj,clips){const m=new T.AnimationMixer(obj);clips.forEach(clip=>m.clipAction(clip).play());return m}
async function enterWorld(){
 renderer=new T.WebGLRenderer({canvas:world,antialias:true,alpha:false});renderer.setPixelRatio(Math.min(devicePixelRatio,1.65));renderer.outputEncoding=T.sRGBEncoding;renderer.shadowMap.enabled=true;renderer.shadowMap.type=T.PCFSoftShadowMap;renderer.toneMapping=T.ACESFilmicToneMapping;renderer.toneMappingExposure=1.03;
 scene=new T.Scene();scene.fog=new T.FogExp2(0xaabbbb,.037);camera=new T.PerspectiveCamera(46,1,.09,130);
 sky=new T.Mesh(new T.SphereGeometry(88,32,16),new T.ShaderMaterial({side:T.BackSide,depthWrite:false,uniforms:{top:{value:new T.Color()},low:{value:new T.Color()}},vertexShader:'varying float h;void main(){h=position.y/88.;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}',fragmentShader:'uniform vec3 top,low;varying float h;void main(){gl_FragColor=vec4(mix(low,top,smoothstep(-0.08,.58,h)),1.);}'}));scene.add(sky);
 hemi=new T.HemisphereLight();sun=new T.DirectionalLight();sun.castShadow=true;sun.shadow.mapSize.set(1024,1024);Object.assign(sun.shadow.camera,{left:-14,right:14,top:15,bottom:-14,far:48});sun.shadow.camera.updateProjectionMatrix();sun.shadow.normalBias=.035;scene.add(hemi,sun);weave=cloth();
 for(const target of stalls){const lamp=new T.PointLight(0xffb45b,1.7,7,2);lamp.position.set(target.x,2.45,-1.64);lamps.push(lamp);scene.add(lamp)}
 const loader=new T.GLTFLoader(),[v,c]=await Promise.all(['village','courier'].map(n=>loader.loadAsync(n+'.glb')));
 village=v.scene;decorate(village);batch(village);scene.add(village);worldMixer=mixCharacter(village,v.animations);
 hero=c.scene;decorate(hero);player.add(hero);scene.add(player);player.position.set(0,0,3.35);heroMixer=mixCharacter(hero,c.animations);
 for(let i=0;i<2;i++){const vendor=c.scene.clone();vendor.scale.setScalar(.83);vendor.position.set(stalls[i].x,0,-4.45);scene.add(vendor);decorate(vendor);actors.push(mixCharacter(vendor,c.animations))}
 const cv=document.createElement('canvas');cv.width=cv.height=64;const ctx=cv.getContext('2d'),gr=ctx.createRadialGradient(32,32,1,32,32,32);gr.addColorStop(0,'rgba(22,32,43,.56)');gr.addColorStop(1,'rgba(22,32,43,0)');ctx.fillStyle=gr;ctx.fillRect(0,0,64,64);
 shadow=new T.Mesh(new T.PlaneGeometry(1.65,1.14),new T.MeshBasicMaterial({map:new T.CanvasTexture(cv),transparent:true,depthWrite:false}));shadow.rotation.x=-Math.PI/2;scene.add(shadow);
 tag=new T.Mesh(new T.TorusGeometry(.59,.04,8,40),new T.MeshStandardMaterial({color:0xffc968,emissive:0x805720}));tag.rotation.x=Math.PI/2;scene.add(tag);
 ready=true;setStyle(style);$('loading').hidden=true;clock=new T.Clock();camera.position.set(0,3.7,8.5);new ResizeObserver(resize).observe(world);resize();renderer.setAnimationLoop(frame);
}
function resize(){const w=world.clientWidth,h=world.clientHeight;renderer.setSize(w,h,false);camera.aspect=w/h;camera.updateProjectionMatrix()}
function openArea(x,z){return Math.abs(x)<7.7&&z<7.2&&z>-6.4&&!stalls.some(s=>Math.abs(x-s.x)<1.95&&z<-1.96&&z>-4.95)}
function jump(){if(!ready||!grounded||modal.open)return;grounded=false;velocity=5.6}
function frame(){const dt=Math.min(clock.getDelta(),.05);time+=dt;const active=!modal.open;
 let dx=active?(+keys.has('KeyD')-keys.has('KeyA')):0,dz=active?(+keys.has('KeyS')-keys.has('KeyW')):0;const magnitude=Math.hypot(dx,dz);
 if(magnitude){dx/=magnitude;dz/=magnitude;const nx=player.position.x+dx*3.8*dt,nz=player.position.z+dz*3.8*dt;if(openArea(nx,player.position.z))player.position.x=nx;if(openArea(player.position.x,nz))player.position.z=nz;const target=Math.atan2(dx,dz);player.rotation.y+=Math.atan2(Math.sin(target-player.rotation.y),Math.cos(target-player.rotation.y))*Math.min(1,13*dt)}
 if(!grounded){velocity-=14*dt;height+=velocity*dt;if(height<=0){height=0;velocity=0;grounded=true}}
 player.position.y=height+.035;shadow.position.set(player.position.x,.045,player.position.z);shadow.scale.setScalar(1-.26*height);worldMixer.update(dt);actors.forEach((m,i)=>m.setTime(((modal.open&&i===stage?73:1)+23*((time*.6+i*.45)%1))/24));
 const now=visitTime>time?'visit':!grounded?'jump':magnitude?'walk':'idle';if(now!==anim){phase=0;anim=now}phase+=dt;const fr={idle:1,walk:25,jump:49,visit:73}[now];heroMixer.setTime((fr+23*(now==='jump'?Math.min(phase/.8,.99):(phase*(now==='walk'?1.65:.85))%1))/24);
 const s=stalls[Math.min(stage,1)],dist=Math.hypot(player.position.x-s.x,player.position.z-s.z);near=dist<2.15&&grounded;tag.position.set(s.x,.06,s.z);tag.visible=stage<2;
 const desired=new T.Vector3(player.position.x*.69,3.05+Math.min(1,Math.max(0,-player.position.z*.16)),player.position.z+5.35);const visiting=modal.open&&stage<2;
 if(visiting)desired.set(s.x+.75,2.02,-.12);
 camera.position.lerp(desired,1-Math.exp(-dt*(visiting?3.5:6)));
 const look=visiting?new T.Vector3(s.x-(world.clientWidth>780?.85:0),1.34,-4.45):new T.Vector3(player.position.x*.88,1.28+height*.28,player.position.z-.58);
 aim.lerp(look,1-Math.exp(-dt*8));camera.lookAt(aim);camera.updateMatrixWorld();
 placard.set(s.x,3.45,-3.12).project(camera);const marker=$('marker');marker.hidden=modal.open||stage===2||Math.abs(placard.x)>.89||Math.abs(placard.y)>.88||placard.z>1;marker.style.left=((placard.x+1)*50)+'%';marker.style.top=((1-placard.y)*50)+'%';marker.style.transform='translate(-50%,-50%)';marker.textContent='◆　'+s.name;
 $('distance').textContent=stage===2?'兩把鑰匙已集齊':near?'抵達攤前，按 Enter 造訪':(s.x<player.position.x-.6?'往左':s.x>player.position.x+.6?'往右':'')+(s.z<player.position.z-.6?'前方':s.z>player.position.z+.6?'後方':'')+'　·　'+Math.ceil(dist)+' 公尺';$('visit').disabled=!ready||(!near&&stage!==2);$('visit').textContent=stage===2?'Enter　查看成果':'Enter　造訪攤位';
 renderer.render(scene,camera)
}
function clearKeys(){keys.clear()}window.addEventListener('blur',clearKeys);document.addEventListener('visibilitychange',clearKeys);
const controls=['KeyW','KeyA','KeyS','KeyD','Space','Enter'];window.addEventListener('keydown',e=>{if(modal.open||!controls.includes(e.code)||e.altKey||e.metaKey||e.ctrlKey)return;if((e.code==='Enter'||e.code==='Space')&&e.target.matches('button'))return;e.preventDefault();if(e.code==='Space'){if(!e.repeat)jump()}else if(e.code==='Enter'){if(!e.repeat)visit()}else keys.add(e.code)});window.addEventListener('keyup',e=>keys.delete(e.code));world.onpointerdown=()=>world.focus();
document.querySelectorAll('[data-code]').forEach(b=>{b.onpointerdown=e=>{e.preventDefault();b.setPointerCapture(e.pointerId);if(b.dataset.code==='Space')jump();else keys.add(b.dataset.code)};b.onlostpointercapture=()=>keys.delete(b.dataset.code)});
$('visit').onclick=visit;$('leave').onclick=()=>modal.close();modal.onclose=()=>{clearKeys();world.focus()};
function visit(){if(!ready||modal.open||(!near&&stage!==2))return;clearKeys();visitTime=time+1;player.rotation.y=Math.PI;paintShop();modal.showModal()}
function paintShop(){const end=stage===2;$('shopname').textContent=end?'學習手記':stalls[stage].name;$('question').textContent=end?'兩把鑰匙到手了！':stage?'替兩家攤位備貨':'哪一袋能安心出發？';$('story').textContent=end?['預算','投資分配'].map((n,i)=>n+' '+points[i]+' / 50 分，'+(miss[i]?'修正 '+miss[i]+' 次':'第一次答對')).join('。')+'。':stage?'共有 100 枚金幣，明天的餐費至少要 40 枚。留下餐費後，讓熱湯攤和冰果攤都分到投資金。即使分散，兩攤也可能一起虧錢。':'你有 100 枚金幣。今天要買 35 元午餐，明天的車票要留 25 元。挑一個兩天都夠用的錢袋。';
 const answers=$('answers');answers.replaceChildren();$('feedback').textContent='';
 if(!end&&!passed){if(!stage){['午餐 35 ＋ 煙火 65','午餐 35 ＋ 車票 25 ＋ 貼紙 15','午餐 35 ＋ 車票 25 ＋ 雪橇 55'].forEach((s,i)=>{const l=document.createElement('label');l.className='choice';const r=document.createElement('input');r.type='radio';r.name='bag';r.checked=bag===i;r.onchange=()=>bag=i;l.append(r,' '+s);answers.append(l)})}else{['餐費袋','熱湯攤','冰果攤'].forEach((s,i)=>{const l=document.createElement('label');l.className='range';const r=document.createElement('input'),o=document.createElement('output');r.type='range';r.min=0;r.max=100;r.step=10;r.value=allocation[i];o.textContent=r.value;r.oninput=()=>{allocation[i]=+r.value;o.textContent=r.value;showTotal()};l.append(s,r,o);answers.append(l)});showTotal()}}
 if(passed&&!end){const img=new Image(68,68);img.src='../art-review/quest-key.png';img.alt='獲得黃銅鑰匙';answers.append(img);$('feedback').textContent='取得鑰匙！本關 '+points[stage]+' / 50 分。'}
 $('confirm').textContent=end?'重新挑戰':passed?(stage?'開啟寶庫':'去找雙攤投資所'):'確認我的安排';
}
function showTotal(){$('feedback').textContent='已安排 '+allocation.reduce((a,b)=>a+b,0)+' / 100 枚'}
$('confirm').onclick=()=>{if(stage===2){location.reload();return}if(passed){passed=false;stage++;$('chapter').textContent=stage===1?'第二關　／　市集投資':'闖關成果';$('objective').textContent=stage===1?'尋找雙攤投資所':'雪市集寶庫已開啟';if(stage===2)paintShop();else modal.close();return}
 let message='';if(!stage){if(bag===null){$('feedback').textContent='先選一個錢袋。';return}message=['留給明天的車票錢還夠嗎？','','一共 115 枚，比預算多了 15 枚。'][bag]}else if(allocation.reduce((a,b)=>a+b,0)!==100)message='請剛好分完 100 枚。';else if(allocation[0]<40)message='明天的餐費至少要 40 枚。';else if(Math.min(allocation[1],allocation[2])===0)message='兩家攤位都要分到投資金。';
 if(message){miss[stage]++;$('feedback').textContent=message;return}passed=true;points[stage]=Math.max(30,50-5*miss[stage]);$('score').textContent=points.reduce((a,b)=>a+b)+' 分　·　鑰匙 '+(stage+1)+' / 2';paintShop()};
enterWorld().catch(error=>{console.error(error);$('loading').textContent='3D 市集未能載入。請確認瀏覽器已開啟 WebGL，然後重新整理。'});
