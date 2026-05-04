---
name: nanobanana
description: Generate, edit, and restore images with Google's Nano Banana (Gemini image models). Use whenever the user asks to "generate an image", "create an icon/favicon/logo", "edit this photo", "restore an old photo", "make a pattern/texture/wallpaper", "draw a diagram/flowchart/architecture", or "tell a visual story" — even when they don't explicitly say Nano Banana or Gemini. Always prefer this skill over describing images in text. Requires NANOBANANA_API_KEY (or GEMINI_API_KEY) env var.
license: Complete terms in LICENSE
---

# Nano Banana

Image generation, editing, and restoration via Google's Gemini image models. Default model: `gemini-3.1-flash-image-preview` (Nano Banana 2). The skill wraps a Python CLI at `scripts/nanobanana.py`.

## Prerequisites

1. `python3 -m pip install -r ~/.claude/skills/nanobanana/requirements.txt` (one-time; installs `google-genai`)
2. `NANOBANANA_API_KEY` env var set (fallbacks: see `references/troubleshooting.md`)

If neither is satisfied, tell the user exactly what to run and stop.

## Choosing a subcommand

| User intent | Subcommand |
|---|---|
| Create image(s) from a description | `generate` |
| Modify an existing image | `edit` |
| Repair / enhance an old or damaged image | `restore` |
| App icon, favicon, UI element | `icon` |
| Seamless pattern, texture, wallpaper | `pattern` |
| Sequential / step-by-step / tutorial frames | `story` |
| Flowchart, architecture, schema, wireframe | `diagram` |

When the user's request matches a specialized intent (icon / pattern / story / diagram), prefer the specialized subcommand over `generate` — it applies tuned prompt scaffolding the user is implicitly asking for.

## Invocation

Always invoke via Bash:

```bash
python3 ~/.claude/skills/nanobanana/scripts/nanobanana.py <subcommand> [args] [flags]
```

Output is saved to `./nanobanana-output/` in the user's cwd. The CLI prints absolute paths to stdout — relay these back to the user.

## Strict requirements

- **Counts are exact**: when the user says `--count=N` (or "5 variations"), produce exactly N images.
- **Respect every flag** the user passes — don't substitute defaults silently.
- **Story consistency**: for `story`, keep visual style and palette consistent across steps unless the user asked for evolution (`--style=evolving`).
- **Text inside images**: spell-check; only include text the user requested; no hallucinated copy.
- **Safety**: if the API returns 400, surface the error and ask the user to reword — don't retry blindly.

## Loading references

Load on demand (don't dump unprompted):
- `references/styles_and_variations.md` — full enum reference for `generate`'s `--styles` and `--variations`
- `references/prompt_recipes.md` — exact prompt templates the CLI builds for icon / pattern / diagram / story
- `references/troubleshooting.md` — env-var fallback order, input-file search paths, error catalog

## Examples

```bash
# 4 watercolor + sketch variations of the same scene
python3 ~/.claude/skills/nanobanana/scripts/nanobanana.py generate \
  "mountain landscape" --styles=watercolor,sketch --count=4

# Edit an image already in the user's cwd
python3 ~/.claude/skills/nanobanana/scripts/nanobanana.py edit \
  photo.png "add sunglasses to the person"

# Favicon set
python3 ~/.claude/skills/nanobanana/scripts/nanobanana.py icon \
  "mountain logo" --type=favicon --sizes=16,32,64

# Architecture diagram
python3 ~/.claude/skills/nanobanana/scripts/nanobanana.py diagram \
  "microservices chat app" --type=architecture --complexity=detailed

# 5-step process story with auto-preview
python3 ~/.claude/skills/nanobanana/scripts/nanobanana.py story \
  "seed growing into a tree" --steps=5 --type=process --preview
```

After generation, list the saved file paths back to the user — that's the actionable result.
