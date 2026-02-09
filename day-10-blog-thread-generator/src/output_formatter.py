from __future__ import annotations

import json
from typing import Dict

from thread_generator import ThreadVariant, ThreadPost


def format_text_thread(variant: ThreadVariant) -> str:
    lines: list[str] = []
    total = len(variant.posts)

    lines.append(f"{variant.name}")
    lines.append(f"Thread ({total} posts)")
    lines.append("")

    for i, post in enumerate(variant.posts, start=1):
        lines.append(f"{i}/{total}")
        lines.append(post.text.strip())
        lines.append("")

    if variant.warnings:
        lines.append("Warnings:")
        for warning in variant.warnings:
            lines.append(f"- {warning}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def format_json_thread(variant: ThreadVariant) -> Dict:
    return {
        "name": variant.name,
        "count": len(variant.posts),
        "warnings": variant.warnings,
        "posts": [
            {
                "index": i + 1,
                "char_count": post.char_count,
                "segment_ids": post.segment_ids,
                "text": post.text,
            }
            for i, post in enumerate(variant.posts)
        ],
    }


def emit_output(
    variant: ThreadVariant,
    *,
    as_json: bool,
    out_path: str | None,
) -> None:
    if as_json:
        payload = json.dumps(
            format_json_thread(variant),
            indent=2,
            ensure_ascii=False,
        )
    else:
        payload = format_text_thread(variant)

    if out_path:
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(payload)
    else:
        print(payload, end="")
