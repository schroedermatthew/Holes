#!/usr/bin/env python3
"""
Convert phantom-fatp transcript files to readable markdown.

Usage:
    python convert_transcript.py <input.txt> <output.md>

The input transcripts are role-labeled blocks (Assistant:, Human:) followed by
"Content:" and a JSON array of content blocks. This script extracts the
readable parts — text, thinking, tool calls, and brief tool result summaries —
and outputs clean markdown.
"""
import json
import re
import sys
from pathlib import Path


def split_into_turns(content: str):
    """Split transcript text into (role, content) turns."""
    pattern = re.compile(r"^(Assistant|Human|User):\s*$", re.MULTILINE)
    splits = pattern.split(content)
    turns = []
    # splits[0] is whatever came before the first role marker (usually empty)
    # then alternates: role, content, role, content, ...
    for i in range(1, len(splits), 2):
        if i + 1 < len(splits):
            role = splits[i].strip()
            body = splits[i + 1].strip()
            turns.append((role, body))
    return turns


def extract_json_array(body: str):
    """The body starts with 'Content:' then a JSON array. Extract it."""
    body = body.strip()
    if body.startswith("Content:"):
        body = body[len("Content:"):].strip()
    # Find the JSON array
    if not body.startswith("["):
        return None
    # Find the matching ] — count brackets, respecting strings
    depth = 0
    in_string = False
    escape = False
    for i, ch in enumerate(body):
        if escape:
            escape = False
            continue
        if ch == "\\":
            escape = True
            continue
        if ch == '"' and not escape:
            in_string = not in_string
            continue
        if in_string:
            continue
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
            if depth == 0:
                json_str = body[: i + 1]
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError as e:
                    print(f"  WARN: JSON decode error: {e}", file=sys.stderr)
                    return None
    return None


def truncate(text: str, n: int = 2000) -> str:
    if len(text) <= n:
        return text
    return text[:n] + f"\n...[truncated {len(text) - n} chars]"


def render_turn(role: str, blocks: list) -> str:
    out = []
    out.append(f"\n\n## {role}\n")
    if blocks is None:
        out.append("*[content could not be parsed as JSON]*\n")
        return "\n".join(out)

    for block in blocks:
        btype = block.get("type", "unknown")

        if btype == "text":
            text = block.get("text", "").strip()
            if text:
                out.append(text)
                out.append("")

        elif btype == "thinking":
            thinking = block.get("thinking", "").strip()
            if thinking:
                out.append("> **[Thinking block]**")
                # indent each line as a quote
                for line in thinking.split("\n"):
                    out.append(f"> {line}")
                out.append("")

        elif btype == "tool_use":
            name = block.get("name", "?")
            tool_input = block.get("input", {})
            out.append(f"**[Tool call: `{name}`]**")
            # format input compactly
            try:
                inp_str = json.dumps(tool_input, indent=2)
            except Exception:
                inp_str = str(tool_input)
            inp_str = truncate(inp_str, 3000)
            out.append("```json")
            out.append(inp_str)
            out.append("```")
            out.append("")

        elif btype == "tool_result":
            tool_name = block.get("name", "?")
            content = block.get("content", [])
            out.append(f"**[Tool result: `{tool_name}`]**")
            if isinstance(content, list):
                for c in content:
                    if isinstance(c, dict):
                        ctype = c.get("type", "")
                        if ctype == "text":
                            text = c.get("text", "")
                            out.append("```")
                            out.append(truncate(text, 1500))
                            out.append("```")
                        elif ctype == "knowledge":
                            title = c.get("title", "")
                            url = c.get("url", "")
                            out.append(f"- {title} ({url})")
                        else:
                            out.append(f"*[{ctype}]*")
                    else:
                        out.append(str(c)[:500])
            elif isinstance(content, str):
                out.append("```")
                out.append(truncate(content, 1500))
                out.append("```")
            else:
                out.append(f"*[content type: {type(content).__name__}]*")
            out.append("")

        elif btype in ("local_resource", "webpage_metadata", "knowledge", "table", "json_block"):
            # display brief summary
            title = block.get("title") or block.get("name") or block.get("file_path") or btype
            out.append(f"*[{btype}: {title}]*")
            out.append("")

        else:
            out.append(f"*[unknown block type: {btype}]*")
            out.append("")

    return "\n".join(out)


def render_user_turn(role: str, body: str) -> str:
    """User turns are simpler — usually just text after 'Content:' or a JSON array."""
    body = body.strip()
    if body.startswith("Content:"):
        body = body[len("Content:"):].strip()

    # Try parsing as JSON array first
    if body.startswith("["):
        blocks = extract_json_array("Content:" + body)
        if blocks:
            return render_turn(role, blocks)

    # Otherwise it's plain text
    out = [f"\n\n## {role}\n"]
    out.append(body)
    return "\n".join(out)


def convert(input_path: Path, output_path: Path):
    print(f"Reading {input_path} ({input_path.stat().st_size:,} bytes)")
    content = input_path.read_text(encoding="utf-8")

    turns = split_into_turns(content)
    print(f"Found {len(turns)} turns")

    out = [f"# Transcript: {input_path.name}\n"]
    out.append(f"*Converted from JSON-formatted transcript file. {len(turns)} turns.*\n")
    out.append("---")

    for i, (role, body) in enumerate(turns):
        if role == "Assistant":
            blocks = extract_json_array(body)
            out.append(render_turn(role, blocks))
        else:
            out.append(render_user_turn(role, body))

        if (i + 1) % 5 == 0:
            print(f"  rendered {i + 1}/{len(turns)} turns")

    output_path.write_text("\n".join(out), encoding="utf-8")
    print(f"Wrote {output_path} ({output_path.stat().st_size:,} bytes)")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python convert_transcript.py <input.txt> <output.md>", file=sys.stderr)
        sys.exit(1)
    convert(Path(sys.argv[1]), Path(sys.argv[2]))
