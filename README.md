# GÓC CÔNG NGHỆ TIỆN ÍCH — TikTok

Kênh: https://www.tiktok.com/@goccongnghetienich

## Hai luồng nội dung, giữ nguyên tính độc lập

1. **CN001–CN100: 100 video mẹo công nghệ** ở `media/` (bản gốc) và `media-pro/` (bản làm lại vùng chữ an toàn). Buffer và GitHub Actions sử dụng luồng công nghệ trong repository `haidtbasaomh-blip/pc-gia-tot`. CN001 được xác nhận đã đăng ngày 18/11/2026: https://www.tiktok.com/@goccongnghetienich/video/7709342773861780744. Trạng thái các bài còn lại phải kiểm chứng theo thời gian bằng chương trình `automation/tiktok/verify_posts_readonly.py`; `scheduled` **không** đồng nghĩa `sent`.
2. **MX: nội dung mới nhiều chủ đề** được quản lý ở `series/`, với các mảng: công nghệ Việt Nam và thế giới, viễn thông, đời sống xã hội, thời sự, thể thao, Tây Bắc, du lịch, ẩm thực, khoa học và khám phá. Đây là luồng **đang xây dựng, chưa tự đăng**. Không lấy nhầm các đề tài nghiên cứu hoặc kịch bản nháp làm video đã xuất bản.

## Quy trình nhiều chủ đề đã thiết lập

- `series/editorial_safety_policy.json`: chính sách nguồn, bản quyền, độ chính xác, hình ảnh và an toàn tài khoản.
- `series/multi_topic_batch01.json`: 6 kịch bản khởi đầu, chưa nghiệm thu hình ảnh.
- `series/research_feeds.json`: 9 nguồn RSS (Việt Nam và quốc tế) để tìm đề tài, **không copy bài báo hoặc tải lại video gốc**.
- `tools/discover_topics.py`, workflow `discover-tiktok-topics.yml`: tìm đề tài tự động mỗi sáng 06:45 (giờ Việt Nam); chỉ lưu metadata, thời gian và link nguồn trong GitHub Actions artifact. Lượt thử ngày 18/11 tìm được 62 đề tài, không phải 62 video.
- `tools/verify_mixed_preflight.py`, workflow `verify-tiktok-mixed.yml`: chặn xuất bản các video chưa có MP4, chưa chứng minh quyền sử dụng tư liệu, chưa kiểm tra nội dung, âm thanh, độ dài, khung dọc và tình trạng đăng trùng.
- Video thời sự nhạy cảm (cháy nổ, tai nạn, thiên tai...) phải đối chiếu ít nhất 2 nguồn độc lập, ghi đúng thời gian/địa điểm, không dựng hình giả làm tư liệu thật.

## Nguyên tắc nghiệm thu trước khi mở tự động đăng MX

1. Có MP4 9:16 ≥ 540×960, độ dài 24–35 giây, nhịp dựng, giọng đọc/âm thanh có quyền sử dụng.
2. Có hình ảnh minh họa hấp dẫn, phù hợp chủ đề, chữ quan trọng nằm vùng an toàn TikTok; không sử dụng video kiểu slide tĩnh che chữ.
3. Có kịch bản viết mới, nội dung đã xác minh, ngày sự kiện rõ, thông tin nguồn còn truy cập được.
4. Mỗi ảnh/video/nhạc bên thứ ba có giấy phép cho mục đích sử dụng, tác giả, đường dẫn, tệp kiểm tra và mã checksum; không giả mạo quyền sở hữu.
5. QA chạy thành công với tình trạng `publish_ready=true`; tránh trùng clip, trùng bài và không vượt quá mục tiêu **2 video/ngày tổng cộng** (CN + MX), khi có kế hoạch chuyển lịch.
6. Không thể cam kết an toàn tài khoản tuyệt đối 100%: TikTok có quyền xử lý theo quy định nền tảng. Nếu rủi ro không rõ, hệ thống phải dừng đăng clip đó.

**Không tự đăng tin chưa đủ kiểm chứng; không thay đổi các lịch CN đã có chỉ để tăng số lượng MX.**
