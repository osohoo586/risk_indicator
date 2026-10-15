#!/usr/bin/env python3
"""Risk indicator runner.  Тусламж:  python ri.py -h"""
import sys

from ri_runner.cli import main

if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):          # Windows консол / pipe: монгол текст cp1252-д алдаа өгөхгүй
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
