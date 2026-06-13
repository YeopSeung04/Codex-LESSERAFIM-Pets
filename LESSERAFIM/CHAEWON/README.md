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

- `ani/*.ani`: animated Windows cursor files for all common Windows pointer roles
- `cur/*.cur`: static fallback Windows cursor files
- `png/*.png`: transparent PNG source previews
- `preview/cursor-sheet.png`: reference sheet
- `preview/*.gif`: animated cursor previews
- `source/mascot-base.png`: high-resolution mascot source used by the cursor generator

Suggested Windows mapping using animated cursors:

- Normal Select: `cursor-pack/ani/normal.ani`
- Help Select: `cursor-pack/ani/help.ani`
- Working In Background: `cursor-pack/ani/working.ani`
- Busy: `cursor-pack/ani/busy.ani`
- Precision Select: `cursor-pack/ani/precision.ani`
- Text Select: `cursor-pack/ani/text.ani`
- Handwriting: `cursor-pack/ani/handwriting.ani`
- Unavailable: `cursor-pack/ani/unavailable.ani`
- Vertical Resize: `cursor-pack/ani/ns-resize.ani`
- Horizontal Resize: `cursor-pack/ani/ew-resize.ani`
- Diagonal Resize 1: `cursor-pack/ani/nwse-resize.ani`
- Diagonal Resize 2: `cursor-pack/ani/nesw-resize.ani`
- Move: `cursor-pack/ani/move.ani`
- Alternate Select: `cursor-pack/ani/alternate.ani`
- Link Select: `cursor-pack/ani/link.ani`
- Location Select: `cursor-pack/ani/location.ani`
- Person Select: `cursor-pack/ani/person.ani`

On Windows, open `Settings > Bluetooth & devices > Mouse > Additional mouse settings > Pointers`, then browse to these files for each pointer role.

Regenerate the cursor pack:

```bash
python tools/build_cursor_pack.py \
  --pet-dir LESSERAFIM/CHAEWON \
  --out-dir LESSERAFIM/CHAEWON/cursor-pack \
  --source-image LESSERAFIM/CHAEWON/cursor-pack/source/mascot-base.png
```
