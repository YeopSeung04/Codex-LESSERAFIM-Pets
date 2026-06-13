# Codex LESSERAFIM Pets

Codex-compatible custom pet spritesheets organized by artist and member.

## Pets

- `LESSERAFIM/CHAEWON`

## How to Use

Copy a pet folder into your Codex pets directory:

```bash
mkdir -p "$HOME/.codex/pets/chaewon"
cp LESSERAFIM/CHAEWON/pet.json "$HOME/.codex/pets/chaewon/pet.json"
cp LESSERAFIM/CHAEWON/spritesheet.webp "$HOME/.codex/pets/chaewon/spritesheet.webp"
```

Then open Codex settings, select the pet, and run `/pet` or the `Wake Pet` command to show the desktop pet overlay.

## Validation

Each pet folder includes QA artifacts:

- `qa/contact-sheet.png`
- `qa/previews/*.gif`
- `qa/validation.json`
- `qa/review.json`

Some pets also include `cursor-pack/`, a Windows cursor adaptation built from the same pet. Use `cursor-pack/ani/*.ani` for animated pointers; `cursor-pack/cur/*.cur` is included as a static fallback.
