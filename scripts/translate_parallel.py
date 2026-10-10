#!/usr/bin/env python3
"""Build an English/Japanese parallel (対訳) Markdown file from a source Markdown file, using DeepL.

Usage:
    python3 translate_parallel.py "input.md" ["output.md"]

Reads DEEPL_API_KEY from the environment, or from a .env file at the
project root, one directory up from this script (format: DEEPL_API_KEY=...).

Passthrough (not translated): code fences, image lines (![...]), table rows
(lines starting with "|"), and blank lines.
Translated: headings, "- " / "* " list items, and normal paragraph lines.
"""
import os
import re
import sys
import time

import requests

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(SCRIPT_DIR, "..", ".env")

CODE_FENCE_RE = re.compile(r"^```")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
LIST_RE = re.compile(r"^(\s*[-*]\s+)(.*)$")

BATCH_SIZE = 20


def load_api_key():
    if os.environ.get("DEEPL_API_KEY"):
        return os.environ["DEEPL_API_KEY"]
    if os.path.exists(ENV_PATH):
        with open(ENV_PATH, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("DEEPL_API_KEY="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise RuntimeError(f"DEEPL_API_KEY not found in environment or {ENV_PATH}")


def api_base(key):
    return "https://api-free.deepl.com/v2" if key.endswith(":fx") else "https://api.deepl.com/v2"


def translate_batch(texts, key, source_lang="EN", target_lang="JA"):
    if not texts:
        return []
    url = f"{api_base(key)}/translate"
    headers = {"Authorization": f"DeepL-Auth-Key {key}"}
    data = [
        ("source_lang", source_lang),
        ("target_lang", target_lang),
        ("preserve_formatting", "1"),
    ]
    data += [("text", t) for t in texts]
    resp = requests.post(url, headers=headers, data=data, timeout=30)
    resp.raise_for_status()
    return [t["text"] for t in resp.json()["translations"]]


def parse_blocks(lines):
    """Split source lines into (kind, content) blocks.

    kind is one of: "pass", "heading", "list", "para".
    """
    blocks = []
    in_code = False
    for raw in lines:
        line = raw.rstrip("\n")

        if CODE_FENCE_RE.match(line):
            in_code = not in_code
            blocks.append(("pass", line))
            continue
        if in_code:
            blocks.append(("pass", line))
            continue
        if line.strip() == "":
            blocks.append(("pass", line))
            continue
        if line.startswith("!["):
            blocks.append(("pass", line))
            continue
        if line.startswith("|"):
            blocks.append(("pass", line))
            continue

        m = HEADING_RE.match(line)
        if m:
            blocks.append(("heading", (m.group(1), m.group(2))))
            continue

        m = LIST_RE.match(line)
        if m:
            blocks.append(("list", (m.group(1), m.group(2))))
            continue

        blocks.append(("para", line))

    return blocks


def collect_texts(blocks):
    texts = []
    for kind, content in blocks:
        if kind in ("heading", "list"):
            texts.append(content[1])
        elif kind == "para":
            texts.append(content)
    return texts


def translate_all(texts, key):
    out = []
    for i in range(0, len(texts), BATCH_SIZE):
        chunk = texts[i : i + BATCH_SIZE]
        out.extend(translate_batch(chunk, key))
        print(f"  translated {min(i + BATCH_SIZE, len(texts))}/{len(texts)}", file=sys.stderr)
        time.sleep(0.2)
    return out


def render(blocks, translations):
    ti = iter(translations)
    out_lines = []
    for kind, content in blocks:
        if kind == "pass":
            out_lines.append(content)
        elif kind == "heading":
            hashes, text = content
            ja = next(ti)
            out_lines.append(f"{hashes} {text}")
            out_lines.append("")
            out_lines.append(f"*{ja}*")
        elif kind == "list":
            prefix, text = content
            ja = next(ti)
            out_lines.append(f"{prefix}{text}")
            out_lines.append(f"{' ' * len(prefix)}*{ja}*")
        elif kind == "para":
            ja = next(ti)
            out_lines.append(content)
            out_lines.append("")
            out_lines.append(f"> {ja}")
    return "\n".join(out_lines) + "\n"


def main():
    if len(sys.argv) < 2:
        print(f"usage: {sys.argv[0]} <input.md> [output.md]", file=sys.stderr)
        sys.exit(1)

    in_path = sys.argv[1]
    out_path = sys.argv[2] if len(sys.argv) > 2 else re.sub(r"\.md$", "", in_path) + " (対訳).md"

    key = load_api_key()

    with open(in_path, encoding="utf-8") as f:
        lines = f.readlines()

    blocks = parse_blocks(lines)
    texts = collect_texts(blocks)
    print(f"{len(texts)} segments to translate...", file=sys.stderr)

    translations = translate_all(texts, key)
    output = render(blocks, translations)

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(output)

    print(f"wrote {out_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
