#!/usr/bin/env python3
"""Tests for qmk_keymap_viz.py using only the Python standard library."""

import os
import sys

# ── Dynamic import ───────────────────────────────────────────────────────

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_REAL_KEYMAP = os.path.join(
    _SCRIPT_DIR, '..',
    'keyboards', 'bastardkb', 'charybdis', '3x5', 'keymaps', 'j4ger', 'keymap.c',
)

# Import keymap_parser directly (parsing moved to its own module)
sys.path.insert(0, os.path.join(_SCRIPT_DIR, '..', 'scripts'))
import keymap_parser  # noqa: E402
parse_keymap = keymap_parser.parse_keymap
finger_for = keymap_parser.finger_for

import generate
generate_html = generate.render_html

# ── Tests ────────────────────────────────────────────────────────────────

def test_parse_keymap():
    data = parse_keymap(_REAL_KEYMAP)

    # Top-level layout dimensions
    assert data['rows'] == 3, f"rows: expected 3, got {data['rows']}"
    assert data['cols'] == 5, f"cols: expected 5, got {data['cols']}"
    assert data['thumbs'] == 3, f"thumbs: expected 3, got {data['thumbs']}"

    layers = data['layers']
    assert len(layers) == 9, f"layers count: expected 9, got {len(layers)}"

    # Base layer (index 0) key counts
    base = layers[0]
    left_rows = base['left']['rows']
    right_rows = base['right']['rows']
    left_thumbs = base['left']['thumbs']
    right_thumbs = base['right']['thumbs']

    matrix_total = sum(len(row) for row in left_rows) + sum(len(row) for row in right_rows)
    assert matrix_total == 30, f"base matrix keys: expected 30, got {matrix_total}"

    thumb_total = len(left_thumbs) + len(right_thumbs)
    assert thumb_total == 5, f"base thumbs: expected 5, got {thumb_total}"

    total = matrix_total + thumb_total
    assert total == 35, f"base total keys: expected 35, got {total}"

    # Thumb label assertions
    left_thumb_labels = [k['label'] for k in left_thumbs]
    assert left_thumb_labels == ['Bksp', 'Space', 'Enter'], (
        f"left thumb labels: expected ['Bksp','Space','Enter'], got {left_thumb_labels}"
    )

    right_thumb_labels = [k['label'] for k in right_thumbs]
    assert right_thumb_labels == ['Esc', 'Tab'], (
        f"right thumb labels: expected ['Esc','Tab'], got {right_thumb_labels}"
    )


def test_html_markers():
    data = parse_keymap(_REAL_KEYMAP)
    html = generate_html(data, 't')

    markers = ['id="practicePanel"', 'CODE_TO_POS', 'const LAYERS', 'data-pos', 'id="numbersToggle"', 'id="symbolsToggle"', 'generatePrompt', 'id="layerDrillToggle"', 'charToChord', 'buildChordIndex']
    for marker in markers:
        assert marker in html, f"expected marker {marker!r} not found in generated HTML"


def test_finger_for():
    assert finger_for('L', 0) == 'left pinky'
    assert finger_for('R', 4) == 'right pinky'
    assert finger_for('L', 2) == 'left middle'


# ── Runner ───────────────────────────────────────────────────────────────

def main():
    tests = [test_parse_keymap, test_html_markers, test_finger_for]
    failures = 0

    for test_fn in tests:
        name = test_fn.__name__
        try:
            test_fn()
            print(f'OK {name}')
        except Exception as exc:
            print(f'FAIL {name}: {exc}')
            failures += 1

    if failures == 0:
        print('All tests passed')
        sys.exit(0)
    else:
        print(f'{failures} tests failed')
        sys.exit(1)


if __name__ == '__main__':
    main()
