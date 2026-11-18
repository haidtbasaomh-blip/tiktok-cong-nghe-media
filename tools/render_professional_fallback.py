#!/usr/bin/env python3
"""Portable FFmpeg fallback for two stalled GitHub Actions video batches.

Uses imageio-ffmpeg's bundled Linux executable, no apt/dpkg or server setup.
The exact same safe-area renderer and the same source manifest are reused.
"""
from __future__ import annotations
import json
import os
import runpy
import subprocess
import tempfile
from pathlib import Path
import imageio_ffmpeg

def main():
    normal_check = subprocess.check_output
    with tempfile.TemporaryDirectory(prefix="tiktok-ffmpeg-") as temporary:
        ffmpeg = Path(temporary) / "ffmpeg"
        ffmpeg.symlink_to(imageio_ffmpeg.get_ffmpeg_exe())
        os.environ["PATH"] = str(temporary) + os.pathsep + os.environ.get("PATH", "")

        def ffprobe_equivalent(args, *extra, **kwargs):
            if args and Path(args[0]).name == "ffprobe":
                path = str(args[-1])
                reader = imageio_ffmpeg.read_frames(path)
                try:
                    metadata = next(reader)
                finally:
                    reader.close()
                size = metadata.get("size")
                fps = metadata.get("fps")
                duration = metadata.get("duration")
                if not size or fps is None or duration is None:
                    raise RuntimeError("Missing MP4 validation metadata")
                return json.dumps({
                    "streams": [{"width": size[0], "height": size[1], "r_frame_rate": f"{round(fps)}/1"}],
                    "format": {"duration": duration, "size": Path(path).stat().st_size}
                }).encode()
            return normal_check(args, *extra, **kwargs)

        subprocess.check_output = ffprobe_equivalent
        runpy.run_path("tools/render_professional_tiktok.py", run_name="__main__")

if __name__ == "__main__":
    main()
