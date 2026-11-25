# GÓC CÔNG NGHỆ TIỆN ÍCH — Review 2 video giọng Bắc, 25/11/2026

**Không phải giấy duyệt đăng.** Giữ nguyên danh sách approved và video cũ.

| Bản MP4 | Thời lượng / codec | Âm lượng | SHA-256 |
|---|---|---|---|
| [Windows + V](WINDOWS_V_58_GIAY_QUAY_THAT_CHO_DUYET.mp4) | 58 giây; 720×1280; H.264/AAC stereo | −16,97 LUFS; −2,21 dBTP | `0d51da672891a48830250c6668016a2515bbd1bc39b9cf73b079fa997bbd778a` |
| [CN010 — winver](batch-01/CN010_WINVER_58_GIAY_CHO_DUYET.mp4) | 58 giây; 720×1280; H.264/AAC stereo | −19,36 LUFS; −3,49 dBTP | `c5092b14392d7f4d04f5552afbb528b082e8d7eb0108ab4e29d6699844c35d41` |

Bằng chứng kiểm tra đúng tệp GitHub: https://github.com/haidtbasaomh-blip/tiktok-cong-nghe-media/actions/runs/45427429365 (11 tệp nguồn cũ không có audio track; 2 mẫu có audio, giải mã đạt). Không suy diễn từ đo âm lượng sang chất lượng giọng hoặc lời/nhạc tách riêng. Windows + V có cùng audio packet với bản nguồn Anh Khôi đã rà; CN010 tài liệu dựng ghi Anh Khôi, chưa đối chiếu độc lập packet với nguồn giọng. Tài liệu quyền giọng preset: https://huggingface.co/pnnbao-ump/VieNeu-TTS-v3-Turbo. Cần xác minh quyền nhạc nền của đúng bản xuất cuối.

Kiểm tra Buffer 25/11: https://github.com/haidtbasaomh-blip/pc-gia-tot/actions/runs/45516078923 — 11 sent, 4 draft, 0 scheduled. CN010 đã có bản cũ đăng; chỉ được đưa bản sửa lên lịch nếu chính sách chống trùng cho phép và có phê duyệt rõ ràng.

## Còn thiếu trước khi đăng
- Nghe hết 2 MP4; kiểm tra giọng tự nhiên, phát âm, nhạc không lấn lời, âm thanh liên tục.
- Kiểm tra phụ đề/vùng che trên màn hình TikTok, đúng thao tác và mũi tên.
- Xác minh nhạc nền và quyền thương mại, đối chiếu SHA của đúng tệp được duyệt.
- Chủ kênh duyệt cụ thể bản nào; không tự gán sign-off. Không đăng lặp CN010 hoặc tự đổi trạng thái Buffer.
