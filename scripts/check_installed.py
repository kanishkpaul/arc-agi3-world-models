"""Smoke-test the installed wheel, with the source checkout excluded."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

checkout = Path(sys.argv[1]).resolve()
for name in ('arc3_substrate.perception.scene', 'arc3_substrate.logging_.logger', 'arc3_substrate.verify.replay'):
    module = importlib.import_module(name)
    installed_path = Path(module.__file__).resolve()
    if installed_path.is_relative_to(checkout):
        raise RuntimeError(f'{name} was loaded from the source checkout')
    print(f'{name}: installed wheel import passed')
