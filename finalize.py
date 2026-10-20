import build as B
from pathlib import Path
import io,json,html,base64,re,zipfile,math
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.utils import ImageReader
import pypdfium2 as pdfium
from PIL import Image,ImageDraw,ImageFont
P=B.P;D=json.loads((P/'storyboard_specs.json').read_text());FR=D['frames'];M=B.META;W,H=1800,1300
C=canvas.Canvas(str(P/'Storyboard_L01_L09_45_Frames.pdf'),pagesize=(W,H));PAGE=0;PAGEBOUNDS=[]
C.setTitle('9 hệ layout - 45 frame storyboard');C.setAuthor('Video Editing Brand Guidelines / DINH HY')
def text(x,y,s,size=23,font='sans',col=B.INK):
 C.setFillColor(col);C.setFont(font,size);C.drawString(x,H-y,s)
 PAGEBOUNDS.append((PAGE,x,y,s,pdfmetrics.stringWidth(s,font,size),size))
def wrap(x,y,s,w,size=22,font='sans',col=B.INK,leading=None):
 leading=leading or size*1.38;line=''
 for word in s.split():
  t=(line+' '+word).strip()
  if pdfmetrics.stringWidth(t,font,size)>w and line:text(x,y,line,size,font,col);y+=leading;line=word
  else:line=t
 if line:text(x,y,line,size,font,col);y+=leading
 return y

def start(label,title,sub):
 global PAGE
 PAGE+=1;C.setFillColor(B.PAPER);C.rect(0,0,W,H,fill=1,stroke=0);text(45,58,label,21,'bold','#916A3C');text(45,127,title,47,'news');text(45,180,sub,21,'sans',B.GRAY);text(45,1260,'L01–L09 / 1080 × 1920 / cùng source trong mỗi mẫu / overlay chỉnh sửa được / timing VO là đề xuất',17,'sans',B.GRAY);text(1690,1260,f'{PAGE:02}',20,'mono',B.GRAY)
def pic(key,x,y,w,h):C.drawImage(ImageReader(str(P/'frames'/f'{key}.jpg')),x,H-y-h,w,h)
def frame(c,i,j,x,y,w,h):
 c.saveState();c.translate(x,H-y-h);c.scale(w/1080,h/1920);q=c.beginPath();q.rect(0,0,1080,1920);c.clipPath(q,stroke=0,fill=0);B.draw(c,i,j);c.restoreState()
def params(row):
 words=[l for l in row['layers'] if l['type']=='karaoke_word']
 if words:return f"Be Vietnam Pro Bold / {words[0]['base_size_px']}px / trắng + viền đen ngoài 2px / active 113%. Điểm neo đầu dòng y={words[0]['baseline_y']}px."
 ts=[l for l in row['layers'] if l['type']=='text'];res=[]
 for t in ts[:3]:res.append(f"{t['text'][:21]}: {t['font']} {t['size_px']}px, ({round(t['baseline'][0])},{round(t['baseline'][1])})")
 return '; '.join(res)+'. Tọa độ đầy đủ trong storyboard_specs.json.'
def bodyblock(x,y,label,s,w=320,size=20):
 text(x,y,label,17,'bold','#916A3C');return wrap(x,y+31,s,w,size)+24

# 01 / cover
start('STORYBOARD / BẢN TRIỂN KHAI','9 hệ layout. 45 cách đặt overlay.','3 cấp độ / 5 frame mỗi mẫu / nhấn A - karaoke - nhấn B - karaoke - nhấn C')
text(50,300,'Thiết kế cho editor nhìn và dựng lại.',57,'news')
wrap(50,370,'Font, màu và hình minh họa tạo nhận diện trong từng mẫu. Các frame nhấn thay đổi cách tổ chức lớp edit; source gốc không đổi. Hai frame karaoke tạo khoảng nghỉ và giữ cùng điểm neo.',1620,26)
for j,key in enumerate(['L01_F02','L02_F01','L04_F03','L07_F01','L09_F05']):
 x=50+j*350;pic(key,x,510,310,551);text(x,1105,key.replace('_',' / '),23,'bold')
text(50,1185,'Bản hướng dẫn và phác thảo tĩnh; có demo karaoke. Chưa có audio thu thật hoặc project dựng native.',21,'sans',B.GRAY);C.showPage()
# 02 / rules
start('QUY TẮC ĐÃ CHỐT','Giữ chất sáng tạo, giữ chữ dễ đọc.','Guide rộng là vùng tham chiếu nội bộ, không phải safe zone chính thức dùng chung cho mọi nền tảng.')
frame(C,4,1,45,245,430,764)
C.setStrokeColor('#7FD9AC');C.setLineWidth(2);C.rect(45+60*430/1080,H-245-1540*764/1920,900*430/1080,1360*764/1920,stroke=1,fill=0)
y=270
rules=[('01 / KHÔNG GIAN','Source full 1080×1920. Vùng sáng tạo khởi điểm x60–960, y180–1540; kiểm tra UI tại nơi đăng trước xuất.'),('02 / CAPTION','Preset chính: căn giữa x520, baseline y1240 và y1328; cỡ 62px. Frame 2/4 cùng mẫu giữ cùng điểm neo.'),('03 / KARAOKE','Chữ trắng, viền đen mỏng ngoài 2px. Đọc đến từ nào, từ đó phóng 100% > 113% > 100%; không đẩy dòng.'),('04 / MÀU ACTIVE','Cấp 1 giữ trắng. Cấp 2–3 dùng màu nhấn của mẫu cho từ đang đọc, vẫn viền đen.'),('05 / NHỊP','A - karaoke - B - karaoke - C. L01 dùng caption suốt đoạn. 5 frame là mốc minh họa, không ép 3s/frame.'),('06 / BẢN DỰNG THẬT','Căn VO thật; thay source rồi kiểm tra mặt, tay, UI. L05 track điểm, L07 roto, L08 kiểm tra phối cảnh/camera.')]
for title,body in rules:
 text(545,y,title,22,'bold','#916A3C');y=wrap(545,y+42,body,1180,25)+34
text(45,1090,'Trong PDF: x/y tính từ góc trên trái; text dùng baseline. Viền, dấu Việt và swash cần tính vào vùng hiển thị.',21,'sans',B.GRAY)
text(45,1150,'C01/C03 cũ: giữ hướng mở đầu ở L07/L08. L06 dùng các crop từ cùng ảnh gốc để minh họa chia vùng.',21,'sans',B.GRAY);C.showPage()
# 03 / index
start('BẢN ĐỒ THƯ VIỆN','Chọn cơ chế trước, chọn phong cách sau.','Nhấp vào tên mẫu trong PDF để tới storyboard. Màu/font/illustration là biến thể trong mỗi hệ.')
for i,m in enumerate(M):
 row=i//3;col=i%3;x=45+col*585;y=265+row*300;pic(m[0]+'_F01',x,y,135,240);xx=x+160;text(xx,y+30,m[0]+f' / CẤP {m[1]}',20,'bold','#916A3C');yy=wrap(xx,y+80,m[2],370,27,'bold');wrap(xx,yy+10,m[6],370,22,col=B.GRAY);C.linkRect('',m[0],(x,H-y-250,x+540,H-y),relative=0,thickness=0)
C.showPage()
# 9 × 3 pages
for i,m in enumerate(M):
 code,level,name,bg,col,fonts,principle,structure=m
 start(code+f' / CẤP {level} / TỔNG QUAN',name,fonts+' / accent '+col+' / cùng một source ở cả 5 frame')
 C.bookmarkPage(code);C.addOutlineEntry(code+' / '+name,code,level=0,closed=False)
 for j in range(5):
  row=FR[i*5+j];x=45+j*350;text(x,240,f'FRAME {j+1:02} / '+('KARAOKE' if row['type']=='karaoke' else 'NHẤN'),20,'bold');frame(C,i,j,x,270,310,551)
  yy=wrap(x,865,row['title'],310,24,'bold');yy=wrap(x,yy+12,'“'+row['vo_proposed']+'”',310,20,col=B.GRAY)
  # Description shortened only for overview; full notes follow on two detail pages.
  if yy<1090:wrap(x,yy+16,('Caption nhẹ, cùng guideline.' if row['type']=='karaoke' else row['description']),310,18,col=B.GRAY)
 wrap(45,1195,structure,1640,21,'bold');C.showPage()
 start(code+' / CHI TIẾT 01 & 03','Hai bố cục nhấn khác nhau.',principle+' / thông số theo canvas 1080×1920')
 for slot,j in enumerate([0,2]):
  row=FR[i*5+j];x=45+slot*890;frame(C,i,j,x,245,410,729);text(x,218,f'FRAME {j+1:02}',22,'bold');xx=x+445;yy=255
  yy=wrap(xx,yy,row['title'],390,25,'bold')+24
  for label,s in [('LỜI THOẠI ĐỀ XUẤT',row['vo_proposed']),('CÁCH TỔ CHỨC OVERLAY',row['description']),('THÔNG SỐ CHÍNH',params(row)),('VÀO / GIỮ / THOÁT',row['motion']['in']+' '+row['motion']['hold']+' '+row['motion']['out'])]:yy=bodyblock(xx,yy,label,s,390,20)
  text(x,1040,'SOURCE / lớp gốc giữ nguyên',20,'bold','#916A3C');wrap(x,1080,'Lớp text/shape ở track trên; riêng L07 cần foreground mask nằm giữa chữ sau người và chữ trước người.',410,20,col=B.GRAY)
 C.showPage()
 start(code+' / CHI TIẾT 02, 04 & 05','Khoảng nghỉ và bố cục chốt.', 'Karaoke giữ cùng preset trong frame 2/4; frame 5 bổ sung cách tổ chức overlay thứ ba.')
 for slot,j in enumerate([1,3,4]):
  row=FR[i*5+j];x=45+slot*585;text(x,235,f'FRAME {j+1:02} / '+('KARAOKE' if row['type']=='karaoke' else 'NHẤN'),21,'bold');frame(C,i,j,x+100,260,310,551)
  yy=wrap(x,855,row['title'],530,25,'bold')+9
  yy=bodyblock(x,yy,'LỜI THOẠI',row['vo_proposed'],530,20)
  yy=bodyblock(x,yy,'BỐ CỤC / THÔNG SỐ',row['description']+' '+params(row),530,18)
  # Short motion on this page; full per-layer instructions remain in specs/viewer.
  wrap(x,yy,('Active 113%; viền đen 2px. Đồng bộ theo VO thật.' if row['type']=='karaoke' else row['motion']['in']+' '+row['motion']['out']),530,18,col=B.GRAY)
 C.showPage()
# 31 / active-word proof
start('KARAOKE / BA TRẠNG THÁI CÙNG MỘT CÂU','Đọc tới đâu, từ đó lớn lên.','L04 / frame 02 / giữ nguyên word cells, điểm neo và khoảng cách / chỉ đổi từ active')
for phase,a in enumerate([1,2,3]):
 x=65+phase*580;mem=io.BytesIO();pc=canvas.Canvas(mem,pagesize=(1080,1920));g=B.draw(pc,3,1,active_override=a);pc.showPage();pc.save();doc=pdfium.PdfDocument(mem.getvalue());im=doc[0].render(scale=.7).to_pil();key=f'karaoke_active_{a}';im.convert('RGB').save(P/'proof'/f'{key}.jpg',quality=95);doc.close();C.drawImage(ImageReader(im),x,H-250-780,438.75,780);word=[z for z in g.layers if z.get('type')=='karaoke_word' and z['index']==a][0]['text'];text(x,220,'ACTIVE: '+word,25,'bold');(P/'proof'/f'{key}.svg').write_text(g.svg())
wrap(65,1120,'Từ active lớn 113%, màu vàng ấm, viền đen mỏng. Các từ khác giữ nguyên chỗ. Demo chuyển động nằm trong index.html; chưa có audio để nghiệm thu sync.',1630,27,'bold');C.showPage()
# 32 / handoff
start('BÀN GIAO / DÙNG TRONG DỰNG','Từ storyboard sang bản edit.', '45 frame + 45 overlay PNG + SVG text chỉnh sửa + font OFL + thông số từng layer + demo karaoke')
blocks=[('XEM & SO SÁNH','Mở index.html. Chọn L01–L09, xem 5 frame; bật demo karaoke để thấy từ active phóng theo nhịp mô phỏng. Có xem lớp overlay và guide rộng.'),('THAY CHỮ / THAY SOURCE','Cài font từ fonts/. Mở SVG để sửa text/shape nếu editor hỗ trợ, hoặc dựng lại theo tọa độ trong storyboard_specs.json. Ảnh source nằm trong assets/.'),('OVERLAY TRONG SUỐT','overlays/ gồm PNG alpha và SVG không source. L06 chỉ xuất phần chữ/đường nét; các cửa sổ crop cần tạo bằng bản sao source trong editor. L07 cần thêm foreground mask thật.'),('GIỚI HẠN ĐÃ GHI RÕ','Ảnh minh họa là tài sản AI có sẵn của dự án. Các phác thảo phối cảnh/mask không thay cho tracking video. Không có file project CapCut/After Effects native hoặc audio thu thật.'),('NGUỒN NGHIÊN CỨU','Kế thừa nghiên cứu Pinterest trong dự án: swash/lettering, hình vẽ theo chủ đề, typography sau người, spatial type và callout. Không đóng gói video reference của bên thứ ba.'),('KIỂM TRA TRƯỚC XUẤT','Xem trên điện thoại, đối chiếu UI placement, căn karaoke theo VO, kiểm tra dấu Việt, giao nhau giữa chữ/hình, mask/tracking và số học L09. Tắt guide trước render.')]
y=280
for label,s in blocks:
 text(50,y,label,23,'bold','#916A3C');wrap(470,y,s,1260,25);y+=145
C.showPage();C.save()
(P/'proof/pdf_text_bounds.json').write_text(json.dumps(PAGEBOUNDS,ensure_ascii=False))
print('PDF pages:',PAGE)
# Self-contained viewer; fonts and source imagery embedded to work without external network.
fontcss=''.join(f'@font-face{{font-family:{k};src:url(data:font/ttf;base64,{base64.b64encode(v.read_bytes()).decode()})}}' for k,v in B.FONTFILES.items())
images={f.name:'data:image/jpeg;base64,'+base64.b64encode(f.read_bytes()).decode() for f in (P/'assets').glob('*.jpg')}
svgs={}
for row in FR:
 key=row['id'];s=(P/'frames'/f'{key}.svg').read_text();s=re.sub(r'@font-face\{[^}]*\}','',s)
 for name,url in images.items():s=s.replace('../assets/'+name,url)
 ids=re.findall(r'id="([^"]+)"',s)
 for old in ids:s=s.replace('id="'+old+'"','id="'+key+'_'+old+'"').replace('url(#'+old+')','url(#'+key+'_'+old+')')
 svgs[key]=s
styles='''*{box-sizing:border-box}body{margin:0;background:#f4f0e8;color:#21362a;font:17px Arial,sans-serif;line-height:1.6}header{padding:30px 4vw;border-bottom:1px solid #d0c9ba}h1{font:46px Georgia;margin:10px 0}header p{max-width:1150px;margin:10px 0}nav{display:flex;gap:8px;flex-wrap:wrap;padding:22px 4vw}nav button{padding:11px 15px;border:1px solid #bbb3a3;background:transparent;border-radius:5px;color:#25392c;cursor:pointer}nav button.selected{background:#25392c;color:#fff}.toolbar{padding:0 4vw 18px;display:flex;gap:25px;align-items:center;flex-wrap:wrap}.toolbar button{padding:12px 18px;background:#25392c;color:#fff;border:0;border-radius:5px;cursor:pointer}main{padding:0 4vw 40px}#summary{max-width:1250px}.grid{display:grid;grid-template-columns:repeat(5,minmax(190px,1fr));gap:18px}.card h3{font-size:18px;min-height:60px}.stage{position:relative;width:100%;aspect-ratio:9/16;overflow:hidden;background:#333}.stage>svg{width:100%;height:100%;display:block}.card p{font-size:15px}.tag{font-size:12px;color:#936637;font-weight:bold;letter-spacing:1px}.card button{border:1px solid #a9aa9b;border-radius:4px;padding:8px 12px;background:transparent;cursor:pointer;color:#25392c}.card a{font-size:13px;color:#825f30}.small{font-size:13px;color:#697267}.guide{display:none;position:absolute!important;inset:0;pointer-events:none}.show-guides .guide{display:block}.overlay-only .stage{background:repeating-conic-gradient(#c5c5c5 0% 25%,#eee 0% 50%) 0/20px 20px}.overlay-only .art image,.overlay-only .art rect[opacity=".32"]{visibility:hidden}.playing .kw text{fill:inherit}.kw{transform-box:view-box}.playing .kw{animation-fill-mode:backwards;animation-iteration-count:infinite;animation-timing-function:linear;fill:#FFF9F0;transform-box:view-box}dialog{border:0;border-radius:10px;background:#f4f0e8;color:#21362a;max-width:1200px;width:95vw;max-height:95vh;padding:25px}dialog::backdrop{background:#000b}.detail{display:grid;grid-template-columns:minmax(230px,410px) 1fr;gap:30px}.detail img{width:100%;max-height:82vh;object-fit:contain}.detail aside{max-height:82vh;overflow:auto}.detail button{padding:10px 20px}details{margin:15px 0}code{font-size:13px}footer{padding:30px 4vw;border-top:1px solid #d0c9ba}@media(max-width:1100px){.grid{grid-template-columns:repeat(3,1fr)}}@media(max-width:700px){.grid{grid-template-columns:1fr 1fr}h1{font-size:34px}.detail{display:block}.detail img{max-height:60vh}.card h3{min-height:0}}'''
body='''<header><div class="tag">9 HỆ LAYOUT / 3 CẤP / 45 FRAME</div><h1>Storyboard cho lớp edit.</h1><p>Cùng source trong mỗi mẫu. Khác cấu trúc overlay ở frame nhấn; xen karaoke nhẹ. Chữ karaoke trắng, viền đen mỏng; từ active phóng 113%, cấp 2–3 có thể dùng màu nhấn.</p><p class="small">Demo karaoke chạy nhịp mô phỏng, không audio. Các mốc hình không thay cho footage đã tracking hoặc project dựng native.</p></header><nav id="nav"></nav><div class="toolbar"><button id="anim" onclick="toggleAnim()">Bật demo karaoke</button><label><input type="checkbox" onchange="document.body.classList.toggle('overlay-only',this.checked)"> Chỉ xem overlay</label><label><input type="checkbox" onchange="document.body.classList.toggle('show-guides',this.checked)"> Guide rộng tham chiếu</label><a href="Storyboard_L01_L09_45_Frames.pdf">Mở PDF</a></div><main><h2 id="title"></h2><p id="summary"></p><div id="grid" class="grid"></div></main><dialog id="detail"><div id="detailBody"></div></dialog><footer><a href="README.md">Hướng dẫn dùng</a> · <a href="storyboard_specs.json">Thông số từng layer</a><p class="small">L06: cùng ảnh gốc, thay crop mask. L07: mask thủ công cho ảnh demo; footage thật cần roto. L08: phối cảnh mô phỏng. L09: số giả định USD.</p></footer>'''
js='''const layouts=LAYOUTS,frames=FRAMES,svgs=SVGS;let selected='L01',playing=false;const $=s=>document.querySelector(s);function esc(s){return s.replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;')}function choose(id){selected=id;let m=layouts.find(x=>x.id===id);$('#title').textContent=m.id+' / Cấp '+m.level+' / '+m.name;$('#summary').textContent=m.structure;document.querySelectorAll('nav button').forEach(b=>b.classList.toggle('selected',b.dataset.id===id));$('#grid').innerHTML='';frames.filter(f=>f.layout===id).forEach(f=>{let a=document.createElement('article');a.className='card';a.dataset.key=f.id;a.innerHTML='<div class="tag">FRAME '+f.frame+' / '+(f.type==='karaoke'?'KARAOKE':'NHẤN')+'</div><h3>'+esc(f.title)+'</h3><div class="stage">'+svgs[f.id].replace('<svg ','<svg class="art" ')+'<svg class="guide" viewBox="0 0 1080 1920"><rect x="60" y="180" width="900" height="1360" fill="none" stroke="#8FE5AE" stroke-width="5" stroke-dasharray="18 12"/></svg></div><p>“'+esc(f.vo_proposed)+'”</p><p>'+esc(f.description)+'</p><button class="open-detail">Xem lớn & thông số</button><p><a href="frames/'+f.id+'.svg">SVG frame</a> · <a href="overlays/'+f.id+'.svg">SVG overlay</a> · <a href="overlays/'+f.id+'.png">PNG alpha</a></p>';$('#grid').append(a);a.querySelector('.open-detail').onclick=()=>detail(f.id);setupKaraoke(a,f)});document.body.classList.toggle('playing',playing)}
function setupKaraoke(card,f){let words=card.querySelectorAll('.kw');if(!words.length)return;let dur=words.length*.42+.6,pct=.42/dur*100,name='pop_'+f.id;let style=document.createElement('style');style.textContent='@keyframes '+name+'{0%{transform:scale(1);fill:#FFF9F0}'+(pct*.2)+'%, '+(pct*.72)+'%{transform:scale(1.13);fill:'+(f.level===1?'#FFF9F0':f.accent)+'}'+pct+'%,100%{transform:scale(1);fill:#FFF9F0}}';card.append(style);words.forEach((w,i)=>{let original=w.getAttribute('transform')||'',sc=(original.match(/scale\(([^)]+)\)/)||[])[1]||'1';w.removeAttribute('transform');w.style.transform='scale('+sc+')';let c=w.dataset.center.split(',');w.style.transformOrigin=c[0]+'px '+c[1]+'px';w.style.animationDuration=dur+'s';w.style.animationDelay=(i*.42)+'s';w.dataset.anim=name});}
function toggleAnim(){playing=!playing;document.body.classList.toggle('playing',playing);document.querySelectorAll('.kw').forEach(w=>w.style.animationName=playing?w.dataset.anim:'none');$('#anim').textContent=playing?'Dừng demo karaoke':'Bật demo karaoke'}
function detail(id){let f=frames.find(x=>x.id===id);let specs=f.layers.filter(x=>x.type==='text'||x.type==='karaoke_word').map(x=>x.type==='text'?x.text+' / '+x.font+' '+x.size_px+'px / baseline '+x.baseline.join(', '):x.text+' / tâm '+x.center.join(', ')+' / active 113% / viền ngoài 2px');$('#detailBody').innerHTML='<div class="detail"><img src="frames/'+f.id+'.jpg" alt="'+f.id+'"><aside><button class="close-detail">Đóng</button><h2>'+f.id+' / '+esc(f.title)+'</h2><h3>Lời thoại đề xuất</h3><p>'+esc(f.vo_proposed)+'</p><h3>Bố cục</h3><p>'+esc(f.description)+'</p><h3>Vào / Giữ / Thoát</h3><p>'+esc(f.motion.in)+'</p><p>'+esc(f.motion.hold)+'</p><p>'+esc(f.motion.out)+'</p><details open><summary>Thông số chữ</summary><ul>'+specs.map(s=>'<li>'+esc(s)+'</li>').join('')+'</ul></details><p class="small">Timing phải căn giọng thật. Tọa độ theo 1080×1920; viền/màu cần kiểm tra với source và UI nơi đăng.</p></aside></div>';$('#detailBody .close-detail').onclick=()=>$('#detail').close();$('#detail').showModal()}
layouts.forEach(m=>{let b=document.createElement('button');b.dataset.id=m.id;b.textContent=m.id+' / Cấp '+m.level;b.onclick=()=>{choose(m.id);if(playing)document.querySelectorAll('.kw').forEach(w=>w.style.animationName=w.dataset.anim)};$('#nav').append(b)});choose(selected);'''.replace('LAYOUTS',json.dumps(D['layouts'],ensure_ascii=False)).replace('FRAMES',json.dumps(FR,ensure_ascii=False)).replace('SVGS',json.dumps(svgs,ensure_ascii=False))
js += '\n' + (P/'motion_preview.js').read_text()
(P/'index.html').write_text('<!doctype html><html lang="vi"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>9 layout / 45 frame storyboard</title><style>'+fontcss+styles+'</style>'+body+'<script>'+js+'</script></html>')
README='''# Storyboard L01–L09 / 45 frame

9 mẫu × 5 frame. Cùng source trong mỗi mẫu; khác lớp overlay. Cấu trúc nhấn A / karaoke / nhấn B / karaoke / nhấn C. L01 là mẫu caption nên 5 frame đều nhẹ.

## Mở và dùng
- Mở `index.html` để xem, phóng lớn, đọc thông số; có demo karaoke không audio, xem overlay và bật guide rộng tham chiếu.
- `Storyboard_L01_L09_45_Frames.pdf`: 32 trang; mỗi L có overview 5 frame và hai trang diễn giải.
- `frames/`: 45 JPG 1080×1920 và 45 SVG composite.
- `overlays/`: 45 PNG alpha và 45 SVG chữ/shape không source.
- `fonts/`: font cùng giấy phép OFL. Cài font trước khi mở SVG trong phần mềm khác. Chữ giữ dạng text; không phải file AI native.
- `storyboard_specs.json`: vị trí chữ, font, cỡ, màu, nét, điểm neo karaoke và chỉ dẫn lớp/motion.
- `previews/`: 9 dải storyboard để xem nhanh.
- `proof/`: ba trạng thái karaoke; các từ giữ chỗ, active phóng 113%.

## Karaoke đã chốt
Chữ trắng + viền đen ngoài 2px. Từ đang đọc scale 100% > 113% > 100% quanh tâm riêng; không làm dịch cả dòng. Cấp 1 giữ trắng; cấp 2–3 active theo accent. Frame 2/4 giữ cùng preset x520, baseline 1240/1328, cỡ 62px. Timing demo chưa có audio nên chỉ mô phỏng; phải căn VO thật.

## Source và các mẫu đặc biệt
- Source là ảnh AI minh họa đã có trong dự án, không phải nhân vật/căn nhà hoặc bằng chứng kinh doanh thật.
- Base source không thay giữa 5 frame. L06 dùng crop/duplicate cùng một ảnh gốc; không thay ảnh để tạo khác biệt. Overlay alpha của L06 chỉ có chữ/nét: editor cần tạo crop mask bằng source của mình.
- L07 composite có mask vector thủ công cho ảnh tĩnh, để thấy thứ tự chữ sau người / foreground / chữ trước người. Overlay PNG/SVG riêng không mang foreground người demo. Với video thật cần roto/track mask.
- L08 là phác thảo mặt phẳng/góc/xa gần trên ảnh tĩnh, chưa phải camera tracking đã nghiệm thu.
- L09 dùng số giả định USD: 5,000 thực nhận; tổng chi 2,000+1,000+500=3,500; còn 1,500. Không phải mức chi tiêu được khuyến nghị.

## Hướng dẫn biên tập
Frame 1/3/5 là ba cách bố trí overlay có cùng nhận diện; frame 2/4 là khoảng nghỉ. Có thể chọn một cách hoặc phối theo nội dung. Không đổi font/màu để giả lập bố cục mới.
Guide x60–960, y180–1540 là vùng sáng tạo nội bộ khởi điểm. Không là safe-zone chính thức chung cho TikTok/Instagram. Đối chiếu UI, caption đăng bài và CTA trước khi xuất; tắt guide khi render.

Bộ này là storyboard + tài sản vector/raster + demo karaoke. Chưa có audio, video footage đã tracking hoặc project CapCut/After Effects native. SVG và JSON không được gọi là project dựng native.
'''
README += '\n## Motion layout trong bản xem\nBấm Bật motion layout để xem 24 frame nhấn của L02–L09. Có tạm dừng, phát lại, thanh kéo 0–6 giây, tốc độ 0.5×/1×/1.5× và lặp. Mở lớn từng frame để xem chuyển động. L01 giữ karaoke; karaoke dùng điều khiển độc lập. Chữ gõ/bay vào, box quét, swash vẽ, callout và thứ tự explainer được mô phỏng trong trình duyệt; chưa phải preset motion native. Khi tắt motion, bố cục trở lại trạng thái đầy đủ.\n'
(P/'README.md').write_text(README)
print('Created self-contained viewer and README.')
