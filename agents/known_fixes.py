"""Hardcoded patches for FakeAgent. Single source of truth so toy tasks
only need one place updated when a new task is added. Not used by any
agent that doesn't cheat via memorized fixes (e.g. DumbAgent).
"""

KNOWN_FIXES = {
    "toy_001": {
        "file": "toy_calc/ops.py",
        "find": "return price - (price * percent)",
        "replace": "return price - (price * (percent / 100))",
    },
    "toy_002": {
        "file": "toy_calc/ops.py",
        "find": "for i in range (start, end):",
        "replace": "for i in range (start, end+1):",
    },
}
