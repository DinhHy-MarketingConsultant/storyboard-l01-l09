// Local SVG motion preview. Six-second simulated timeline, independent from karaoke.
(()=>{
const NS='http://www.w3.org/2000/svg',DURATION=6000;
let enabled=false,running=false,clock=0,last=0,registry=[],serial=0,speed=1;
const notes={
 L01:'Caption nhẹ; dùng nút karaoke để xem từ active phóng lên.',
 L02:'Headline bay lên theo cụm → box quét ngang → keyword bật nhẹ. Giữ câu rồi thoát.',
 L03:'Các cụm chữ xuất hiện theo đường đọc: trái → phải → dưới; đường nối vẽ sau cụm đầu.',
 L04:'Chữ gõ hoặc trượt nhẹ → swash vẽ theo hướng nét → illustration vẽ lần lượt. Không di chuyển source.',
 L05:'Điểm neo bật trước → đường callout vẽ từ vật thể tới nhãn → nhãn gõ ra.',
 L06:'Các vùng crop của cùng source trượt vào → headline xuất hiện theo vùng. Source không đổi.',
 L07:'Chữ phía sau bay vào dưới mask người → chữ phía trước xuất hiện → swash vẽ sau cùng.',
 L08:'Chữ đi từ xa tới gần, giữ góc nghiêng của từng lớp → đường phối cảnh vẽ ra.',
 L09:'Đầu vào hiện trước → đường nối vẽ → khoản chi hiện tiếp → kết quả bật sau cùng.'
};
const css=document.createElement('style');css.textContent='.stage>.guide{display:none}.show-guides .stage>.guide{display:block}.motion-tools{margin:0 4vw 25px;padding:16px 20px;border:1px solid #b4b8aa;border-radius:6px}.motion-controls{display:flex;align-items:center;gap:15px;flex-wrap:wrap}.motion-controls button{padding:10px 14px;background:#25392c;color:white;border:0;border-radius:4px;cursor:pointer}.motion-controls input[type=range]{width:230px;max-width:65vw}.motion-note{font-size:14px;margin:10px 0 0}.motion-caption{font-size:12px!important;color:#826237}.motion-detail-stage{position:relative;aspect-ratio:9/16;max-height:82vh;background:#333;overflow:hidden}.motion-detail-stage svg{height:100%;width:100%;display:block}.motion-controls select{padding:8px}.motion-detail-stage .guide{display:none!important}';document.head.append(css);
const panel=document.createElement('section');panel.className='motion-tools';panel.innerHTML='<div class="motion-controls"><button id="layout-motion">Bật motion layout</button><button id="motion-pause" disabled>Tạm dừng</button><button id="motion-replay" disabled>Phát lại</button><label>Thời gian <input id="motion-seek" type="range" min="0" max="6" step="0.01" value="0"></label><output id="motion-time">0.00 / 6.00s</output><label>Tốc độ <select id="motion-speed"><option value="0.5">0.5×</option><option value="1" selected>1×</option><option value="1.5">1.5×</option></select></label><label><input id="motion-loop" type="checkbox" checked> Lặp</label></div><p id="motion-note" class="motion-note"></p><p class="small">Motion layout chạy các frame nhấn 1 / 3 / 5. Frame karaoke giữ nút điều khiển riêng. Mỗi frame demo 6 giây, chưa căn VO thật; chưa phải tracking trên video.</p>';document.querySelector('.toolbar').after(panel);
const $=s=>document.querySelector(s);
function tween(el,from,to,start,dur,exit=true,ease='cubic-bezier(.22,.72,.2,1)'){
 const a=Math.max(.001,start/DURATION),b=Math.min(.88,(start+dur)/DURATION);
 const keys=[{...from,offset:0},{...from,offset:a,easing:ease},{...to,offset:b},{...to,offset:.89}];
 if(exit)keys.push({...to,opacity:0,offset:1});else keys.push({...to,offset:1});
 let animation=el.animate(keys,{duration:DURATION,fill:'both'});animation.pause();animation.currentTime=enabled?clock:DURATION*.7;registry.push(animation);
}
function wrap(el){const w=document.createElementNS(NS,'g');el.before(w);w.append(el);w.style.transformBox='view-box';return w;}
function fly(el,dx,dy,start=0,dur=550,scale=1){let b;try{b=el.getBBox()}catch{}const w=wrap(el);if(b)w.style.transformOrigin=(b.x+b.width/2)+'px '+(b.y+b.height/2)+'px';tween(w,{opacity:0,transform:`translate(${dx}px,${dy}px) scale(${scale})`},{opacity:1,transform:'translate(0px,0px) scale(1)'},start,dur);}
function type(el,start=200){const text=el.textContent;const chars=Array.from(text);el.textContent='';chars.forEach((ch,n)=>{const t=document.createElementNS(NS,'tspan');t.textContent=ch;el.append(t);tween(t,{opacity:0},{opacity:1},start+n*40,1,true,'steps(1,end)');});}
function draw(el,start=0,dur=900,reverse=false){let len;try{len=el.getTotalLength()}catch{return}if(!len)return;el.style.strokeDasharray=len+' '+len;tween(el,{strokeDashoffset:reverse?-len:len,opacity:1},{strokeDashoffset:0,opacity:1},start,dur);}
function box(el,start=350,vertical=false){const b=el.getBBox(),w=wrap(el);w.style.transformOrigin=b.x+'px '+(b.y+b.height)+'px';tween(w,{opacity:1,transform:vertical?'scale(1,0)':'scale(0,1)'},{opacity:1,transform:'scale(1,1)'},start,450);}
function build(svg,f){if(!svg||svg.dataset.motionReady||f.type==='karaoke')return;svg.dataset.motionReady='1';
 const texts=[...svg.children].filter(e=>e.tagName.toLowerCase()==='text');
 const shapes=[...svg.children].filter(e=>['path','polyline','ellipse'].includes(e.tagName.toLowerCase()));
 const rects=[...svg.children].filter(e=>e.tagName.toLowerCase()==='rect'&&!e.hasAttribute('opacity'));
 const L=f.layout,n=f.frame;
 if(L==='L02'){
  texts.forEach((t,i)=>fly(t,0,i===0?20:120,100+i*180,500,i===texts.length-1?.82:1));rects.forEach(r=>box(r,650,n===5));
 }else if(L==='L03'){
  texts.forEach((t,i)=>fly(t,i%2===0?-110:110,i>2?55:0,180+i*320,650));shapes.forEach((s,i)=>draw(s,650+i*270,850));
 }else if(L==='L04'){
  texts.forEach((t,i)=>i===0?type(t,120):fly(t,i%2?70:-70,i===1?45:0,300+i*300,750));shapes.forEach((s,i)=>draw(s,800+i*110,900,i%3===1));
 }else if(L==='L05'){
  shapes.forEach((s,i)=>s.tagName.toLowerCase()==='ellipse'?fly(s,0,0,200+i*100,250,.2):draw(s,450+i*140,700));texts.forEach((t,i)=>type(t,i===0?150:1050+i*220));
 }else if(L==='L06'){
  const images=[...svg.children].filter(e=>e.tagName.toLowerCase()==='image').slice(1);images.forEach((im,i)=>fly(im,n===3?0:(i%2?-1080:1080),n===3?(i%2?1920:-1920):0,i*220,900));texts.forEach((t,i)=>fly(t,0,100,850+i*240,650));shapes.forEach(s=>draw(s,1100,700));
 }else if(L==='L07'){
  texts.forEach((t,i)=>{if(n===5&&i<13)fly(t,0,-70,180+i*75,650);else fly(t,i%2?100:-100,50,180+i*300,850);});shapes.forEach((s,i)=>draw(s,1650+i*100,900));
 }else if(L==='L08'){
  texts.forEach((t,i)=>fly(t,(i%2?1:-1)*100,-80,220+i*400,950,.45));shapes.forEach((s,i)=>draw(s,900+i*250,950));
 }else if(L==='L09'){
  texts.forEach((t,i)=>{const final=i>=texts.length-2;fly(t,0,final?55:25,final?2800+(i-texts.length+2)*180:180+i*210,final?600:400,final?.8:1);});shapes.forEach((s,i)=>draw(s,950+i*140,800));
 }
}
function updateNotes(){const id=$('#nav .selected')?.dataset.id||'L01';$('#motion-note').textContent=notes[id];}
function cancel(){registry.forEach(a=>a.cancel());registry=[];}
function prepare(){cancel();clock=0;document.querySelectorAll('#grid .card').forEach(card=>{const id=card.dataset.key,f=frames.find(f=>f.id===id);build(card.querySelector('svg.art'),f);if(f.type!=='karaoke'){const p=document.createElement('p');p.className='motion-caption';p.textContent='Motion: '+notes[f.layout];card.append(p);}});updateNotes();apply();}
function apply(){registry.forEach(a=>a.currentTime=clock);$('#motion-seek').value=clock/1000;$('#motion-time').textContent=(clock/1000).toFixed(2)+' / 6.00s';}
function restore(){registry.forEach(a=>a.currentTime=5320);}
function buttons(){const b=$('#layout-motion');b.textContent=enabled?'Tắt motion layout':'Bật motion layout';b.setAttribute('aria-pressed',String(enabled));$('#motion-pause').disabled=!enabled;$('#motion-replay').disabled=!enabled;$('#motion-pause').textContent=running?'Tạm dừng':'Tiếp tục';}
$('#layout-motion').onclick=()=>{enabled=!enabled;running=enabled;clock=0;last=0;buttons();enabled?apply():restore();};
$('#motion-pause').onclick=()=>{running=!running;last=0;buttons();};
$('#motion-replay').onclick=()=>{enabled=true;running=true;clock=0;last=0;buttons();apply();};
$('#motion-seek').oninput=e=>{enabled=true;running=false;clock=Number(e.target.value)*1000;last=0;buttons();apply();};
$('#motion-speed').onchange=e=>{speed=Number(e.target.value)};
function tick(t){if(enabled&&running){if(last)clock+=(t-last)*speed;if(clock>DURATION){if($('#motion-loop').checked)clock=clock%DURATION;else{clock=DURATION;running=false;buttons();}}apply();}last=t;requestAnimationFrame(tick);}requestAnimationFrame(tick);
const originalChoose=choose;choose=function(id){originalChoose(id);prepare();buttons();if(!enabled)restore();};
const originalDetail=detail;detail=function(id){originalDetail(id);const f=frames.find(f=>f.id===id);if(f.type==='karaoke')return;const img=$('#detailBody img'),stage=document.createElement('div');stage.className='motion-detail-stage';stage.innerHTML=svgs[id];img.replaceWith(stage);const svg=stage.querySelector('svg');[...svg.querySelectorAll('[id]')].forEach(el=>{const old=el.id,newid=old+'_modal_'+serial;el.id=newid;svg.querySelectorAll('[clip-path]').forEach(e=>{if(e.getAttribute('clip-path')==='url(#'+old+')')e.setAttribute('clip-path','url(#'+newid+')');});});serial++;build(svg,f);const p=document.createElement('p');p.className='motion-note';p.textContent=notes[f.layout];$('#detailBody aside').append(p);const b=document.createElement('button');b.textContent='Phát lại motion frame này';b.onclick=()=>{$('#motion-replay').click()};$('#detailBody aside').append(b);enabled?apply():restore();};
document.fonts.ready.then(()=>{prepare();restore();});
})();
