# nanobanana-skill

A [Claude Agent Skill](https://github.com/anthropics/skills) for image generation, editing, and restoration via Google's Nano Banana (Gemini image models).

When you ask Claude things like *"generate a watercolor of a fox"*, *"make a favicon for my app"*, *"edit this photo to add sunglasses"*, or *"draw an architecture diagram for a microservices system"*, this skill activates and runs the appropriate Gemini image model. Default: `gemini-3.1-flash-image-preview` (Nano Banana 2).

## Install

```bash
git clone https://github.com/batou9150/nanobanana-skill ~/.claude/skills/nanobanana
python3 -m pip install -r ~/.claude/skills/nanobanana/requirements.txt
export NANOBANANA_API_KEY=...   # https://aistudio.google.com/apikey
```

Restart Claude Code (or reload skills) and ask Claude to generate something.

## Subcommands

| Command | Purpose |
|---|---|
| `generate` | Text-to-image with optional batch styles / variations |
| `edit` | Modify an existing image |
| `restore` | Repair / enhance an image |
| `icon` | App icon, favicon, UI element |
| `pattern` | Seamless pattern / texture |
| `story` | Sequential frames (story / process / tutorial / timeline) |
| `diagram` | Flowchart, architecture, schema, wireframe |

Run any subcommand with `--help` to see flags:

```bash
python3 ~/.claude/skills/nanobanana/scripts/nanobanana.py generate --help
```

## Direct CLI use (without Claude)

The CLI works standalone:

```bash
python3 ~/.claude/skills/nanobanana/scripts/nanobanana.py generate \
  "sunset over mountains" --count=3 --styles=watercolor,oil-painting
```

Output goes to `./nanobanana-output/` in your cwd.

## Model override

```bash
export NANOBANANA_MODEL=gemini-3-pro-image-preview   # Nano Banana Pro
export NANOBANANA_MODEL=gemini-2.5-flash-image       # Nano Banana v1
```

## Credit

Adapted from the official [`gemini-cli-extensions/nanobanana`](https://github.com/gemini-cli-extensions/nanobanana) Gemini CLI extension. This is a Claude-Skill port — no MCP server, no Node runtime, just a Python CLI invoked from `SKILL.md`.

## License

MIT — see [LICENSE](LICENSE).
