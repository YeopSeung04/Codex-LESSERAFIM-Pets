# CHAEWON Codex Pet

Compact chibi Codex desktop pet packaged for the Codex custom pet system.

## Files

- `pet.json`: Codex pet manifest
- `spritesheet.webp`: final transparent atlas, `1536x1872`
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

