# KẾ HOẠCH NỘI DUNG TIKTOK + AI AGENT / GOOGLE FLOW
**Ngày:** 21/11/2026.
**Kế hoạch tổng thể từ 08/11/2026 cho 5 kênh:** https://github.com/haidtbasaomh-blip/pc-gia-tot/blob/main/plans/KE_HOACH_TONG_HOP_AI_AGENT_FLOW_5_KENH_TU_08_11_2026.md

Đây là bản lưu ý tưởng và nguyên tắc sản xuất; không phải trạng thái “đã đăng”. Không tự đẩy bản xem trước lên TikTok.

## Kênh và kỳ vọng từ người dùng
Kênh: https://www.tiktok.com/@goccongnghetienich

- Không chỉ thủ thuật máy tính: tin mới về AI, robot, vũ trụ, công nghệ, xe, triển lãm CES/MWC/Computex/IFA, văn hóa, nghệ thuật, thể thao, tin Việt Nam/thế giới, thiên nhiên, du lịch/Tây Bắc và ẩm thực.
- Học hook, kỹ thuật kể chuyện, chuyển cảnh, retention từ kênh lớn, nhưng dựng nội dung, hình ảnh, lời dẫn, nhạc gốc hoặc có quyền; không xóa watermark để sao chép.
- Video ban đầu 12–17 giây nền xanh và ít bước bị chủ kênh đánh giá chất lượng kém; chuẩn mới 50–90 giây, ưu tiên 55–60 giây, nhiều cảnh đẹp, nội dung thật.
- Với thủ thuật: quay Windows/điện thoại thật, khoanh đỏ/mũi tên trỏ chính xác nút bấm, zoom, cursor và kết quả thật; màn hình mô phỏng phải dán nhãn.
- Tiếng nam Việt chuẩn Bắc tự nhiên như người thật, âm lượng rõ, nhạc nền giảm khi có lời, SFX theo đúng cảnh; không sử dụng eSpeak khó nghe.
- Mục tiêu 3–5 video/ngày khi kiểm duyệt/bản quyền và tài khoản cho phép; **25 đề tài nghiên cứu/ngày không đồng nghĩa 25 video MP4/ngày**. Không tự bật đăng hàng loạt.

## Bằng chứng/kho đã có và tình trạng
- Kho CN001–CN100 thủ thuật, và storyboard kế hoạch kéo dài mỗi video: series/CN001-CN100_63s_RED_HIGHLIGHT_STORYBOARDS.json. Đây là kịch bản, không phải 100 video mới đã nghiệm thu.
- Chính sách âm thanh, nguồn tin, bản quyền, đăng trùng: series/editorial_safety_policy.json.
- Công cụ tìm tin mới đa chủ đề và 18 nguồn RSS: tools/discover_topics.py, tools/daily_idea_lab.py, series/research_feeds.json. Kết quả là đề tài cần kiểm chứng, không phải bản tin viral thực.
- Có clip gốc/NASA và photo essay mang tính mẫu; kiểm tra giấy phép từng tài sản khi dùng.
- Mẫu Windows + V có cả bản minh họa và bản có một đoạn quay Windows 11 thật trong review/WINDOWS_V_58_GIAY_QUAY_THAT_CHO_DUYET.mp4; tài liệu đi kèm ghi CHỜ DUYỆT. Không gọi bản này là đã đăng/đã hoàn thành kho 100.
- Luồng Buffer TikTok trong repo PC GIÁ TỐT có cổng chất lượng và trạng thái HOLD cho video mới chưa duyệt; không thay hàng đợi cũ nếu chưa xác minh.

## Các agent cần thử, không tự xuất bản
1. **Trend Research:** tìm tin 24–48h theo nguồn, có ngày, 2 nguồn với tin nhạy cảm; học xu hướng nhưng không khẳng định view chưa kiểm chứng.
2. **Script Editor:** câu chuyện riêng có hook 2 giây đầu, bối cảnh, diễn giải, kết quả và CTA phù hợp.
3. **Copyright/Safety:** giấy phép footage/music/voice, bản quyền/attribution, cảnh AI gắn nhãn khi cần; tránh làm giả hình hiện trường.
4. **Shot/Storyboard:** cảnh quay thật được phép, 3 thang cảnh, hình bôi đỏ và mũi tên đúng tọa độ thao tác; không slideshow chữ.
5. **Northern Narration:** giọng nam Bắc rõ, bản thử trước -> nghe phê duyệt -> mới ghép MP4; không tự ghi AI voice thành người thật.
6. **Sound/Mix:** nhạc gốc có quyền, tự giảm ít nhất khoảng 12 dB khi giọng nói, hiệu ứng đúng thao tác, kiểm tra bằng loa điện thoại.
7. **Video QA:** 9:16, 50–90s, cảnh thật/ảnh thật, phụ đề vùng an toàn, kết quả có chứng cứ, actual audio/video tracks.
8. **Publisher Guard:** check approved, link public, content hash, Buffer queue và TikTok Sent; đăng không quá lịch/quota.
9. **Feedback:** theo dõi 3 giây đầu, trung bình thời gian xem, completion rate, saves, shares, follower thật; chỉ nhận số có nguồn.

## Google Flow phù hợp ở đâu
- Có thể dùng miễn phí theo credits hiện có để thử **1 cảnh AI/robot/vũ trụ hoặc transition mở video** (được phép và minh bạch).
- Không dùng Flow thay ảnh quay bàn phím/giao diện đúng nút, footage hiện trường hoặc quán/thiết bị có thật.
- Không cam kết Google Flow miễn phí sản xuất 3–5 clip dài gần 1 phút mỗi ngày; Veo API chính thức không có free tier tại tài liệu Google.
- Kết quả thử nghiệm phải được duyệt hình/giọng/điều khoản trước khi đưa vào video chính thức.
- Nguồn: https://support.google.com/flow/answer/16526234 và https://ai.google.dev/gemini-api/docs/pricing/.

## Ưu tiên và nghiệm thu
P0 một video 55–60s quay thật + giọng Bắc rõ nghe duyệt -> P1 5 video tốt và đo phản hồi -> P2 20 video đã QA -> P3 làm lại 100 video; song song xây series tin nóng/công nghệ/văn hóa có nguồn; sau đó mới tăng lên 3–5/ngày khi đạt chất lượng.

**Tệp chỉ lưu kế hoạch, không gọi API đăng, không chi tiền và không làm thay đổi video đã đăng.**
