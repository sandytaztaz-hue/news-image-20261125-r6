#!/usr/bin/env python3
"""Sum 25 round 6 entry point (stdlib only).

Copies entry.png byte-identical to $MAKEFUN_OUTPUT_DIR if set,
else /output/entry.png. Deterministic: no timestamps, no network.
"""
import os
import shutil
import sys


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(src, dst)
    return 0


if __name__ == "__main__":
    sys.exit(main())
