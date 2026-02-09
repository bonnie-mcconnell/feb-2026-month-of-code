from __future__ import annotations

import json
from typing import List, Dict


def format_text_thread(posts: List[str]) -> str:
    lines: list[str] = []
    total = len(posts)

    lines.append(f"Thread ({total} posts)\n")

    for i, post in enumerate(posts, start=1):
        lines.append(f"{i}/{total}")
        lines.append(post.strip())
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def format_json_thread(posts: List[str]) -> Dict:
    return {
        "count": len(posts),
        "posts": [
            {"index": i + 1, "text": post}
            for i, post in enumerate(posts)
        ],
    }


def emit_output(
    posts: List[str],
    *,
    as_json: bool,
    out_path: str | None,
) -> None:
    if as_json:
        payload = json.dumps(
            format_json_thread(posts),
            indent=2,
            ensure_ascii=False,
        )
    else:
        payload = format_text_thread(posts)

    if out_path:
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(payload)
    else:
        print(payload, end="")
