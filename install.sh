#!/usr/bin/env bash
set -e
# Install dtk to /usr/local/bin (zero-dependency, stdlib-only)
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/dtk.py"
DST="/usr/local/bin/dtk"
sudo -S -p '' cp "$SRC" "$DST"
sudo -S -p '' chmod +x "$DST"
echo "✓ dtk installed to $DST — try: dtk doctor"
