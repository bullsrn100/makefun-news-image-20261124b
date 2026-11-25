#!/usr/bin/env python3
"""Copy the 24 November 2026 news image to the output directory.

The image (entry.png, kept beside this script) is delivered byte-for-byte:
it is read once, staged under a temporary name, verified, and only then
moved into place, so a partial or corrupted write can never pose as the
entry. Standard library only, no network, deterministic.
"""

import hashlib
import os
import sys

SOURCE_NAME = "entry.png"
OUTPUT_NAME = "entry.png"
CHUNK = 65536


def source_path():
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(here, SOURCE_NAME)


def output_dir():
    return os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")


def sha256_of(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        while True:
            block = handle.read(CHUNK)
            if not block:
                break
            digest.update(block)
    return digest.hexdigest()


PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def copy_verified(src, dst):
    """Copy src to dst via a staging file, verifying bytes before the move."""
    staging = dst + ".staging"
    if os.path.exists(staging):
        os.remove(staging)
    with open(src, "rb") as probe:
        if probe.read(len(PNG_MAGIC)) != PNG_MAGIC:
            raise SystemExit("source is not a PNG file")
    total = 0
    with open(src, "rb") as reader, open(staging, "wb") as writer:
        while True:
            block = reader.read(CHUNK)
            if not block:
                break
            writer.write(block)
            total += len(block)
    if sha256_of(staging) != sha256_of(src):
        os.remove(staging)
        raise SystemExit("staging copy failed verification")
    os.replace(staging, dst)
    if sha256_of(dst) != sha256_of(src):
        raise SystemExit("delivered file failed verification")
    return total


def main():
    src = source_path()
    out = output_dir()
    os.makedirs(out, exist_ok=True)
    dst = os.path.join(out, OUTPUT_NAME)
    size = copy_verified(src, dst)
    digest = sha256_of(dst)
    print(f"wrote {dst}: {size} bytes, sha256 {digest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
