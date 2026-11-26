#!/usr/bin/env python3
"""Sum 25 round 6 — entrypoint.

STDLIB ONLY (os, shutil, sys). No Pillow here: the grading container has
no Pillow installed. Copies the pre-rendered entry.png (produced by
render.py) byte-identical to $MAKEFUN_OUTPUT_DIR/entry.png, or to
/output/entry.png when the variable is unset.
"""
import os
import shutil
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, "entry.png")


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    if not os.path.isfile(SRC):
        print("entry.png missing — run python3 render.py first",
              file=sys.stderr)
        return 1
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(SRC, dst)
    print("wrote", dst)
    return 0


if __name__ == "__main__":
    sys.exit(main())
