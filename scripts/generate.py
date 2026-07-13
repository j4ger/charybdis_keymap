#!/usr/bin/env python3
"""
HTML generation: assembles static assets + templates into an inlined HTML page.
"""

import json
import os
import sys
from pathlib import Path

# Ensure sibling imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import templater

_ROOT = Path(__file__).resolve().parent.parent
_TEMPLATES = _ROOT / 'templates'
_STATIC = _ROOT / 'static'


def render_html(data, title="QMK Keymap"):
    """Render a keymap data dict into a complete inlined HTML page."""
    context = {
        'title':        title,
        'layer_count':  len(data['layers']),
        'rows':         data['rows'],
        'cols':         data['cols'],
        'thumbs':       data['thumbs'],
        'layers_json':  json.dumps(data['layers'], indent=2),
        'base_css':     (_STATIC / 'style.css').read_text(encoding='utf-8'),
        'practice_css': (_STATIC / 'practice.css').read_text(encoding='utf-8'),
        'viz_js':       (_STATIC / 'viz.js').read_text(encoding='utf-8'),
        'practice_js':  (_STATIC / 'practice.js').read_text(encoding='utf-8'),
    }
    tpl = (_TEMPLATES / 'layout.html').read_text(encoding='utf-8')
    return templater.render_template(tpl, context)


if __name__ == '__main__':
    # Quick test
    import keymap_parser
    import sys as _sys
    d = keymap_parser.parse_keymap(
        str(_ROOT / 'keyboards' / 'bastardkb' / 'charybdis' / '3x5' / 'keymaps' / 'j4ger' / 'keymap.c')
    )
    _sys.stdout.write(render_html(d, 'test'))
