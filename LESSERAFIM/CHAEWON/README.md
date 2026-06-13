# CHAEWON Codex Pet

Compact chibi Codex desktop pet packaged for the Codex custom pet system.

## Files

- `pet.json`: Codex pet manifest
- `spritesheet.webp`: final transparent atlas, `1536x1872`
- `cursor-pack/`: Windows cursor adaptation generated from the pet
- `qa/contact-sheet.png`: full row-by-row contact sheet
- `qa/previews/*.gif`: motion previews for every state
- `qa/validation.json`: atlas validation output
- `qa/review.json`: frame inspection output

## States

The spritesheet follows the Codex pet 9-state contract:

1. `idle`
2. `running-right`
3. `running-left`
4. `waving`
5. `jumping`
6. `failed`
7. `waiting`
8. `running`
9. `review`

## Verification

The generated atlas was checked with the hatch-pet deterministic pipeline:

- `validation.json`: `ok: true`, no errors, no warnings
- `review.json`: `ok: true`, no errors, no warnings
- transparent atlas size: `1536x1872`

## Windows Cursor Pack

The `cursor-pack` folder contains:

- `cur/*.cur`: static Windows cursor files
- `ani/*.ani`: animated Windows cursor files
- `png/*.png`: transparent PNG source previews
- `preview/cursor-sheet.png`: reference sheet
- `preview/*.gif`: animated cursor previews

Suggested Windows mapping:

- Normal Select: `cursor-pack/cur/normal.cur`
- Help Select: `cursor-pack/cur/help.cur`
- Working In Background: `cursor-pack/ani/working.ani`
- Busy: `cursor-pack/ani/busy.ani`
- Text Select: `cursor-pack/cur/text.cur`
- Link Select: `cursor-pack/cur/link.cur`
- Unavailable: `cursor-pack/cur/unavailable.cur`
- Move: `cursor-pack/cur/move.cur`
- Horizontal Resize: `cursor-pack/cur/ew-resize.cur`
- Vertical Resize: `cursor-pack/cur/ns-resize.cur`
- Diagonal Resize 1: `cursor-pack/cur/nwse-resize.cur`
- Diagonal Resize 2: `cursor-pack/cur/nesw-resize.cur`

On Windows, open `Settings > Bluetooth & devices > Mouse > Additional mouse settings > Pointers`, then browse to these files for each pointer role.

Regenerate the cursor pack:

```bash
python tools/build_cursor_pack.py \
  --pet-dir LESSERAFIM/CHAEWON \
  --out-dir LESSERAFIM/CHAEWON/cursor-pack
```
