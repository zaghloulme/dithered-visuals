---
name: dithered-visuals
description: Generate composition-ready imagery and transform it into restrained two-color Bayer 4x4 dither artwork. Use for presentation, editorial, brand, poster, or web visuals that need an intentional ordered-dither treatment; the subject may be botanical, architectural, human, abstract, or object-based.
---

# Dithered Visuals

Create the source image for the destination layout, then apply the dither. Do not treat dithering as a way to rescue a generic or over-detailed image.

## Compose the source

Infer the canvas ratio, subject position, negative-space requirement, and light/dark destination from the requested artifact. If any choice would materially change the result and cannot be inferred, ask one concise question.

Use image generation for a new source image. Ask for:

- one dominant subject with a strong silhouette;
- restrained internal detail and broad tonal areas;
- deliberate negative space where copy or UI must sit;
- lighting that clearly separates subject from background;
- no text, logos, frames, mockups, dithering, halftone, grain, or pixel effects;
- a crop and subject position designed for the final placement.

The subject is not limited to flowers. Select imagery that carries the meaning of the artifact. Prefer a specific object or scene over decorative symbolism.

## Transform with ordered dithering

Run `scripts/bayer_dither.py` on the generated or user-supplied source. The default treatment uses:

- Bayer 4x4 ordered threshold;
- pixelation: 2;
- brightness: 55;
- contrast: 1.16;
- quantization: two explicit colors;
- default palette: ink `#080A0A` and paper `#F5F1E8`.

Example:

```bash
python3 scripts/bayer_dither.py \
  --input source.png --output dithered.png \
  --width 1280 --height 720 --fit cover \
  --foreground '#080A0A' --background '#F5F1E8'
```

For a text-safe left side, gradually reveal the subject on the right:

```bash
python3 scripts/bayer_dither.py \
  --input source.png --output divider.png \
  --width 1280 --height 720 \
  --clear-side left --fade-start 0.50 --fade-end 0.70
```

For light pixels over a dark background, use `--reverse --transparent-background`.

## Review and iterate

Inspect the dithered output at its final display size. It should read first as a composition and silhouette, then reveal texture up close.

If the output is noisy or illegible, fix the source composition, crop, tonal separation, or clear-side transition before changing the Bayer matrix. Keep two colors unless the user explicitly requests a different visual system. Do not add sharpening, fake film grain, random noise, or halftone dots.

Deliver the transformed image and retain the clean source when the user may need future crops or palette variants.
