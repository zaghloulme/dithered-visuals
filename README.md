# Dithered Visuals

![Dithered Visuals icon](assets/icon.svg)

An agent skill for creating composition-ready imagery and converting it into restrained, two-color Bayer 4×4 dither artwork.

It works with architectural scenes, botanicals, portraits, objects, abstract forms, editorial graphics, presentation visuals, posters, and web imagery. The workflow deliberately composes the source image first, then applies the dither so the final result keeps a strong silhouette and useful negative space.

## Install

Install with the open Agent Skills CLI:

```bash
npx skills add zaghloulme/dithered-visuals
```

To install it globally for Codex without prompts:

```bash
npx skills add zaghloulme/dithered-visuals \
  --skill dithered-visuals \
  --agent codex \
  --global \
  --yes
```

After installation, start a new agent session so the skill is discovered.

## Use

Ask your agent to use the skill explicitly:

```text
Use $dithered-visuals to create an isometric architectural drawing
of a Gothic building with a simple background.
```

Or describe the intended visual and layout:

```text
Create a two-color editorial image of an old observatory.
Keep the left half quiet for a headline and use dark ink on warm paper.
```

The skill guides the agent through three stages:

1. Compose a clean source image for its final placement.
2. Convert it with a two-color Bayer 4×4 ordered dither.
3. Review the result at its intended display size and iterate if needed.

## Default treatment

- Bayer 4×4 ordered threshold
- Two-color output
- Pixelation: `2`
- Brightness: `55`
- Contrast: `1.16`
- Ink: `#080A0A`
- Paper: `#F5F1E8`

## Run the converter directly

The bundled converter requires Python 3.10 or newer.

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

Convert an image:

```bash
python3 scripts/bayer_dither.py \
  --input source.png \
  --output dithered.png \
  --width 1280 \
  --height 720 \
  --fit cover
```

Create a composition with a clear left side for text:

```bash
python3 scripts/bayer_dither.py \
  --input source.png \
  --output divider.png \
  --width 1280 \
  --height 720 \
  --clear-side left \
  --fade-start 0.50 \
  --fade-end 0.70
```

Create light pixels for placement over a dark background:

```bash
python3 scripts/bayer_dither.py \
  --input source.png \
  --output reversed.png \
  --reverse \
  --transparent-background
```

Run `python3 scripts/bayer_dither.py --help` for every option.

## Repository structure

| Path | Purpose |
| --- | --- |
| `SKILL.md` | Agent instructions and workflow |
| `agents/openai.yaml` | OpenAI agent metadata |
| `scripts/bayer_dither.py` | Bayer 4×4 image converter |
| `assets/icon.svg` | Skill icon |

## Design principles

- Compose for the destination layout before dithering.
- Prefer one clear subject and broad tonal areas.
- Preserve intentional negative space for copy or UI.
- Keep the output to two colors unless a different system is requested.
- Fix composition, crop, or tonal separation before changing the dither matrix.
- Avoid halftone dots, random noise, fake grain, and unnecessary sharpening.
