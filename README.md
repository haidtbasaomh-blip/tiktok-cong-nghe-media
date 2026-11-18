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
5. QA chạy thành công với tình trạng `publish_ready=true`; tránh trùng clip, trùng bài và không vượt mức đang cấu hình **3 video/ngày tổng cộng** trên toàn kênh (CN + MX); trần cứng hiện tại là 5 và chỉ nâng sau nghiệm thu.
6. Không thể cam kết an toàn tài khoản tuyệt đối 100%: TikTok có quyền xử lý theo quy định nền tảng. Nếu rủi ro không rõ, hệ thống phải dừng đăng clip đó.

**Không tự đăng tin chưa đủ kiểm chứng; không thay đổi các lịch CN đã có chỉ để tăng số lượng MX.**

## Nghiên cứu sáng tạo hằng ngày và công cụ miễn phí (18/11/2026)

- `tools/daily_idea_lab.py` và `discover-tiktok-topics.yml`: mỗi sáng thu thập bài nguồn, chọn **tối đa 5 ý tưởng** độc lập với 5 kiểu dẫn chuyện; tin nguy cơ cao được tách riêng để xét duyệt. Đầu ra dạng artifact, **không phải video**.
- `series/global_tiktok_youtube_creator_inspiration.json`: tham khảo cách kể từ 16 nhà sáng tạo lớn. **Chưa tự đo được lượt xem thực tế trên TikTok/YouTube**.
- `series/quy_trinh_hoc_video_nhieu_view_moi_ngay.md`: quy tắc học–thử–đo–cải tiến dựa trên số liệu sau khi video đã công khai.
- `tools/creator_toolchain_audit.py` và workflow `tiktok-free-creator-tools.yml`: FFmpeg, ffprobe, PySceneDetect, Pillow, Auto-Editor miễn phí; kiểm tra phim lưu kho và tạo contact sheet qua GitHub Actions. Công cụ không cấp phép bản quyền cho video.
- `tools/trim_owned_video.py`: chỉ cắt video tự quay hoặc có phép kèm ledger; mặc định `series/approved_raw_footage.json` trống và **không có nguồn nào được tự động cho phép**.
- Kiểm tra bước đầu thấy 6 video MX cũ mỗi video chỉ có 1 cảnh chính, nên **vẫn chưa duyệt đăng**; cần hình chuyển động thực và âm thanh/lời dẫn tốt hơn.
