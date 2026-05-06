# convert_transcript.py — Transcript-to-Markdown Converter

Converts Anthropic transcript export files (`.txt`, JSON-formatted) into readable markdown.

## What it does

The transcripts in `/mnt/transcripts/` are stored as text files containing role-labeled turns (`Assistant:`, `Human:`) followed by `Content:` and a JSON array of content blocks. Each block has a `type` field — `text`, `thinking`, `tool_use`, `tool_result`, etc. — plus type-specific fields like `text`, `thinking`, `name`, `input`, `content`.

The raw files are technically readable in any text editor but unpleasant: lots of metadata (`start_timestamp`, `stop_timestamp`, `flags`, `integration_name`, `approval_options`, ...), heavy JSON escaping, and tool results that contain whole-file dumps embedded as escaped strings. This script strips the noise and produces a markdown rendering that opens cleanly in VS Code, Obsidian, Typora, GitHub, or anything else that renders `.md`.

## Usage

```
python convert_transcript.py <input.txt> <output.md>
```

Requires Python 3 (any 3.7+ should work — uses standard library only, no external dependencies).

Example:
```
python convert_transcript.py transcript-2-phantom-fatp-rewrite-post-compaction.txt transcript-2-readable.md
```

## What gets preserved

| Block type | What you see in the output |
|---|---|
| `text` | The full text verbatim, no truncation |
| `thinking` | Full thinking content as a blockquote, prefixed with `**[Thinking block]**` |
| `tool_use` | Tool name plus the input arguments rendered as JSON in a code block, truncated at 3000 chars |
| `tool_result` | Tool name plus a truncated dump of the result content (1500 chars per item) |
| `local_resource`, `webpage_metadata`, `knowledge`, `table`, `json_block` | Brief one-line summary with the title or name |

Role markers (`Assistant`, `Human`, `User`) become H2 headings (`## Assistant`, etc.).

## What gets dropped or compressed

**JSON metadata** — `start_timestamp`, `stop_timestamp`, `flags`, `integration_name`, `integration_icon_url`, `icon_name`, `context`, `display_content`, `approval_options`, `approval_key`, `is_mcp_app`, `mcp_server_url`, `id`, `tool_use_id`, `citations`, `summaries` — none of these appear in the output. They are not informative for reading the conversation.

**Tool result content** is truncated to 1500 chars per item (with `...[truncated N chars]` marker). The truncation matters because tool results often contain whole files being read back, full search result pages, etc. — keeping them in full would defeat the purpose. If you need fuller tool results, see "Adjusting truncation" below.

**Tool input JSON** is truncated to 3000 chars. This matters mostly for `create_file` calls where the entire file content is passed as the `file_text` parameter. The first 3000 chars are usually enough to identify what file is being created and the start of its content; the original `.txt` has the full version if you need it.

## Known limitation: thinking blocks

The transcripts as exported contain very few thinking blocks. In the two FatP-rewrite transcripts:

- `transcript-1-phantom-fatp-rewrite-pre-compaction.txt`: 1 thinking block across 9 turns
- `transcript-2-phantom-fatp-rewrite-post-compaction.txt`: 1 thinking block across 4 turns

This is a property of the source files, not of this converter. Whatever was happening in the model's extended thinking during most turns either was not captured or was stripped before transcript export. The single thinking block per file that did make it through is rendered fully.

If you want a verbatim record of reasoning going forward, the workaround is to externalize reasoning into the visible response — write out alternatives, considerations, rationale in normal text rather than relying on thinking blocks to be retained.

## Adjusting truncation

The truncation thresholds are constants inside `render_turn()`. To change them, edit these lines:

```python
inp_str = truncate(inp_str, 3000)        # tool_use input JSON
out.append(truncate(text, 1500))         # tool_result text content
out.append(truncate(content, 1500))      # tool_result string content
```

Set the second argument to a larger number (or to a very large number like `10**9` to disable truncation entirely). The output file will get correspondingly bigger.

If you want to disable truncation only for specific tools — for example, keep `web_search` results full but truncate `bash_tool` output — you'll need to add a check on `tool_name` inside the `tool_result` branch.

## How parsing works

The converter does three things in sequence.

**1. Split into role-labeled turns.** The regex `^(Assistant|Human|User):\s*$` (multiline) finds the role markers. Each turn is a `(role, body)` pair where body is everything between this role marker and the next.

**2. Extract the JSON array from each turn body.** Assistant turn bodies start with `Content:` followed by a JSON array. The script strips the `Content:` prefix, then scans character-by-character to find the matching closing `]` for the opening `[`, respecting string delimiters and escapes. This is more robust than naive regex matching against arrays containing nested brackets, quoted strings with brackets, or escape sequences.

**3. Render each block.** A dispatch on `block.get("type")` formats each block according to the table above. Unknown types produce a placeholder line (`*[unknown block type: foo]*`) rather than failing.

User-turn bodies are usually plain text rather than a JSON array; the converter tries JSON parse first and falls back to displaying the body as-is.

## Failure modes

**JSON parse fails on a turn.** Output shows `*[content could not be parsed as JSON]*` for that turn. The original transcript may have been corrupted at that turn, or the format may have changed. Other turns continue to render normally. A warning is printed to stderr.

**An unknown block type appears.** Output shows `*[unknown block type: <type>]*` and processing continues. To handle the new type properly, add an `elif btype == "<new_type>":` branch in `render_turn()`.

**The role marker regex misses a transition.** Symptom: two turns get merged into one in the output. This would happen if a transcript had a non-standard role marker. The current regex matches exactly `Assistant`, `Human`, `User` followed by `:` at start of line. Add additional alternatives if needed.

**Encoding errors.** The script assumes UTF-8 throughout (read and write). All transcripts I tested are valid UTF-8. If you encounter a `UnicodeDecodeError`, the file may be in a different encoding; pass `encoding="utf-8-sig"` or detect via `chardet`.

## Output structure

The output markdown begins with a heading naming the source file and a turn count, then alternates role headings and turn content:

```markdown
# Transcript: <source-filename>

*Converted from JSON-formatted transcript file. N turns.*

---

## Assistant

[text from first turn]

**[Tool call: `bash_tool`]**
```json
{
  "command": "ls",
  "description": "list files"
}
```

**[Tool result: `bash_tool`]**
```
total 0
```

[more text]

## Human

[user message]

## Assistant

[next assistant turn]
```

## Files in this distribution

- `convert_transcript.py` — the script.
- `README.md` — this file.

No installation, no dependencies, no configuration file. Drop the script anywhere and run it.

## Source transcripts

The transcripts this script was written for are stored at:

- `/mnt/transcripts/2026-05-02-19-51-53-phantom-fatp-rewrite.txt` (947 KB, 9 turns) — earlier FatP-rewrite session
- `/mnt/transcripts/2026-05-02-20-08-21-phantom-fatp-rewrite.txt` (634 KB, 4 turns) — post-compaction continuation

Plus seven other earlier sessions from the broader Phantom-framework-extension work (May 1-2, 2026) listed in `/mnt/transcripts/journal.txt`.

The script handles all of them — the format is consistent across the export.

---

*Companion to the Phantom framework documentation. The transcripts captured here record the development of the framework's ML extension and the FatP-style rewrite of the framework documents. They are reference material for understanding how the framework documents were arrived at, not part of the framework itself.*
