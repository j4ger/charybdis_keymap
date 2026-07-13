# QMK Userspace

This is the QMK Userspace for the Bastard Keyboards keymaps.

You can read how to compile your own keymap on the official docs here: [https://docs.bastardkb.com/fw/compile-firmware.html](https://docs.bastardkb.com/fw/compile-firmware.html).

## Keymap Visualizer & Practice

This repo ships a self-contained Python visualizer (`scripts/qmk_keymap_viz.py`) that parses a QMK `keymap.c` and emits a single static `index.html` with an interactive, dark-themed keyboard diagram, layer tabs, search, and a built-in **typing practice** mode.

### File layout

The generator was recently split from a single script into a modular structure:

- `scripts/qmk_keymap_viz.py` — CLI entry point
- `scripts/keymap_parser.py` — QMK keymap.c parsing
- `scripts/generate.py` — HTML rendering (loads templates + static assets)
- `scripts/templater.py` — tiny `{{ var }}` templater
- `templates/layout.html` — HTML skeleton
- `static/` — CSS (`style.css`, `practice.css`) and JS (`viz.js`, `practice.js`)

The generated output is still a single self-contained `index.html` (all assets are inlined at build time).

### Local development

With Nix (provides python3):
```sh
nix develop
python3 scripts/qmk_keymap_viz.py keyboards/bastardkb/charybdis/3x5/keymaps/j4ger/keymap.c -o /tmp/viz.html
python3 -m http.server -d /tmp 8000
# open http://localhost:8000/viz.html
```

Without Nix (any python3):
```sh
python3 scripts/qmk_keymap_viz.py keyboards/bastardkb/charybdis/3x5/keymaps/j4ger/keymap.c -o viz.html
```

CI (`.github/workflows/build-viz.yml`) regenerates and deploys the page to GitHub Pages on every push that touches a `keymap.c` or the generator script; no extra setup is needed.

### Practice mode

Click **▶ Practice** under the title to enter practice mode (click again or **✕ Exit** to leave). Reference: monkeytype (words test, live WPM/accuracy, blinking caret, correct/incorrect char feedback) and keybr (on-screen keyboard highlighting the next key + finger hint).

- Set the word count (5–100), then type the prompt. A blinking caret marks your position; correct characters dim, incorrect ones get a red wavy underline.
- The on-screen keyboard highlights the **next key to press** and shows a **finger hint** (e.g. `Next: left index`).
- Live **WPM**, **Accuracy**, and **Progress** update as you type; a results panel appears at the end.
- **↻ Restart** for a new prompt, **✕ Exit** to return to the visualizer.

**Colemak emulator (on by default):** the page maps your physical QWERTY key positions to the keymap's actual layout (Colemak) using the parsed keymap data, so you can practice this Colemak keymap from any ordinary QWERTY keyboard. Turn it **off** if your OS is already set to Colemak — then your typed characters are compared directly.

Backspace is supported (raw accuracy is preserved; corrections don't reduce the error count). Paste is disabled during practice.

### Tests

```sh
python3 tests/test_viz.py
```
Stdlib-only; verifies keymap parsing (35 keys, 9 layers, thumb layout), HTML marker generation, and the finger-mapping helper.