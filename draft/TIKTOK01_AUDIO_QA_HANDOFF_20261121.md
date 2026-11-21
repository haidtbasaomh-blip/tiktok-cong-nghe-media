# TIKTOK 01 — REBUILD AUDIO: northern Vietnamese natural clear voice (2026-11-21)

Owner rejected previously generated TikTok video audio: **"âm thanh chán vậy à bạn? tiếng nói ko rõ ràng"**. DO NOT relabel or reupload existing eSpeak audio as improved.

## Source assets to preserve
- Video: `/mnt/data/TIKTOK_MAU_01_WINDOWS_V_LONG_TIENG_NHAC_DAY_DU.mp4` (current preview, poor eSpeak voice, NOT approved).
- Visuals: `/mnt/data/tiktok_demo_assets/visual_no_audio.mp4`; 44.7 seconds, 9:16.
- Music: `/mnt/data/TIKTOK_MAU_01_NHAC_NEN_THEO_CANH.wav`; original music with scene transitions (can improve).
- Seven voice scene files in `/mnt/data/tiktok_demo_assets/voice_{0..6}.wav` are eSpeak, MUST replace entirely.
- Timed subtitles: `/mnt/data/TIKTOK_MAU_01_LOI_DAN_GIONG_BAC.srt`.

## Narration script (Northern Vietnamese)
Scene 1 00:00.4–00:04.7: "Copy thêm một đoạn, rồi quên mất đoạn cũ? Có cách nhanh hơn!"
Scene 2 00:05.45–00:10.5: "Bấm cùng lúc hai phím Windows và V. Mẹo nằm ngay đây!"
Scene 3 00:11.4–00:17.15: "Nếu dùng lần đầu, chọn Bật để kích hoạt lịch sử bảng tạm."
Scene 4 00:18.0–00:23.75: "Giờ bạn sao chép từng đoạn bằng Control C, như bình thường."
Scene 5 00:24.5–00:30.7: "Muốn tìm lại đoạn trước, nhấn Windows V rồi chọn đúng mục cần dán."
Scene 6 00:31.55–00:37.3: "Thế là dán lại được ngay, không phải tìm và sao chép lần nữa."
Scene 7 00:38.05–00:44.25: "Lưu ý, đừng sao chép mật khẩu hoặc dữ liệu nhạy cảm. Lưu video để dùng khi cần!"

## Required deliverable (DO NOT auto-publish)
1. Natural male Hanoi/Northern Vietnamese narration, clear pronunciation of "Windows", "Control", "Clipboard", measured pacing, small deliberate pauses; test with full phone speaker playback. Avoid eSpeak, phonetically robotic voices, harsh pitch shifts or low-bitrate TTS.
2. Use a properly authorized professional Vietnamese TTS voice service if available. The public `doclen.vn/text-to-speech-tieng-viet` sample offers Northern male Khang, Bao, Quan; anonymous trial is only 200 characters per day, so DO NOT attempt to bypass caps or claim it can generate full 7-scene narration for free.
3. Music 14–20 dB below narration while speaking. Sidechain ducking with 180 ms attack, 350 ms release; gentle original licensed music in seven chapter moods; low-volume clicks/whooshes at real on-screen events only.
4. Voice EQ highpass ~85 Hz, corrective EQ for intelligibility, compression 2:1–2.5:1, mild de-ess, output -16 to -14 integrated LUFS for social, true peak <= -1 dBTP; confirm no audible clipping, pumping, wrong-word stress or slurred words.
5. Keep exact CTA, use subtitles embedded into safe TikTok zones. Actual Windows screen captures are needed for a production-ready tutorial: simulated UI must be clearly marked if it remains.
6. Verify final MP4 actual audible speech throughout, timestamps match arrows/highlights, volume balance at 25–50% phone playback, AAC 48 kHz/160–192 kbps, video H.264 1080x1920, 30 fps; supply preview link. Final file stays UNPUBLISHED until explicit editorial/audio QA.
7. Do not change existing Buffer schedule, do not delete any media or prior video.

## Status
Audio quality currently **BLOCKED** from meeting user spec by lack of connected high-quality Northern Vietnamese TTS in this Chat turn. The prior video has audio but still eSpeak and failed owner review. Do not claim 'complete' before replacing narration and listening to actual result.
