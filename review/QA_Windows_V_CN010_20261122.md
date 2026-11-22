# Kiểm tra kỹ thuật video mẫu ngày 22/11/2026

Đã kiểm tra trực tiếp hai file cục bộ Windows + V và CN010 winver. Cả hai là MP4 H.264 720 × 1280, dài 58 giây, có AAC stereo. SHA Git lần lượt 841ae333406e99ab3471201dd8d0778dbabd96c9 và 086d013567c09595a9fb5d087b31c3a0c0c83781. File Windows + V trên GitHub trả SHA fd7f638b55ba52bcf09e445f591fa020e632da36. Dữ liệu MP4 do GitHub trả chưa tải được qua phiên này, vì vậy kết quả chi tiết dưới đây chỉ áp dụng cho bản cục bộ.

| Video | Hình và phụ đề | Âm thanh bản phối | Trạng thái |
|---|---|---|---|
| Windows + V | Có cảnh Windows thật cho các bước chọn chữ, bật lịch sử bảng tạm, chọn đoạn cũ và kiểm tra kết quả. Cảnh phím tắt và cảnh kết dùng minh họa có nhãn. Đọc được khoanh đỏ và mũi tên ở các khung hình lấy mẫu mỗi 4 giây. | Trung bình −19,8 dBFS, đỉnh −2,2 dBFS. | Đã kiểm thông số và khung hình mẫu. Chờ xác minh bản từ GitHub, nghe lời dẫn và tách đo lời/nhạc trước khi duyệt. |
| CN010 winver | Có màn hình Run, winver, khoảng thông tin phiên bản và OS Build, khoanh đúng vùng ở khung kiểm tra. | Trung bình −22,8 dBFS, đỉnh −3,5 dBFS. | Đã kiểm thông số và khung hình mẫu. Chờ duyệt giọng, nhạc và vùng che chữ khi phát trong ứng dụng. |

Kiểm đếm 11 video hiển thị trên hồ sơ TikTok tại thời điểm đọc. Kho Buffer cho kênh có 0 bài đã lên lịch. Chưa có bài đăng mới, chưa đóng QA toàn phần cho hai mẫu và chưa nghiệm thu lô 5, 20 hoặc 100. TikTok không cộng vào bảng 117 việc AUTO 4 KÊNH.

- [Hồ sơ TikTok](https://www.tiktok.com/@goccongnghetienich)
- [Bản Windows + V trong review](https://github.com/haidtbasaomh-blip/tiktok-cong-nghe-media/blob/main/review/WINDOWS_V_58_GIAY_QUAY_THAT_CHO_DUYET.mp4)
