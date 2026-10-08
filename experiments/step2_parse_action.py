"""Step 2 of building LLMAgent: parse a bash-action block out of LM text.

Throwaway script, no API calls needed -- this is pure regex, testable
in isolation before it ever touches a real model response.
Run manually: python experiments/step2_parse_action.py
"""

import re


class FormatError(RuntimeError):
    """Raised when the LM output doesn't contain exactly one action block."""


INCORRECT_FORMAT_MESSAGE = """Your output was malformatted.
Please include exactly 1 action formatted as in the following example:
```bash-action
ls -R
```
"""


def parse_action(lm_output: str) -> str:
    """Extract the command inside a ```bash-action ... ``` block.

    Raises FormatError if there isn't exactly one such block.
    """
    matches = re.findall(r"```bash-action\s*\n(.*?)\n```", lm_output, re.DOTALL)
    if len(matches) != 1:
        raise FormatError(INCORRECT_FORMAT_MESSAGE)
    return matches[0].strip()


if __name__ == "__main__":
    # Happy path: exactly one action block.
    happy = """I'll list the files first.
```bash-action
ls -R
```
"""
    print("happy path ->", repr(parse_action(happy)))
    assert parse_action(happy) == "ls -R"

    # No action block at all.
    try:
        parse_action("I think the fix is to change line 5.")
        print("FAILED: should have raised FormatError")
    except FormatError:
        print("no-action-block -> correctly raised FormatError")

    # Two action blocks -- ambiguous, should also fail.
    two_blocks = """First:
```bash-action
ls
```
Then:
```bash-action
cat ops.py
```
"""
    try:
        parse_action(two_blocks)
        print("FAILED: should have raised FormatError")
    except FormatError:
        print("two-action-blocks -> correctly raised FormatError")

    # Multi-line command inside one block.
    multiline = """```bash-action
cd toy_calc && \\
cat ops.py
```
"""
    print("multiline ->", repr(parse_action(multiline)))

    print("\nAll step 2 checks passed.")
