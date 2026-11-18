#!/usr/bin/env python3
"""Entry program for make.fun's news-image-20261118.

The contest asks for one image that sums up the world news of Wednesday
18 November 2026. The image lives beside this file as entry.png (drawn by
draw.py from the day's verified headlines) and this program copies it to
the grader's output directory as entry.png.

The grader runs the program twice with no network, a read-only /bot and a
writable /output, so the copy must be byte-for-byte deterministic: the
source bytes are read once, checked against the contest's own limits
(a whole PNG of at most 1 MiB and at most 1024 by 1024 pixels), written
out, and read back to prove both runs land on the same file.

Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output:
    mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import os
import struct
import sys
from pathlib import Path

MAX_BYTES = 1_048_576  # 1 MiB, the contest's size limit
MAX_SIDE = 1024        # the contest's pixel limit
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def read_source() -> bytes:
    """Return the entry image's bytes, from beside this program."""
    source = Path(__file__).resolve().parent / "entry.png"
    return source.read_bytes()


def check_image(data: bytes) -> None:
    """Refuse anything the contest gate would refuse.

    The gate tells PNG and JPEG apart by their first bytes and checks the
    size and pixel limits; this entry is a PNG, so its IHDR is checked
    for the width and height the header promises.
    """
    if len(data) > MAX_BYTES:
        raise ValueError(f"entry image is {len(data)} bytes, over 1 MiB")
    if not data.startswith(PNG_SIGNATURE):
        raise ValueError("entry image is not a PNG")
    # IHDR is the first chunk: 8 signature bytes, then length, type, data.
    width, height = struct.unpack(">II", data[16:24])
    if width > MAX_SIDE or height > MAX_SIDE:
        raise ValueError(f"entry image is {width}x{height}, over 1024 px")


def main() -> int:
    data = read_source()
    check_image(data)
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / "entry.png"
    target.write_bytes(data)
    if target.read_bytes() != data:
        raise IOError("written entry.png does not match the source bytes")
    print(f"wrote {target} ({len(data)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
