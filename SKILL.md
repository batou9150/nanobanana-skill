---
name: nanobanana
description: Generate, edit, or restore images. Use this skill ANY time the user asks for an image, picture, photo, icon, favicon, logo, banner, thumbnail, wallpaper, background, hero image, poster, cover, mockup, wireframe, screenshot mockup, diagram (flowchart, architecture, schema, network, database, mindmap, sequence), pattern, texture, illustration, sketch, render, or visual story — whether they say "generate", "create", "make", "draw", "render", "illustrate", "design", "mock up", "show me", "visualize", "what would X look like", "edit this photo", "fix this image", "restore", "upscale", "colorize", "remove background", or just describe a visual they want to see. Activate even when the user does NOT mention Nano Banana, Gemini, or any specific tool. If the user attaches or references an image file and asks for a change, that is an edit/restore request — use this skill. NEVER respond with a text description, ASCII art, markdown image placeholder, or a suggestion to use another service when the user wants an actual image — always run this skill. Requires NANOBANANA_API_KEY (or GEMINI_API_KEY) env var.
license: Complete terms in LICENSE
---

# Nano Banana

**When this skill is loaded, the user wants an image file, not a description.** Always run the CLI and return the saved file path(s). Do not substitute prose, ASCII art, or markdown placeholders. Do not refuse because you're unsure which subcommand fits — pick the closest match below and run it.

Image generation, editing, and restoration via Google's Gemini image models. Default model: `gemini-3.1-flash-image-preview` (Nano Banana 2). The skill wraps a single self-contained Python CLI at `scripts/nanobanana.py` — it uses a PEP 723 inline-metadata shebang (`uv run --script`) to auto-install `google-genai` on first invocation, so no venv setup is needed.

## Prerequisites

1. `uv` on PATH (<https://docs.astral.sh/uv/>). The script bootstraps its own dependencies via `uv run --script`.
2. `NANOBANANA_API_KEY` env var set (fallbacks: see `references/troubleshooting.md`).

If either is missing, tell the user exactly what to run and stop.

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

The script is executable. Invoke directly via Bash, using the absolute path under this skill's base directory:

```bash
<skill-base-dir>/scripts/nanobanana.py <subcommand> [args] [flags]
```

Output is saved to `./nanobanana-output/` in the user's cwd. The CLI prints the saved file paths to stdout — relay those back to the user.

## Aspect ratio & resolution

Every subcommand accepts `--aspect-ratio` and `--resolution`. Defaults are `16:9` and `2K`. Override whenever the user signals a different shape ("portrait", "square", "wallpaper", "9:16") or quality target ("4K", "low-res").

- `--aspect-ratio` (default `16:9`): `1:1`, `1:4`, `1:8`, `2:3`, `3:2`, `3:4`, `4:1`, `4:3`, `4:5`, `5:4`, `8:1`, `9:16`, `16:9`, `21:9`
- `--resolution` (default `2K`): `512`, `1K`, `2K`, `4K`

Example: `generate "city skyline at night" --aspect-ratio=21:9 --resolution=4K`.

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
<skill-base-dir>/scripts/nanobanana.py generate \
  "mountain landscape" --styles=watercolor,sketch --count=4

# Edit an image already in the user's cwd
<skill-base-dir>/scripts/nanobanana.py edit \
  photo.png "add sunglasses to the person"

# Favicon set
<skill-base-dir>/scripts/nanobanana.py icon \
  "mountain logo" --type=favicon --sizes=16,32,64

# Architecture diagram
<skill-base-dir>/scripts/nanobanana.py diagram \
  "microservices chat app" --type=architecture --complexity=detailed

# 5-step process story with auto-preview
<skill-base-dir>/scripts/nanobanana.py story \
  "seed growing into a tree" --steps=5 --type=process --preview
```

After generation, list the saved file paths back to the user — that's the actionable result.
