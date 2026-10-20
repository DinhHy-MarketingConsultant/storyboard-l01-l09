# Storyboard L01–L09 / 45 frame

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

## Motion layout trong bản xem
Bấm Bật motion layout để xem 24 frame nhấn của L02–L09. Có tạm dừng, phát lại, thanh kéo 0–6 giây, tốc độ 0.5×/1×/1.5× và lặp. Mở lớn từng frame để xem chuyển động. L01 giữ karaoke; karaoke dùng điều khiển độc lập. Các hiệu ứng mô phỏng trong trình duyệt, chưa phải preset motion native.
