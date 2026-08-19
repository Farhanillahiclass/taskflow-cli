#!/usr/bin/env python3
"""
Convenience launcher so the app can be run as `python run.py` from the
project root without needing to fiddle with PYTHONPATH.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from taskflow.main import main  # noqa: E402

if __name__ == "__main__":
    main()
