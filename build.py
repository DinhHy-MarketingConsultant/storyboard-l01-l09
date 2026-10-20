from pathlib import Path
import io,math,json,html,base64,shutil,zipfile,re,textwrap
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
import pypdfium2 as pdfium
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).parent;ROOT=P.parent.parent;A=ROOT/'video_editing_brand_book/assets';T=P.parent/'type_illustration_research/fonts'
for sub in ['frames','overlays','assets','fonts','proof','previews']:(P/sub).mkdir(exist_ok=True)
FONTFILES={'sans':A/'fonts/bevietnampro-400.ttf','bold':A/'fonts/bevietnampro-700.ttf','anton':A/'fonts/anton-400.ttf','hand':A/'fonts/dancingscript-700.ttf','lora':A/'fonts/lora-400.ttf','mono':A/'fonts/ibmplexmono-400.ttf','space':A/'fonts/spacegrotesk-700.ttf','fraunces':T/'fraunces.ttf','bricolage':T/'bricolagegrotesque.ttf','script':T/'luxuriousscript.ttf','news':T/'newsreader.ttf','wide':T/'unbounded.ttf','anybody':T/'anybody.ttf'}
for k,f in FONTFILES.items():pdfmetrics.registerFont(TTFont(k,str(f)));shutil.copy2(f,P/'fonts'/f'{k}.ttf')
WHITE='#FFF9F0';INK='#1E2D27';PAPER='#F4F0E8';GRAY='#6A7269'
META=[
('L01',1,'Caption / karaoke',12,'#FFFFFF','Be Vietnam Pro','Câu ngắn, nhịp chữ và điểm neo','Một dòng, bậc thang và căn phải; K2/K4 giữ cùng preset giữa khung.'),
('L02',1,'Hero typography',15,'#FF6641','Anton + Dancing Script','Một ý lớn làm trọng tâm','A: poster xếp chồng. B: keyword bắc ngang. C: trục chữ dọc. Box chỉ dùng ở frame nhấn.'),
('L03',1,'Cụm ý phân bố',12,'#89CEFF','Lora + Be Vietnam Pro','Nhiều cụm ý tạo thứ tự đọc','A: đường chéo. B: hai phía đối lập. C: một tâm và các ý vệ tinh.'),
('L04',2,'Chữ + illustration',9,'#FFD58D','Fraunces Italic + Be Vietnam Pro','Nét vẽ cùng chữ kể chuyện','A: chữ chính + hình nhỏ. B: hình lớn + chữ bao quanh. C: chuỗi motif nối ba hành động.'),
('L05',2,'Object callout',8,'#8CEBD8','Newsreader Italic + IBM Plex Mono','Chú thích gắn vào chi tiết thật','A: một nhãn. B: hai nhãn từ một vật thể. C: điểm đánh số và bảng chú thích mở.'),
('L06',2,'Montage nhiều vùng hình',5,'#FFB265','Bricolage Grotesque + Newsreader','Tiêu đề nối các vùng hình','A: hai dải dọc. B: hai vùng trên/dưới. C: source lớn + lát hình chéo. Cùng ảnh gốc.'),
('L07',3,'Chữ qua lớp che khuất',10,'#FFED72','Anton + Fraunces Italic','Tương tác giữa lớp người và lớp chữ','A: hai dòng sau người. B: chữ trước/sau khác lớp. C: chữ cong sau người + câu chốt phía trước.'),
('L08',3,'Chữ trong không gian',1,'#DBF55A','Anton + Anybody Italic','Vị trí, hướng và tỷ lệ trong cảnh','A: ba mặt phẳng chữ. B: chữ theo mặt bàn. C: các từ xa/gần. Giữ hướng mở đầu C03.'),
('L09',3,'Explainer nhiều bước',3,'#66DBFF','Space Grotesk + IBM Plex Mono','Thông tin được nối và biến đổi','A: phép trừ nối kết quả. B: nhiều khoản hội tụ. C: một đầu vào chia nhánh. Số liệu giả định USD.')]
# Every row contains 5 overlay compositions on one fixed source, with basic caption states between emphasis states.
COPY=[
 [('Một dòng theo lời','Mỗi việc nhỏ đều có giá trị.','Caption một dòng, ở vùng trước ngực. Từ đang đọc chỉ phóng nhẹ, toàn bộ chữ trắng.', ['Mỗi việc nhỏ','đều có giá trị.']),('Karaoke / điểm neo chính','Bắt đầu từ một việc nhỏ.','Hai dòng căn giữa, một từ active. Đây là preset dùng lại ở frame 4.',['Bắt đầu từ','một việc nhỏ.']),('Bậc thang nhẹ','Hiểu rồi chọn, sau đó làm.','Ba cụm caption lệch dần sang phải, tạo nhịp đọc bậc thang. Không dùng headline lớn.',['Hiểu rồi','chọn, sau đó','làm.']),('Karaoke / giữ preset','Làm đều quan trọng hơn làm nhiều.','Giữ đúng font, cỡ, căn giữa và điểm neo của frame 2.',['Làm đều quan trọng','hơn làm nhiều.']),('Căn phải / câu chốt','Hôm nay, làm một việc thôi.','Caption căn phải trong khoảng trống; nhấn động từ theo giọng. Không thêm đồ họa.',['Hôm nay, làm','một việc thôi.'])],
 [('Poster xếp chồng','Tiệm đông khách mà vẫn có thể lỗ.','ĐÔNG/KHÁCH tạo cột lớn; vẫn là chữ nối; LỖ? nằm trong box cam. Không đổi source.',None),('Karaoke / giải thích','Tiền vào chưa phải tiền lời.','Caption trắng viền đen; từ active phóng 113%, không dùng màu cam ở cấp 1.',['Tiền vào chưa phải','tiền lời.']),('Keyword bắc ngang','Đừng chỉ đếm khách. Hãy nhìn tiền còn lại.','Một từ TIỀN ở giữa, box CÒN LẠI bắc ngang; câu dẫn nhỏ phía trên. Khác cấu trúc cột frame 1.',None),('Karaoke / hành động','Ghi đủ từng khoản chi.','Giữ preset caption frame 2, đổi câu và từ active theo lời.',['Ghi đủ từng','khoản chi.']),('Trục dọc / chốt','Để có lời, bắt đầu từ ghi chép.','LỜI xoay thành trục dọc trái; câu BẮT ĐẦU TỪ GHI CHÉP xếp thành nhịp bên phải.',None)],
 [('Ba cụm theo đường chéo','Muốn an tâm, cần kế hoạch và bắt đầu nhỏ.','Ba cụm chữ tạo đường đọc trái trên, phải giữa, trái dưới; không che mắt. Mỗi ý vào theo lời.',None),('Karaoke / nối ý','Một việc nhỏ cũng đáng bắt đầu.','Caption trắng viền đen. Cấp 1 chỉ phóng từ active, giữ màu trắng.',['Một việc nhỏ cũng','đáng bắt đầu.']),('Hai phía đối lập','Để sau hay bắt đầu hôm nay?','Câu hỏi nhỏ ở trên. Hai vế ĐỂ SAU/HÔM NAY tách trái/phải, khoảng giữa là khoảng nghỉ.',None),('Karaoke / trả lời','Chọn điều bạn làm được hôm nay.','Giữ cùng preset và điểm neo như frame 2; không thêm đường dẫn.',['Chọn điều bạn làm','được hôm nay.']),('Một tâm / ba vệ tinh','Hiểu, chọn rồi làm: từng bước một.','BẮT ĐẦU là tâm thấp; HIỂU/CHỌN/LÀM là ba cụm vệ tinh. Đường mảnh chỉ dẫn thứ tự đọc.',None)],
 [('Chữ chính / hình nhỏ','Cho mình chậm một nhịp.','Fraunces mềm lệch trái; một tách cà phê nhỏ nằm cạnh flourish. Nét hơi nước kết nối với đuôi chữ vẽ riêng.',None),('Karaoke / nghỉ nhịp','Không cần vội trong mọi khoảnh khắc.','Chữ trắng viền đen; từ active vàng ấm và phóng nhẹ. Không illustration ở frame này.',['Không cần vội trong','mọi khoảnh khắc.']),('Hình lớn / chữ ôm quanh','Đặt việc xuống, nhìn quanh và thở một chút.','Tách cà phê lớn là tâm. Ba cụm chữ ôm quanh hơi nước và quai; hình không có nền card.',None),('Karaoke / cùng chất liệu','Một khoảng nghỉ cũng có ý nghĩa.','Giữ preset caption. Có thể giữ một nét hơi nước rất nhỏ ở góc, không cạnh tranh với chữ.',['Một khoảng nghỉ','cũng có ý nghĩa.']),('Chuỗi ba motif','Uống một ngụm, ngắm một chút, nghỉ một nhịp.','Ba motif cà phê, cửa sổ, chiếc lá nối thành một đường ngang. Nhãn ngắn theo từng hình, headline nhỏ ở trên.',None)],
 [('Một nhãn gắn vật thể','Bắt đầu bằng ánh sáng trong căn phòng.','Điểm neo ở cửa sổ thật; đường gãy dẫn tới nhãn bên trái. Headline italic ngắn, không phải illustration ngôi nhà.',None),('Karaoke / quan sát','Hãy nhìn nơi bạn sẽ ngồi mỗi ngày.','Từ active mint, viền đen mỏng và phóng 113%; không giữ cả bộ callout trên source.',['Hãy nhìn nơi bạn','sẽ ngồi mỗi ngày.']),('Một vật thể / hai nhánh','Một góc ngồi có thể phục vụ nhiều việc.','Cùng ghế sofa có hai điểm chú thích: vị trí ngồi và vùng thư giãn. Nhãn ở hai phía, không bắn đường tùy ý.',None),('Karaoke / nối ý','Chọn theo cách bạn sử dụng không gian.','Giữ vị trí và cỡ caption của frame 2; nhấn từ sử dụng theo audio.',['Chọn theo cách bạn','sử dụng không gian.']),('Điểm đánh số / chú giải mở','Ánh sáng, chỗ ngồi và mặt bàn: nhìn cùng nhau.','Ba điểm số đặt vào cửa sổ, sofa và bàn thật. Cột chú giải cùng phía; không có bảng nền kín.',None)],
 [('Hai dải dọc / chữ nối','Một nơi có nhiều cách để nhìn.','Hai dải lấy hai crop từ cùng một ảnh gốc, luôn phủ kín khung; tiêu đề nối qua cả hai vùng.',None),('Karaoke / trở về một hình','Cùng một căn phòng, thử nhìn kỹ hơn.','Base source full khung trở lại; caption màu trắng viền đen, active màu cam đào.',['Cùng một căn phòng,','thử nhìn kỹ hơn.']),('Hai vùng ngang / chữ tại giao điểm','Nhìn tổng thể rồi nhìn vào chi tiết.','Hai vùng crop trên/dưới từ cùng ảnh gốc; headline đặt ngang điểm tiếp giáp, không thêm khe trắng.',None),('Karaoke / giữ nhịp','Điều bạn cần có thể nằm ở chi tiết.','Không chia vùng hình. Caption cùng preset với frame 2, từ active phóng nhẹ.',['Điều bạn cần có thể','nằm ở chi tiết.']),('Một vùng lớn / lát hình chéo','Một không gian, nhiều câu chuyện.','Giữ base full khung; thêm hai lát crop chéo cùng ảnh gốc ở hai mép. Tiêu đề nằm ở vùng mở giữa.',None)],
 [('Hai dòng sau người','Bắt đầu một chương mới.','Giữ hướng mở đầu C01: BẮT/ĐẦU vàng lớn phía sau tóc/vai; nhân vật là lớp trước. Câu phụ phía trước.',None),('Karaoke / lớp trước người','Bắt đầu từ điều bạn có thể làm hôm nay.','Chữ ở trên foreground, trắng viền đen; active vàng, phóng nhẹ. Chữ lớn phía sau đã thoát.',['Bắt đầu từ điều bạn','có thể làm hôm nay.']),('Chữ trước / chữ sau','Từng bước nhỏ vẫn đưa bạn đi tiếp.','TỪNG là chữ lớn sau nhân vật. bước nhỏ nằm ở lớp trước, khác vị trí và tỷ lệ, tạo hai tầng đọc.',None),('Karaoke / giữ khoảng nghỉ','Không cần làm mọi thứ cùng lúc.','Giữ preset caption frame 2 và tất cả chữ ở lớp trước. Không giữ mask typography phức tạp khi không cần.',['Không cần làm','mọi thứ cùng lúc.']),('Chữ cong qua tóc / câu chốt trước','Một chương mới, theo cách của bạn.','Chữ MỘT CHƯƠNG MỚI chạy cong sau vùng đầu. Câu của bạn ở trước, nằm ở khoảng trống bên trái.',None)],
 [('Ba mặt phẳng chữ','Thu, chi và phần còn lại: ba điều cần nhìn.','Giữ hướng mở đầu C03: THU trái, CHI phải, CÒN LẠI gần phía dưới; góc và tỷ lệ khác nhau.',None),('Karaoke / trở về người','Hiểu dòng tiền trước khi quyết định.','Source không đổi, đồ họa không gian đã rút; active lime phóng lên, viền đen vẫn giữ.',['Hiểu dòng tiền','trước khi quyết định.']),('Một mặt bàn / chữ trải ngang','Đặt các khoản thu chi vào cùng một cách nhìn.','Ba cụm THU/CHI/CÒN được bố trí như nằm trên mặt bàn. Góc nghiêng và baseline cùng tuân một mặt phẳng.',None),('Karaoke / nối ý','Ghi nhận đều để nhìn rõ hơn.','Giữ preset caption. Một dòng dẫn nhẹ, không thêm mặt phẳng chữ 3D.',['Ghi nhận đều','để nhìn rõ hơn.']),('Xa gần / hướng đi','Nhìn đủ dòng tiền của mình.','Các từ ĐỌC/ĐỦ/DÒNG TIỀN lần lượt ở xa, giữa và gần. Khác bố cục ba mặt phẳng ở frame 1.',None)],
 [('Phép trừ / đường kết quả','Giả sử thực nhận năm nghìn, trừ hai nghìn tiền nhà.','5,000 ở trên trái, −2,000 ở trục giữa; đường gấp khúc dẫn tới 3,000. Toàn bộ số là giả định USD.',None),('Karaoke / giải thích','Đó là số còn lại sau tiền nhà.','Caption trắng viền đen, active cyan phóng nhẹ. Dữ liệu được nhắc bằng lời, không thêm đồ thị.',['Đó là số còn lại','sau tiền nhà.']),('Ba khoản hội tụ','Ví dụ này có ba khoản chi, tổng là ba nghìn năm trăm.','2,000 + 1,000 + 500 ở ba điểm; đường hội tụ về 3,500. Đây là cấu trúc mới, không chỉ đổi số ở frame 1.',None),('Karaoke / nối kết quả','Cộng đủ rồi nhìn phần còn lại.','Giữ caption như frame 2. Từ active cyan; không mang số giả định thành khuyến nghị.',['Cộng đủ rồi nhìn','phần còn lại.']),('Một đầu vào / hai nhánh','Năm nghìn chia thành ba nghìn năm trăm đã chi, còn một nghìn năm trăm.','5,000 ở đầu vào. Nhánh cam 3,500 đã chi; nhánh cyan 1,500 còn lại. Dữ liệu nhất quán với các bước trước.',None)]
]
for n in {m[3] for m in META}:shutil.copy2(A/f'background_{n}.jpg',P/'assets'/f'background_{n}.jpg')
class G:
 def __init__(self,c,overlay=False):self.c=c;self.s=[];self.layers=[];self.overlay=overlay;self.id=0;self.used=set()
 def text(self,x,y,s,size=64,font='bold',col=WHITE,anchor='start',rot=0,outline=0,record=True):
  # Paint stroke first and fill second, preserving a thin outside edge around Vietnamese glyphs.
  self.used.add(font);self.c.saveState();self.c.translate(x,1920-y);self.c.rotate(-rot);self.c.setFillColor(col);self.c.setStrokeColor('#000000');self.c.setLineWidth(outline*2)
  width=pdfmetrics.stringWidth(s,font,size);xx={'start':0,'middle':-width/2,'end':-width}[anchor]
  if outline:
   t=self.c.beginText(xx,0);t.setFont(font,size);t.setTextRenderMode(1);t.textOut(s);self.c.drawText(t)
  t=self.c.beginText(xx,0);t.setFont(font,size);t._code.append('0 Tr');t.textOut(s);self.c.drawText(t);self.c.restoreState()
  o=f' stroke="#000000" stroke-width="{outline*2}" paint-order="stroke fill" stroke-linejoin="round"' if outline else ''
  self.s.append(f'<text x="{x}" y="{y}" font-family="{font}" font-size="{size}" fill="{col}" text-anchor="{anchor}" transform="rotate({rot} {x} {y})"{o}>{html.escape(s)}</text>')
  if record:self.layers.append({'type':'text','text':s,'baseline':[x,y],'font':font,'size_px':size,'fill':col,'align':anchor,'rotation_deg':rot,'outline_outside_px':outline,'approx_width_px':round(width,1)})
 def line(self,pts,col=WHITE,w=3):
  self.c.setStrokeColor(col);self.c.setLineWidth(w);q=self.c.beginPath();q.moveTo(pts[0][0],1920-pts[0][1])
  for x,y in pts[1:]:q.lineTo(x,1920-y)
  self.c.drawPath(q,stroke=1,fill=0);self.s.append('<polyline points="'+' '.join(f'{x},{y}' for x,y in pts)+f'" stroke="{col}" stroke-width="{w}" fill="none" stroke-linecap="round" stroke-linejoin="round"/>');self.layers.append({'type':'line','points':pts,'stroke':col,'width_px':w})
 def curve(self,p,col=WHITE,w=4):
  self.c.setStrokeColor(col);self.c.setLineWidth(w);q=self.c.beginPath();q.moveTo(p[0][0],1920-p[0][1]);q.curveTo(p[1][0],1920-p[1][1],p[2][0],1920-p[2][1],p[3][0],1920-p[3][1]);self.c.drawPath(q,stroke=1,fill=0)
  self.s.append(f'<path d="M{p[0][0]} {p[0][1]} C{p[1][0]} {p[1][1]} {p[2][0]} {p[2][1]} {p[3][0]} {p[3][1]}" fill="none" stroke="{col}" stroke-width="{w}" stroke-linecap="round"/>');self.layers.append({'type':'bezier','points':p,'stroke':col,'width_px':w})
 def rect(self,x,y,w,h,col):self.c.setFillColor(col);self.c.rect(x,1920-y-h,w,h,fill=1,stroke=0);self.s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{col}"/>');self.layers.append({'type':'rect','bounds':[x,y,w,h],'fill':col})
 def ellipse(self,x,y,rx,ry,col=WHITE,w=4,fill=None):
  self.c.setStrokeColor(col);self.c.setLineWidth(w)
  if fill:self.c.setFillColor(fill)
  self.c.ellipse(x-rx,1920-y-ry,x+rx,1920-y+ry,fill=bool(fill),stroke=1);self.s.append(f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="{fill or "none"}" stroke="{col}" stroke-width="{w}"/>');self.layers.append({'type':'ellipse','center':[x,y],'radius':[rx,ry],'stroke':col,'width_px':w})
 def arrow(self,p1,p2,col=WHITE,w=4):
  self.line([p1,p2],col,w);a=math.atan2(p2[1]-p1[1],p2[0]-p1[0]);self.line([(p2[0]-24*math.cos(a-.5),p2[1]-24*math.sin(a-.5)),p2,(p2[0]-24*math.cos(a+.5),p2[1]-24*math.sin(a+.5))],col,w)
 def image(self,n,x=0,y=0,w=1080,h=1920,focus=.5,polygon=None):
  if self.overlay:return
  path=A/f'background_{n}.jpg';im=ImageReader(str(path));iw,ih=im.getSize();scale=max(w/iw,h/ih);ww,hh=iw*scale,ih*scale;xx=x+(w-ww)*focus;yy=y+(h-hh)/2
  if n==3 and x==0 and y==0 and w==1080 and h==1920:ww*=1.05;hh*=1.05;xx=x+(w-ww)*focus;yy=y
  if n==10 and x==0 and y==0 and w==1080 and h==1920:xx,yy,ww,hh=-690,0,3072,2048
  self.id+=1;pid=f'crop{self.id}';self.c.saveState();q=self.c.beginPath()
  if polygon:
   q.moveTo(polygon[0][0],1920-polygon[0][1])
   for a,b in polygon[1:]:q.lineTo(a,1920-b)
   q.close();clip='<polygon points="'+' '.join(f'{a},{b}' for a,b in polygon)+'"/>'
  else:q.rect(x,1920-y-h,w,h);clip=f'<rect x="{x}" y="{y}" width="{w}" height="{h}"/>'
  self.c.clipPath(q,stroke=0);self.c.drawImage(im,xx,1920-yy-hh,ww,hh);self.c.restoreState();self.s.append(f'<defs><clipPath id="{pid}">{clip}</clipPath></defs><image href="../assets/background_{n}.jpg" x="{xx}" y="{yy}" width="{ww}" height="{hh}" clip-path="url(#{pid})"/>')
 def grade(self):
  if self.overlay:return
  self.c.saveState();self.c.setFillColor('#0E1718');self.c.setFillAlpha(.32);self.c.rect(0,0,1080,1920,fill=1,stroke=0);self.c.restoreState();self.s.append('<rect width="1080" height="1920" fill="#0E1718" opacity=".32"/>')
 def foreground(self):
  if self.overlay:return
  pts=[(154,59),(159,39),(172,20),(189,12),(205,13),(219,17),(230,29),(233,47),(229,67),(241,87),(262,104),(274,127),(272,153),(261,167),(276,214),(286,256),(141,256),(142,217),(139,189),(127,172),(132,133),(139,107),(141,87)]
  xy=[(a*8-690,b*8) for a,b in pts];self.c.saveState();q=self.c.beginPath();q.moveTo(xy[0][0],1920-xy[0][1])
  for a,b in xy[1:]:q.lineTo(a,1920-b)
  q.close();self.c.clipPath(q,stroke=0);self.c.drawImage(ImageReader(str(A/'background_10.jpg')),-690,-128,3072,2048)
  self.c.setFillColor('#0E1718');self.c.setFillAlpha(.32);self.c.rect(0,0,1080,1920,fill=1,stroke=0);self.c.restoreState()
  self.s.append('<defs><clipPath id="foreground"><polygon points="'+' '.join(f'{a},{b}' for a,b in xy)+'"/></clipPath></defs><g clip-path="url(#foreground)"><image href="../assets/background_10.jpg" x="-690" y="0" width="3072" height="2048"/><rect width="1080" height="1920" fill="#0E1718" opacity=".32"/></g>');self.layers.append({'type':'foreground_mask_demo','source':'background_10.jpg','polygon':xy,'status':'manual static demo; retrace/track on real footage'})
 def arc(self,s,cx,cy,r,size,font,col):
  ws=[pdfmetrics.stringWidth(ch,font,size)+3 for ch in s];cur=-sum(ws)/2
  for ch,w in zip(s,ws):
   a=cur/r;self.text(cx+r*math.sin(a),cy+r*(1-math.cos(a)),ch,size,font,col,rot=math.degrees(a));cur+=w
 def cup(self,cx,cy,s,col):
  self.ellipse(cx,cy,140*s,25*s,col,5);self.curve([(cx-140*s,cy),(cx-125*s,cy+200*s),(cx+125*s,cy+200*s),(cx+140*s,cy)],col,5)
  self.curve([(cx+140*s,cy+15*s),(cx+260*s,cy-25*s),(cx+220*s,cy+150*s),(cx+120*s,cy+125*s)],col,5);self.curve([(cx-170*s,cy+180*s),(cx-80*s,cy+235*s),(cx+140*s,cy+220*s),(cx+190*s,cy+170*s)],col,4)
  self.curve([(cx,cy-20*s),(cx+90*s,cy-100*s),(cx-100*s,cy-140*s),(cx+20*s,cy-250*s)],col,4)
 def leaf(self,cx,cy,s,col):
  self.curve([(cx,cy),(cx-150*s,cy-140*s),(cx+80*s,cy-250*s),(cx+110*s,cy-230*s)],col,5);self.curve([(cx+110*s,cy-230*s),(cx+150*s,cy-70*s),(cx+40*s,cy-15*s),(cx,cy)],col,5);self.line([(cx-25*s,cy+50*s),(cx+90*s,cy-205*s)],col,4)
 def window(self,cx,cy,s,col):
  self.line([(cx-120*s,cy+180*s),(cx-120*s,cy-110*s),(cx+120*s,cy-110*s),(cx+120*s,cy+180*s)],col,5);self.line([(cx,cy-110*s),(cx,cy+180*s)],col,4);self.line([(cx-120*s,cy+30*s),(cx+120*s,cy+30*s)],col,4);self.line([(cx-155*s,cy+190*s),(cx+155*s,cy+190*s)],col,5)
 def karaoke(self,lines,level,col,active=2,y=1240,size=62,align='middle',x=520,stair=False):
  self.used.add('bold');self.s.append(f'<g class="karaoke" data-active-color="{WHITE if level==1 else col}">');idx=0
  for j,line in enumerate(lines):
   words=line.split();widths=[pdfmetrics.stringWidth(w,'bold',size) for w in words];cells=[w*1.15+18 for w in widths];total=sum(cells);xx=x-total/2 if align=='middle' else (x-total if align=='end' else x)
   if stair:xx=x+j*65
   yy=y+j*88
   for word,cw in zip(words,cells):
    cx=xx+cw/2;cy=yy-size*.35;scale=1.13 if idx==active else 1;fill=WHITE if level==1 or idx!=active else col
    # Render the active word around its own fixed center, with layout space already reserved.
    old=len(self.s);self.text(cx,cy+(yy-cy)*scale,word,size*scale,'bold',fill,'middle',outline=2,record=False);self.s=self.s[:old]
    self.s.append(f'<g class="kw" data-word="{idx}" data-center="{cx:.2f},{cy:.2f}" transform="translate({cx:.2f} {cy:.2f}) scale({scale}) translate({-cx:.2f} {-cy:.2f})"><text x="{cx:.2f}" y="{yy}" font-family="bold" font-size="{size}" text-anchor="middle" fill="{fill}" stroke="#000000" stroke-width="4" paint-order="stroke fill" stroke-linejoin="round">{html.escape(word)}</text></g>')
    self.layers.append({'type':'karaoke_word','index':idx,'text':word,'center':[round(cx,2),round(cy,2)],'baseline_y':yy,'font':'bold','base_size_px':size,'active_scale':1.13,'static_active':idx==active,'inactive_fill':WHITE,'active_fill':WHITE if level==1 else col,'outline_outside_px':2,'cell_width_px':round(cw,2)});idx+=1;xx+=cw
  self.s.append('</g>')
 def svg(self):
  css=''.join(f'@font-face{{font-family:{k};src:url(../fonts/{k}.ttf)}}' for k in self.used)
  return '<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1920" viewBox="0 0 1080 1920"><style>'+css+'</style>'+''.join(self.s)+'</svg>'

def draw(c,i,j,overlay=False,active_override=None):
 m=META[i];code,lv,name,bg,col,*_=m;g=G(c,overlay);g.image(bg);g.grade();frame=j+1;data=COPY[i][j]
 if j in [1,3]:
  g.karaoke(data[3],lv,col,2 if active_override is None else active_override)
  if i==3 and j==3:g.curve([(870,1470),(915,1425),(835,1425),(880,1370)],col,3)
  return g
 if i==0:
  if j==0:g.karaoke(['Mỗi việc nhỏ đều có giá trị.'],1,col,2 if active_override is None else active_override,1200,56)
  elif j==2:g.karaoke(['Hiểu rồi','chọn, sau đó','làm.'],1,col,3 if active_override is None else active_override,1050,64,'start',160,True)
  else:g.karaoke(['Hôm nay, làm','một việc thôi.'],1,col,2 if active_override is None else active_override,1190,64,'end',920)
 elif i==1:
  if j==0:
   g.text(80,210,'CHUYỆN CHỦ TIỆM',28);g.text(80,610,'ĐÔNG',265,'anton');g.text(80,910,'KHÁCH',240,'anton');g.text(85,1170,'vẫn',140,'hand');g.rect(350,990,610,390,col);g.text(655,1310,'LỖ?',250,'anton','#15231D','middle')
  elif j==2:
   g.text(540,390,'Đừng chỉ đếm khách.',54,'hand',WHITE,'middle');g.text(540,800,'TIỀN',220,'anton',WHITE,'middle');g.rect(80,940,880,270,col);g.text(520,1140,'CÒN LẠI',157,'anton','#15231D','middle');g.text(540,1390,'mới là điều cần nhìn.',48,'sans',WHITE,'middle')
  else:
   g.text(85,360,'ĐỂ CÓ',54,'hand');g.rect(65,780,445,600,col);g.text(480,1300,'LỜI',320,'anton','#15231D',rot=-90)
   for y,t in [(650,'BẮT'),(810,'ĐẦU'),(950,'TỪ'),(1120,'GHI'),(1280,'CHÉP')]:g.text(565,y,t,100,'anton')
 elif i==2:
  if j==0:
   g.text(90,460,'Muốn an tâm',79,'lora');g.line([(95,500),(260,500)],col,4);g.text(950,970,'Cần kế hoạch',72,'bold',WHITE,'end');g.text(110,1370,'Bắt đầu nhỏ',94,'lora',col)
  elif j==2:
   g.text(540,370,'Ghi chép?',100,'lora',WHITE,'middle');g.text(90,1110,'ĐỂ',93,'bold');g.text(90,1230,'SAU',112,'bold');g.text(950,1110,'HÔM',93,'bold',col,'end');g.text(950,1230,'NAY',112,'bold',col,'end');g.text(540,1450,'Bạn chọn lúc nào?',43,'sans',WHITE,'middle')
  else:
   g.text(100,460,'HIỂU',72,'bold');g.text(950,860,'CHỌN',72,'bold',WHITE,'end');g.text(170,1430,'LÀM',72,'bold',col);g.text(540,1150,'BẮT ĐẦU',94,'lora',col,'middle');g.line([(270,500),(90,700),(90,950),(440,1030)],col,2);g.line([(840,900),(660,1030)],col,2);g.line([(260,1340),(440,1190)],col,2)
 elif i==3:
  if j==0:
   g.text(90,350,'MỘT CHÚT ĐỜI THƯỜNG',28,'sans',col);g.text(90,700,'Chậm',200,'fraunces');g.text(140,915,'một nhịp',145,'fraunces',col);g.curve([(150,1010),(360,1120),(970,1010),(850,850)],col,6);g.cup(800,1320,.65,col)
  elif j==2:
   g.cup(500,1030,1.2,col);g.text(100,580,'Đặt việc xuống',65,'fraunces',WHITE,rot=-7);g.text(920,760,'nhìn quanh',67,'fraunces',col,'end',rot=8);g.text(530,1430,'thở một chút.',74,'fraunces',WHITE,'middle');g.curve([(160,640),(90,850),(100,1000),(260,1060)],col,4)
  else:
   g.text(100,480,'CHO MÌNH',84,'fraunces');g.text(100,620,'một khoảng nghỉ',72,'fraunces',col);g.cup(210,1030,.6,col);g.window(540,1000,.58,col);g.leaf(850,1110,.63,col);g.line([(325,1160),(450,1160)],col,3);g.line([(650,1160),(760,1160)],col,3)
   for x,t in [(210,'Uống'),(540,'Ngắm'),(850,'Nghỉ')]:g.text(x,1350,t,57,'fraunces',WHITE,'middle')
 elif i==4:
  if j==0:
   g.text(90,360,'Nhìn ánh sáng',94,'news');g.ellipse(650,650,9,9,col,3,col);g.line([(650,650),(350,560),(100,560)],col,4);g.text(100,510,'CỬA SỔ',43,'mono',WHITE);g.text(100,1430,'Một chi tiết để bắt đầu quan sát.',35,'sans')
  elif j==2:
   g.text(100,350,'Một góc ngồi',92,'news');g.text(100,450,'nhiều cách dùng',69,'news',col)
   g.ellipse(820,1240,8,8,col,3,col);g.line([(820,1240),(550,910),(100,910)],col,4);g.text(100,855,'CHỖ NGỒI',42,'mono');g.ellipse(720,1280,8,8,col,3,col);g.line([(720,1280),(950,1120),(950,1020)],col,4);g.text(950,980,'THƯ GIÃN',38,'mono',WHITE,'end')
  else:
   g.text(100,350,'Đọc căn phòng',92,'news');labels=[('01','Ánh sáng',650,650),('02','Chỗ ngồi',820,1240),('03','Mặt bàn',420,1480)]
   for k,(num,label,x,y) in enumerate(labels):
    g.ellipse(x,y,37,37,col,3);g.text(x,y+13,num,29,'mono',WHITE,'middle');g.text(100,550+k*115,num,33,'mono',col);g.text(195,550+k*115,label,48,'news')
 elif i==5:
  # The source asset remains background_5 in all frames; only overlay crop masks change.
  if j==0:
   g.image(bg,0,0,530,1920,.25);g.image(bg,530,0,550,1920,.72);g.grade();g.text(540,890,'Ở ĐÂY',163,'bricolage',col,'middle');g.text(540,1000,'một nơi, nhiều góc nhìn',37,'sans',WHITE,'middle')
  elif j==2:
   g.image(bg,0,0,1080,950,.3);g.image(bg,0,950,1080,970,.7);g.grade();g.text(90,880,'TỔNG THỂ',102,'bricolage');g.text(950,1090,'chi tiết',128,'news',col,'end');g.line([(90,950),(950,950)],col,3)
  else:
   g.image(bg,0,0,1080,1920,.2,[(0,0),(330,0),(140,1920),(0,1920)]);g.image(bg,0,0,1080,1920,.8,[(920,0),(1080,0),(1080,1920),(730,1920)]);g.grade();g.text(540,720,'MỘT NƠI',89,'bricolage',WHITE,'middle');g.text(540,925,'nhiều câu',103,'news',col,'middle');g.text(540,1070,'chuyện.',133,'news',col,'middle')
 elif i==6:
  if j==0:
   g.text(85,560,'BẮT',260,'anton',col);g.text(85,850,'ĐẦU',260,'anton',col);g.foreground();g.text(100,1390,'một chương mới',55,'fraunces')
  elif j==2:
   g.text(80,660,'TỪNG',235,'anton',col);g.foreground();g.text(95,1130,'bước nhỏ',111,'fraunces');g.text(100,1390,'vẫn đưa bạn đi tiếp.',37,'sans',col)
  else:
   g.arc('MỘT CHƯƠNG MỚI',470,230,1000,62,'anton',col);g.foreground();g.text(85,1080,'của bạn.',116,'fraunces');g.text(90,1410,'Một chương mới, theo cách riêng.',32,'sans',col);g.curve([(90,1160),(160,1240),(390,1190),(480,1110)],col,4)
 elif i==7:
  if j==0:
   g.text(90,300,'MỘT CÁCH NHÌN VỀ',26,'mono',col);g.text(120,665,'THU',215,'anton',WHITE,rot=-10);g.text(850,1000,'CHI',180,'anton',WHITE,'end',rot=12);g.line([(180,735),(420,810),(810,1110),(450,1280)],col,4);g.text(540,1450,'CÒN LẠI',145,'anton',col,'middle',rot=-4)
  elif j==2:
   g.text(100,360,'Đặt cùng một góc nhìn',62,'anybody');g.line([(120,1240),(470,990),(950,1130),(700,1470),(120,1240)],col,3);g.text(240,1190,'THU',110,'anton',WHITE,rot=-17);g.text(580,1140,'CHI',89,'anton',col,rot=12);g.text(650,1370,'CÒN',98,'anton',WHITE,rot=12)
  else:
   g.text(145,450,'ĐỌC',50,'anton',WHITE,rot=-6);g.text(150,860,'ĐỦ',110,'anton',WHITE,rot=-10);g.text(90,1410,'DÒNG TIỀN',145,'anton',col,rot=-12);g.line([(190,990),(90,1480)],col,2);g.line([(420,990),(940,1480)],col,2)
 elif i==8:
  if j==0:
   g.text(90,300,'VÍ DỤ / USD THỰC NHẬN',26,'mono');g.text(90,580,'5,000',175,'space');g.text(470,800,'−2,000',111,'space','#FFB178','middle');g.line([(140,660),(140,900),(790,900)],col,4);g.arrow((790,900),(790,1100),col,4);g.text(950,1300,'3,000',185,'space',col,'end');g.text(950,1400,'CÒN SAU TIỀN NHÀ',29,'mono',WHITE,'end')
  elif j==2:
   g.text(540,350,'CÁC KHOẢN CHI',60,'space',WHITE,'middle')
   for x,y,n,t in [(210,650,'2,000','NHÀ Ở'),(850,860,'1,000','SINH HOẠT'),(210,1100,'500','KHÁC')]:
    g.text(x,y,n,93,'space',WHITE,'middle');g.text(x,y+70,t,29,'mono',WHITE,'middle');g.arrow((x,y+115),(540,1260),'#FFB178',3)
   g.text(540,1440,'3,500',207,'space','#FFB178','middle');g.text(540,1530,'TỔNG CHI / USD',28,'mono',WHITE,'middle')
  else:
   g.text(540,430,'5,000',178,'space',WHITE,'middle');g.text(540,520,'THỰC NHẬN',28,'mono',WHITE,'middle');g.line([(540,600),(540,800)],WHITE,5);g.line([(540,800),(220,1090)],'#FFB178',12);g.line([(540,800),(850,1090)],col,6);g.arrow((220,1090),(220,1190),'#FFB178',4);g.arrow((850,1090),(850,1190),col,4);g.text(220,1340,'3,500',109,'space','#FFB178','middle');g.text(850,1340,'1,500',109,'space',col,'middle');g.text(220,1450,'ĐÃ CHI',30,'mono',WHITE,'middle');g.text(850,1450,'CÒN LẠI',30,'mono',WHITE,'middle')
 return g

def pixel_wrap(s,font,width):
 out=[];line=''
 for w in s.split():
  t=(line+' '+w).strip()
  if font.getlength(t)>width and line:out.append(line);line=w
  else:line=t
 if line:out.append(line)
 return out

def build_assets():
 # Render all 45 frames as high-resolution JPG + editable SVG + transparent PNG overlay.
 ALL=[]
 for i,m in enumerate(META):
  for j in range(5):
   key=f'{m[0]}_F{j+1:02}';mem=io.BytesIO();c=canvas.Canvas(mem,pagesize=(1080,1920));g=draw(c,i,j);c.showPage();c.save();doc=pdfium.PdfDocument(mem.getvalue());im=doc[0].render(scale=1).to_pil();im.convert('RGB').save(P/'frames'/f'{key}.jpg',quality=94);doc.close();(P/'frames'/f'{key}.svg').write_text(g.svg())
   mem=io.BytesIO();c=canvas.Canvas(mem,pagesize=(1080,1920));og=draw(c,i,j,True);c.showPage();c.save();doc=pdfium.PdfDocument(mem.getvalue());doc[0].render(scale=1,fill_color=(0,0,0,0)).to_pil().save(P/'overlays'/f'{key}.png');doc.close();(P/'overlays'/f'{key}.svg').write_text(og.svg())
   row=COPY[i][j];cap=j in [1,3] or i==0
   motion={'in':'0.18–0.35s; vào theo thứ tự đọc, giữ một chuyển động chính.','hold':'Giữ đủ để đọc; thời gian phải căn theo VO thật.','out':'0.18–0.3s; rút về caption hoặc bố cục kế tiếp.'}
   if cap:motion={'in':'Caption vào nhẹ; từ active phóng quanh tâm, không đẩy cả dòng.','hold':'100% > 113% > 100% theo từ được đọc; cấp 1 trắng, cấp 2–3 active theo màu mẫu; viền đen ngoài 2px.','out':'Hết câu giữ một nhịp ngắn, rồi fade; không giật vị trí.'}
   if i==4 and not cap:motion['hold']='Nếu footage chuyển động, track từng điểm neo; giữ nhãn trong vùng đọc.'
   if i==6 and not cap:motion['hold']='Chữ sau người giữ lớp cố định; mask phải bám tóc/vai qua toàn shot thật.'
   if i==7 and not cap:motion['hold']='Mô phỏng phối cảnh trong storyboard; footage thật cần camera/planar tracking và kiểm tra che khuất.'
   if i==8 and not cap:motion['hold']='Lộ đầu vào trước, đường/nhánh tiếp theo, kết quả sau. Kiểm tra 2,000 + 1,000 + 500 = 3,500; 5,000 − 3,500 = 1,500.'
   ALL.append({'id':key,'layout':m[0],'level':m[1],'frame':j+1,'type':'karaoke' if cap else 'emphasis','title':row[0],'vo_proposed':row[1],'caption_lines':row[3],'description':row[2],'source_asset':f'assets/background_{m[3]}.jpg','same_source_across_layout':True,'accent':m[4],'canvas':[1080,1920],'motion':motion,'layers':g.layers,'graphic_overlay_layers':og.layers,'timing_status':'illustrative; not aligned to recorded audio'})
 (P/'storyboard_specs.json').write_text(json.dumps({'layouts':[dict(id=m[0],level=m[1],name=m[2],source=m[3],accent=m[4],fonts=m[5],principle=m[6],structure=m[7]) for m in META],'frames':ALL,'rule':'same source per layout; A/karaoke/B/karaoke/C, L01 caption only; wide creative zone is guidance, not universal platform safe-zone'},ensure_ascii=False,indent=2))
 print('Rendered 45 frames and 45 transparent overlays.')
 # Static strips for easy review and final handoff.
 for i,m in enumerate(META):
  board=Image.new('RGB',(1900,1200),PAPER);d=ImageDraw.Draw(board);fb=ImageFont.truetype(str(FONTFILES['bold']),29);fs=ImageFont.truetype(str(FONTFILES['sans']),22)
  d.text((35,20),m[0]+f' / CẤP {m[1]} / '+m[2],font=fb,fill=INK);d.text((35,70),'Cùng một source / khác cấu trúc overlay / xen karaoke nhẹ / mốc hình tĩnh',font=fs,fill=GRAY)
  for j in range(5):
   x=35+j*375;im=Image.open(P/'frames'/f'{m[0]}_F{j+1:02}.jpg');im.thumbnail((340,605));board.paste(im,(x,165));d.text((x,120),f'FRAME {j+1:02} / '+('KARAOKE' if ALL[i*5+j]['type']=='karaoke' else 'NHẤN'),font=fs,fill=INK)
   y=795
   for line in pixel_wrap(COPY[i][j][0],fb,340):d.text((x,y),line,font=fb,fill=INK);y+=39
   for line in pixel_wrap(COPY[i][j][1],fs,340):d.text((x,y+15),line,font=fs,fill=GRAY);y+=34
  d.text((35,1150),'Karaoke: trắng + viền đen mỏng / active scale 113% / cấp 2–3 dùng màu nhấn / timing cần khớp VO thật',font=fs,fill=GRAY);board.save(P/'previews'/f'{m[0]}_storyboard.jpg',quality=94)
 # Font licenses for all families actually used.
 for k,src in FONTFILES.items():
  candidates=[src.parent/(src.stem.split('-')[0]+'-OFL.txt')]
  if src.parent==T:candidates=[T/(src.stem+'-OFL.txt')]
  if k in ['sans','bold']:candidates=[A/'fonts/bevietnampro-OFL.txt']
  if k=='hand':candidates=[A/'fonts/dancingscript-OFL.txt']
  if k=='space':candidates=[A/'fonts/spacegrotesk-OFL.txt']
  for f in candidates:
   if f.exists():shutil.copy2(f,P/'fonts'/f.name);break

if __name__=='__main__':build_assets()
