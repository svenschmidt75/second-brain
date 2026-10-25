---
name: sb
description: Interact with the second_brain CLI. Use when second brain or notes are mentioned.
---

# sb — second_brain notes

Save a summary of the current conversation in the second brain, with a matching title.
If a summary note for this session already exists, enhance that file instead of creating a new one.

## Steps

1. Find the session transcript: `~/.claude/projects/<project-dir>/<session-id>.jsonl`.
   `<project-dir>` is the working directory with `/`, `_` and `.` replaced by `-`.
   `<session-id>` is the UUID in the scratchpad path; otherwise the newest `.jsonl` in that directory.
2. Look for an existing note of this session: `rg -l <session-id> "${SECOND_BRAIN_DIR:-~/second_brain}"`.
3. No note yet: `second_brain new "<title>" --body "<note body>"`. It prints the note path.
   Note exists: edit that file in place. Keep earlier content, add new points, update the title if the scope grew.
4. The note must always contain:
   - `Session:` the absolute path of the transcript from step 1.
   - `Project:` the absolute path of the project directory the conversation took place in.
5. Respond with the filepath of the note, and nothing else.

## Note body

- Short summary: goal, decisions, outcome, open points.
- Terse bullets; no transcript dumps.

## CLI reference

```bash
second_brain new "Title" [--body TEXT]   # body from stdin if omitted; prints path
second_brain list                        # numbered, newest first
second_brain show N                      # print note N (1-based, as in `list`)
```

Notes dir: `SECOND_BRAIN_DIR` (default `~/second_brain/`). Filenames are `YYYY-MM-DD-<slug>.md`.
