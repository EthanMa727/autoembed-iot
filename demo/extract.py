"""Pull a pure C/C++ sketch out of an LLM reply (spec 3.1).

Strips ``` fences and any leading prose. Deliberately dumb.
"""
import re


def extract_sketch(reply):
    text = reply.strip()
    fence = re.search(r"```(?:[a-zA-Z+]*)\n(.*?)```", text, re.DOTALL)
    if fence:  # take the content of the first fenced block
        text = fence.group(1).strip()
    else:  # strip stray leading/trailing fence lines, if any
        text = re.sub(r"^```[a-zA-Z+]*\s*", "", text)
        text = re.sub(r"\s*```$", "", text).strip()
    # If a prose preamble remains, slice from the first real C/C++ token.
    m = re.search(r"#include|void\s+setup", text)
    if m and m.start() > 0:
        text = text[m.start():]
    return text.strip() + "\n"
