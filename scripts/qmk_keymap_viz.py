#!/usr/bin/env python3
"""QMK Keymap Visualizer — CLI entry point.

Parses a QMK keymap.c and generates an interactive HTML visualization.
"""

import os
import sys
import argparse
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from keymap_parser import parse_keymap
from generate import render_html


def main():
    parser = argparse.ArgumentParser(
        description='Generate an interactive HTML visualization of a QMK keymap.c'
    )
    parser.add_argument('keymap', help='Path to keymap.c')
    parser.add_argument('-o', '--output', help='Output HTML file (default: <keymap_dir>/keymap_viz.html)')
    parser.add_argument('-t', '--title', default=None, help='Title for the visualization')

    args = parser.parse_args()
    keymap_path = Path(args.keymap)

    if not keymap_path.exists():
        print(f"Error: {keymap_path} not found", file=sys.stderr)
        sys.exit(1)

    # Parse
    data = parse_keymap(keymap_path)

    # Generate title
    title = args.title
    if not title:
        # Try to get keyboard name from path
        parts = keymap_path.parts
        for i, p in enumerate(parts):
            if p == 'keymaps' and i > 0:
                title = parts[i-1].replace('_', ' ').title()
                break
        if not title:
            title = keymap_path.stem.replace('_', ' ').title()

    # Generate HTML
    html = render_html(data, title)

    # Output
    if args.output:
        out_path = Path(args.output)
    else:
        out_path = keymap_path.parent / 'keymap_viz.html'

    out_path.write_text(html, encoding='utf-8')
    print(f"\u2713 Generated: {out_path}", file=sys.stderr)
    print(str(out_path))


if __name__ == '__main__':
    main()
