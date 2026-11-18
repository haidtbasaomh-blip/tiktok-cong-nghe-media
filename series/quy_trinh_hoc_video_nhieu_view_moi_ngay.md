# CHU TRÌNH HỌC TỪ VIDEO NHIỀU NGƯỜI XEM — TIKTOK GÓC CÔNG NGHỆ TIỆN ÍCH

**Ngày áp dụng:** 18/11/2026. **Mục tiêu:** sáng tạo video có thể thu hút người xem theo cách chính đáng, không sao chép hình, lời, âm thanh, kịch bản của bên khác.

## 1. Nghiên cứu phải có hai luồng khác nhau

- **Luồng A — xu hướng thật từ nền tảng video:** Theo dõi bảng xếp hạng và ví dụ video nổi bật tại [TikTok Creative Center VN](https://ads.tiktok.com/creative/creativeCenter/trends?region=VN), [YouTube Charts](https://charts.youtube.com/) và các tài khoản tiêu biểu đã lưu ở `series/global_tiktok_youtube_creator_inspiration.json`. Chỉ ghi lại **thông điệp, nhịp dựng, kiểu mở đầu, cấu trúc kể chuyện**. Nếu muốn nói video có nhiều lượt xem phải lưu URL, view hiển thị và **thời điểm kiểm chứng**. Một bảng xếp hạng âm nhạc không đại diện toàn bộ TikTok.
- **Luồng B — đề tài mới có nguồn tin:** Tự thu thập tiêu đề, ngày tháng và URL từ các RSS tin chính thống ở `series/research_feeds.json`. Tin hoặc đề tài đang được báo chí đề cập **chưa chứng minh** là video viral. Hệ thống chấm điểm tiềm năng biên tập, không chấm lượt xem TikTok/YouTube.

**Hiện thực tế:** Luồng B và danh mục phương pháp từ 16 nhà sáng tạo đã vận hành trên GitHub. Luồng A **chưa kết nối API đo view video hàng ngày** nên không được khẳng định đã tự chọn video nhiều view theo số liệu hàng ngày.

## 2. Quy trình lặp có đo lường, không lặp video

1. **06:45 hằng ngày:** GitHub đọc 9 RSS; bỏ URL lỗi, loại trùng, phân nhóm chủ đề.
2. **Chọn tối đa 5 ý tưởng:** có URL gốc, phân tán giữa công nghệ, thế giới, khoa học, thể thao, đời sống/du lịch. Tin cháy nổ, thiệt mạng, chiến tranh… đưa vào **hàng chờ kiểm tra riêng**, không mặc định làm chủ đề đăng tự động.
3. **Học 1 cơ chế sáng tạo chung từ nhóm creator:** ví dụ một câu hỏi tò mò, thí nghiệm, trước/sau có bằng chứng, địa điểm có câu chuyện, sơ đồ giải thích; không bắt chước cảnh quay/hình thức nhận diện đặc trưng.
4. **Viết kịch bản mới và dựng độc lập:** hình tự tạo hoặc clip thực được phép; lời bình tự viết; kiểm tra sự thật, quyền thương mại và đạo đức với người xuất hiện trong video.
5. **Kiểm thử trước đăng:** 2–3 cách mở đầu chỉ thử **nội bộ**, chọn bản tốt nhất; không đăng nhiều video gần giống nhau chỉ để A/B.
6. **Sau khi đăng công khai:** chỉ so sánh bằng TikTok Analytics thực tế (nếu kết nối được): lượt xem 24h/72h, thời gian xem, tỉ lệ xem hết, chia sẻ, lưu và follower tăng từ video.
7. **Lặp lại điều đã hiệu quả, không sao chép video:** điều chỉnh nhịp kể, độ dài, khung mở, hình ảnh, âm thanh với đề tài hoàn toàn mới; nếu hiệu quả kém thì giảm số lượng, nâng chất lượng.

## 3. Mỗi ngày áp dụng ý tưởng gì?

| Cách kể thành công có thể học | Video gốc đề xuất cho kênh |
|---|---|
| Câu hỏi lạ ở 2 giây đầu | Một hiểu lầm công nghệ được giải bằng mô phỏng tự dựng |
| Quá trình với kết quả đáng chờ | Một phép thử mẹo PC có đầu vào, thao tác và kết quả thật |
| Ngắn nhưng có cảm xúc | Một nghề truyền thống được giải thích qua video được phép sử dụng |
| Sự thật bất ngờ nhưng có nguồn | Một hiện tượng khoa học/vũ trụ được minh họa đúng ngày, đúng nguồn |
| Phân tích đơn giản điều phức tạp | Bản đồ và sơ đồ tự dựng giải thích một tin đã kiểm chứng |
| Cận cảnh đời sống chân thực | Quy trình nấu món ăn với clip chủ sở hữu cho phép hoặc stock có phép |

Không lấy những video người khác có view cao về rồi dùng xóa nền, đổi tiếng, cắt logo, xoay hình để đăng lại.

## 4. Nghiệm thu bằng bằng chứng

**Mỗi ngày** lưu `series/daily_ideas_latest.json`, `series/daily_ideas_latest.md` trong GitHub Actions artifact của workflow `discover-tiktok-topics.yml`. Đây là **bản nháp ý tưởng**, không phải danh sách video đã làm. Báo cáo phải ghi rõ ngày, số nguồn đã xử lý, số ý tưởng, trạng thái nguồn, nguồn thông tin chưa được xác minh.

**Mỗi tuần** kiểm thử dựng bằng `tiktok-free-creator-tools.yml`: FFmpeg/ffprobe + PySceneDetect + Pillow + Auto-Editor (chỉ chạy cắt đối với tư liệu đã được xác minh quyền). Video có ít cảnh hoặc âm thanh máy móc phải qua khâu sửa; không suy từ kiểm tra kỹ thuật rằng có quyền dùng ảnh hay nội dung đã hấp dẫn.

**Sau khi đăng** mới được cập nhật bảng hiệu quả: URL TikTok công khai, view có thời điểm kiểm tra, tỷ lệ giữ chân, lượt lưu/chia sẻ và follower tăng; không mua view/follow và không coi GitHub success là TikTok success.

## 5. Rào chắn trung thực

- Không có dữ liệu lượt xem thực tế của 16 kênh từ tài khoản này; không tự gọi một ý tưởng là “đã chứng minh viral”.
- Việc xem nhiều video không thay thế kiểm duyệt bản quyền và nội dung do TikTok quy định.
- Không có công cụ bảo đảm 1 triệu follower hay bảo đảm không bị giảm phân phối.
- Không bật 25 bài/ngày tự động khi chưa chứng minh nội dung đủ khác biệt, an toàn và thành công.
- **Chưa có chức năng tự tạo video hoàn chỉnh từ 5 ý tưởng RSS và tự đăng mỗi ngày.** Muốn triển khai phải qua kiểm tra kịch bản, giấy phép, âm thanh và nghiệm thu hình ảnh.
