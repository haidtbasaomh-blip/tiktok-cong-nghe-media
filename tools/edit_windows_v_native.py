"""Replace two Windows + V illustrations with verified, chronological Windows captures."""
import argparse
from pathlib import Path
import subprocess

from PIL import Image, ImageDraw, ImageFont, ImageStat, ImageChops

WIDTH, HEIGHT, FPS = 720, 1280, 30
RED = "#F73149"
FONT_FILE = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(size):
    return ImageFont.truetype(FONT_FILE, size)


def slide(screenshot, crop, highlight, result=False):
    canvas = Image.new("RGB", (WIDTH, HEIGHT), "#101930")
    draw = ImageDraw.Draw(canvas)
    accent = "#82e2d0" if result else "#ffd890"
    draw.ellipse((420, -640, 1540, 355), fill="#1d3459")
    draw.polygon([(0, 935), (720, 1090), (720, 1280), (0, 1280)], fill="#1b2e52")
    draw.text((60, 131), "GÓC CÔNG NGHỆ TIỆN ÍCH", font=font(22), fill=accent)
    title = "Đã dán đúng đoạn cũ" if result else "Chọn lại đoạn cũ"
    draw.text((57, 216), title, font=font(42), fill="#f4f9ff")
    left, top, right, bottom = crop
    box = screenshot.crop(crop)
    scale = min(550 / box.width, 494 / box.height)
    box = box.resize((round(box.width * scale), round(box.height * scale)), Image.Resampling.LANCZOS)
    x, y = (655 - box.width) // 2, 300 + (510 - box.height) // 2
    draw.rounded_rectangle((x-5, y-5, x+box.width+5, y+box.height+5), 12, fill="#647ca9")
    canvas.paste(box, (x, y))
    if highlight:
        a, b, c, d = highlight
        a, b, c, d = x+(a-left)*scale, y+(b-top)*scale, x+(c-left)*scale, y+(d-top)*scale
        draw.rounded_rectangle((a,b,c,d), 9, outline=RED, width=7)
        middle = (b+d)/2
        draw.line((c+37,middle-22,c+4,middle), fill=RED, width=6)
        draw.polygon([(c+4,middle),(c+22,middle-1),(c+13,middle-14)], fill=RED)
    draw.text((62, 830), "QUAY MÀN HÌNH WINDOWS 11", font=font(18), fill="#bbccec")
    draw.rounded_rectangle((58, 876, 606, 963), 17, fill="#283b60")
    lines = ("Dòng cũ xuất hiện", "ở ngay vị trí con trỏ.") if result else (
        "Windows + V để mở lịch sử", "Chọn dòng được khoanh đỏ.")
    for row, line in enumerate(lines):
        draw.text((77, 888+31*row), line, font=font(24), fill="#f4f9ff")
    draw.rounded_rectangle((60,983,607,992),4,fill="#40547c")
    draw.rounded_rectangle((60,983,537 if result else 470,992),4,fill=accent)
    return canvas


def image_distance(a, b, crop):
    a = a.crop(crop).convert("L").resize((96, 88))
    b = b.crop(crop).convert("L").resize((96, 88))
    return ImageStat.Stat(ImageChops.difference(a, b)).mean[0]


def edit(source, capture, output, panel_crop, item, result_crop, line):
    files = sorted(capture.glob("native-*.png"))
    if len(files) < 14:
        raise ValueError("The capture needs a verified sequence of Windows screenshots.")
    images = [Image.open(path).convert("RGB") for path in files]
    popup = Image.open(capture/"demo-06-history.png").convert("RGB")
    result = Image.open(capture/"demo-07-result.png").convert("RGB")
    scores = [(image_distance(f, popup, panel_crop), image_distance(f, result, panel_crop)) for f in images]
    history_start = next(i for i, (a,b) in enumerate(scores) if a < b and a < 10)
    result_start = next(i for i,(a,b) in enumerate(scores) if i > history_start+2 and b < a and b < 8)
    history_frames = [slide(f,panel_crop,item if i >= history_start else None) for i, f in enumerate(images[:result_start])]
    result_frames = [slide(f,result_crop,line,True) for f in images[result_start:]]
    result_still = slide(result,result_crop,line,True)
    clip = output.parent / "native-scenes.mp4"
    encode = subprocess.Popen([
        "ffmpeg","-v","error","-y","-f","rawvideo","-pixel_format","rgb24","-video_size","720x1280",
        "-framerate","30","-i","pipe:0","-c:v","libx264","-crf","18","-preset","fast","-pix_fmt","yuv420p",
        "-threads","4",str(clip)
    ],stdin=subprocess.PIPE)
    with encode.stdin as pipe:
        # Hold the real pop-up under the narration and retain the recorded click at the cut.
        parts = history_frames[:history_start] + [history_frames[history_start]] * 18 + history_frames[history_start:]
        for i in range(round(7.5*FPS)):
            idx = min(len(parts)-1,int(i*len(parts)/(7.5*FPS)))
            pipe.write(parts[idx].tobytes())
        for i in range(7*FPS):
            idx = min(len(result_frames),i//5)
            frame = result_frames[idx] if idx < len(result_frames) else result_still
            pipe.write(frame.tobytes())
    if encode.wait():
        raise RuntimeError("Could not encode the native footage")
    filters = "[0:v]trim=end_frame=1050,setpts=PTS-STARTPTS[a];[1:v]setpts=PTS-STARTPTS[b];[0:v]trim=start_frame=1485,setpts=PTS-STARTPTS[c];[a][b][c]concat=n=3:v=1:a=0[v]"
    subprocess.run([
        "ffmpeg","-v","error","-y","-i",str(source),"-i",str(clip),"-filter_complex",filters,
        "-map","[v]","-map","0:a:0","-c:v","libx264","-crf","19","-preset","fast","-threads","4",
        "-pix_fmt","yuv420p","-c:a","copy","-movflags","+faststart","-t","58",str(output)
    ],check=True)
    print(f"Windows panel visible at capture frame {history_start}; pasted result starts at {result_start}.")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    for name in ("source", "capture", "output"):
        p.add_argument(name, type=Path)
    for name in ("panel-crop", "item", "result-crop", "line"):
        p.add_argument("--" + name, type=int, nargs=4, required=True)
    edit(**vars(p.parse_args()))
