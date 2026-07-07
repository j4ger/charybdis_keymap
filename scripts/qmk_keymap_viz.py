#!/usr/bin/env python3
"""
QMK Keymap Visualizer
=====================
Parses a QMK keymap.c and generates an interactive HTML visualization.

Usage:
    python3 qmk_keymap_viz.py <keymap.c> [-o output.html]

Supports:
    - Layer definitions via LAYOUT() macro
    - QMK keycodes (KC_*, LT, MO, TO, TG, OSL, OSM, etc.)
    - Custom #define macros (resolves nested expansion)
    - Home row mods (LGUI_T, LALT_T, etc.)
    - Dead/transparent keys (XXXXXXX, _______, KC_TRNS)
"""

import re
import sys
import json
import argparse
from pathlib import Path

# ─── QMK Keycode Mapping ────────────────────────────────────────────────

# Basic key labels (KC_* → human readable)
KC_MAP = {
    # Letters
    'KC_A': 'A', 'KC_B': 'B', 'KC_C': 'C', 'KC_D': 'D', 'KC_E': 'E',
    'KC_F': 'F', 'KC_G': 'G', 'KC_H': 'H', 'KC_I': 'I', 'KC_J': 'J',
    'KC_K': 'K', 'KC_L': 'L', 'KC_M': 'M', 'KC_N': 'N', 'KC_O': 'O',
    'KC_P': 'P', 'KC_Q': 'Q', 'KC_R': 'R', 'KC_S': 'S', 'KC_T': 'T',
    'KC_U': 'U', 'KC_V': 'V', 'KC_W': 'W', 'KC_X': 'X', 'KC_Y': 'Y',
    'KC_Z': 'Z',
    # Numbers
    'KC_1': '1', 'KC_2': '2', 'KC_3': '3', 'KC_4': '4', 'KC_5': '5',
    'KC_6': '6', 'KC_7': '7', 'KC_8': '8', 'KC_9': '9', 'KC_0': '0',
    # Symbols
    'KC_MINS': '-', 'KC_EQL': '=', 'KC_LBRC': '[', 'KC_RBRC': ']',
    'KC_BSLS': '\\', 'KC_SCLN': ';', 'KC_QUOT': "'", 'KC_GRV': '`',
    'KC_COMM': ',', 'KC_DOT': '.', 'KC_SLSH': '/', 'KC_NUBS': '\\',
    # Shifted symbols (for symbol layers)
    'KC_EXLM': '!', 'KC_AT': '@', 'KC_HASH': '#', 'KC_DLR': '$',
    'KC_PERC': '%', 'KC_CIRC': '^', 'KC_AMPR': '&', 'KC_ASTR': '*',
    'KC_LPRN': '(', 'KC_RPRN': ')', 'KC_LCBR': '{', 'KC_RCBR': '}',
    'KC_PIPE': '|', 'KC_TILD': '~', 'KC_PLUS': '+', 'KC_COLN': ':',
    'KC_UNDS': '_',
    # Control keys
    'KC_ESC': 'Esc', 'KC_ENT': 'Enter', 'KC_SPC': 'Space', 'KC_BSPC': 'Bksp',
    'KC_TAB': 'Tab', 'KC_CAPS': 'Caps', 'KC_DEL': 'Del', 'KC_INS': 'Ins',
    'KC_PSCR': 'PrtSc', 'KC_SCRL': 'ScrLk', 'KC_PAUS': 'Pause',
    'KC_BRK': 'Break', 'KC_NLCK': 'NumLk',
    # Navigation
    'KC_LEFT': '←', 'KC_DOWN': '↓', 'KC_UP': '↑', 'KC_RGHT': '→',
    'KC_HOME': 'Home', 'KC_END': 'End', 'KC_PGUP': 'PgUp', 'KC_PGDN': 'PgDn',
    # Function keys
    'KC_F1': 'F1', 'KC_F2': 'F2', 'KC_F3': 'F3', 'KC_F4': 'F4',
    'KC_F5': 'F5', 'KC_F6': 'F6', 'KC_F7': 'F7', 'KC_F8': 'F8',
    'KC_F9': 'F9', 'KC_F10': 'F10', 'KC_F11': 'F11', 'KC_F12': 'F12',
    # Media
    'KC_MPLY': '▶️', 'KC_MSTP': '⏹', 'KC_MPRV': '⏮', 'KC_MNXT': '⏭',
    'KC_MUTE': 'Mute', 'KC_VOLU': 'Vol+', 'KC_VOLD': 'Vol−',
    'KC_MSEL': 'Media', 'KC_EJCT': 'Eject',
    # Modifiers
    'KC_LSFT': 'LShift', 'KC_RSFT': 'RShift', 'KC_LCTL': 'LCtrl',
    'KC_RCTL': 'RCtrl', 'KC_LALT': 'LAlt', 'KC_RALT': 'RAlt',
    'KC_LGUI': 'LGui', 'KC_RGUI': 'RGui', 'KC_LCMD': 'LCmd',
    'KC_RCMD': 'RCmd', 'KC_LOPT': 'LOpt', 'KC_ROPT': 'ROpt',
    'KC_LSFT': 'LShift', 'KC_RSFT': 'RShift',
    # Mod taps
    'LCTL_T': 'LCTL', 'RCTL_T': 'RCTL', 'LSFT_T': 'LSFT', 'RSFT_T': 'RSFT',
    'LALT_T': 'LALT', 'RALT_T': 'RALT', 'LGUI_T': 'LGUI', 'RGUI_T': 'RGUI',
    'LOPT_T': 'LOPT', 'ROPT_T': 'ROPT', 'LCMD_T': 'LCMD', 'RCMD_T': 'RCMD',
    # Mouse
    'KC_BTN1': 'LMB', 'KC_BTN2': 'RMB', 'KC_BTN3': 'MMB',
    'KC_BTN4': 'MB4', 'KC_BTN5': 'MB5', 'KC_MS_U': 'Mouse↑',
    'KC_MS_D': 'Mouse↓', 'KC_MS_L': 'Mouse←', 'KC_MS_R': 'Mouse→',
    'KC_WH_U': 'Wheel↑', 'KC_WH_D': 'Wheel↓', 'KC_WH_L': 'Wheel←',
    'KC_WH_R': 'Wheel→', 'KC_ACL0': 'Accel0', 'KC_ACL1': 'Accel1',
    'KC_ACL2': 'Accel2',
    # QMK special
    'KC_TRNS': '▽', 'KC_TRANSPARENT': '▽',
    'XXXXXXX': '×', 'KC_NO': '×',
    'QK_BOOT': 'Reset', 'QK_REBOOT': 'Reboot',
    'EE_CLR': 'EE_CLR', 'EEP_RST': 'EE_CLR',
    'RGB_TOG': 'RGB', 'RGB_MOD': 'RGB→', 'RGB_RMOD': 'RGB←',
    'RGB_HUI': 'Hue+', 'RGB_HUD': 'Hue-', 'RGB_SAI': 'Sat+',
    'RGB_SAD': 'Sat-', 'RGB_VAI': 'Bri+', 'RGB_VAD': 'Bri-',
    'SNIPING': 'Snipe', 'DRGSCRL': 'DragScrl', 'DRAGSCROLL': 'DragScrl',
    'DPI_MOD': 'DPI+', 'S_D_MOD': 'SnpDPI+',
}

# Key type classification for coloring
KEY_TYPE_MAP = {
    # Modifiers
    'KC_LSFT': 'mod', 'KC_RSFT': 'mod', 'KC_LCTL': 'mod', 'KC_RCTL': 'mod',
    'KC_LALT': 'mod', 'KC_RALT': 'mod', 'KC_LGUI': 'mod', 'KC_RGUI': 'mod',
    'KC_LCMD': 'mod', 'KC_RCMD': 'mod', 'KC_LOPT': 'mod', 'KC_ROPT': 'mod',
    # Function keys
    'KC_F1': 'fn', 'KC_F2': 'fn', 'KC_F3': 'fn', 'KC_F4': 'fn',
    'KC_F5': 'fn', 'KC_F6': 'fn', 'KC_F7': 'fn', 'KC_F8': 'fn',
    'KC_F9': 'fn', 'KC_F10': 'fn', 'KC_F11': 'fn', 'KC_F12': 'fn',
    'KC_PSCR': 'fn', 'KC_SCRL': 'fn', 'KC_PAUS': 'fn', 'KC_BRK': 'fn',
    # Navigation
    'KC_LEFT': 'nav', 'KC_DOWN': 'nav', 'KC_UP': 'nav', 'KC_RGHT': 'nav',
    'KC_HOME': 'nav', 'KC_END': 'nav', 'KC_PGUP': 'nav', 'KC_PGDN': 'nav',
    'KC_CAPS': 'nav', 'KC_INS': 'nav', 'KC_DEL': 'nav',
    # Media
    'KC_MPLY': 'media', 'KC_MSTP': 'media', 'KC_MPRV': 'media', 'KC_MNXT': 'media',
    'KC_MUTE': 'media', 'KC_VOLU': 'media', 'KC_VOLD': 'media',
    'KC_MSEL': 'media', 'KC_EJCT': 'media',
    'RGB_TOG': 'media', 'RGB_MOD': 'media', 'RGB_RMOD': 'media',
    'RGB_HUI': 'media', 'RGB_HUD': 'media', 'RGB_SAI': 'media',
    'RGB_SAD': 'media', 'RGB_VAI': 'media', 'RGB_VAD': 'media',
    # Mouse
    'KC_BTN1': 'mouse', 'KC_BTN2': 'mouse', 'KC_BTN3': 'mouse',
    'KC_BTN4': 'mouse', 'KC_BTN5': 'mouse', 'KC_MS_U': 'mouse',
    'KC_MS_D': 'mouse', 'KC_MS_L': 'mouse', 'KC_MS_R': 'mouse',
    'KC_WH_U': 'mouse', 'KC_WH_D': 'mouse', 'KC_WH_L': 'mouse',
    'KC_WH_R': 'mouse', 'SNIPING': 'mouse', 'DRGSCRL': 'mouse',
    'DRAGSCROLL': 'mouse', 'DPI_MOD': 'mouse', 'S_D_MOD': 'mouse',
    # Special
    'KC_TRNS': 'dead', 'KC_TRANSPARENT': 'dead', 'XXXXXXX': 'dead', 'KC_NO': 'dead',
    'QK_BOOT': 'media', 'QK_REBOOT': 'media', 'EE_CLR': 'media', 'EEP_RST': 'media',
}

# Layer colors for visualization
LAYER_COLORS = {
    'default': 'var(--accent)',
    'lower': 'var(--pink)',
    'raise': 'var(--purple)',
    'adjust': 'var(--yellow)',
    'function': 'var(--purple)',
    'nav': 'var(--cyan)',
    'navigation': 'var(--cyan)',
    'media': 'var(--accent)',
    'mouse': 'var(--red)',
    'pointer': 'var(--red)',
    'num': 'var(--yellow)',
    'numeral': 'var(--yellow)',
    'number': 'var(--yellow)',
    'symbol': 'var(--pink)',
    'symbols': 'var(--pink)',
    'gaming': 'var(--green)',
    'game': 'var(--green)',
    'base': 'var(--accent)',
}


# ─── Preprocessor ────────────────────────────────────────────────────────

class Preprocessor:
    """C preprocessor that handles #define macros with cycle detection."""

    def __init__(self):
        self.macros = {}  # name -> (params, body)

    def add_macro(self, name, params, body):
        self.macros[name] = (params, body)

    def _find_call(self, text, name):
        """Find a call to macro `name(text)` in text. Returns (start, end, args_str) or None."""
        pattern = r'\b' + re.escape(name) + r'\s*\('
        m = re.search(pattern, text)
        if not m:
            return None
        start = m.start()
        paren_start = m.end()
        depth = 1
        i = paren_start
        while i < len(text) and depth > 0:
            if text[i] == '(':
                depth += 1
            elif text[i] == ')':
                depth -= 1
            i += 1
        if depth != 0:
            return None
        return (start, i, text[paren_start:i-1])

    def _split_args(self, s):
        """Split macro arguments respecting nested parens."""
        args = []
        depth = 0
        current = []
        for ch in s:
            if ch == '(':
                depth += 1
                current.append(ch)
            elif ch == ')':
                depth -= 1
                current.append(ch)
            elif ch == ',' and depth == 0:
                args.append(''.join(current).strip())
                current = []
            else:
                current.append(ch)
        if current:
            args.append(''.join(current).strip())
        return args

    def expand(self, text, max_iterations=50, _depth=0):
        """Expand macros with fixed-point iteration and cycle detection."""
        if _depth > 15:
            return text

        seen = set()
        for iteration in range(max_iterations):
            old = text

            # Expand function-like macros (innermost first: longest name match)
            func_names = [(n, p, b) for n, (p, b) in self.macros.items() if p is not None]
            func_names.sort(key=lambda x: -len(x[0]))

            for name, params, body in func_names:
                is_variadic = params and '...' in params
                named_params = [p for p in params if p != '...'] if params else []
                min_args = len(named_params)

                safety = 0
                while safety < 20:
                    safety += 1
                    result = self._find_call(text, name)
                    if result is None:
                        break
                    start, end, args_str = result
                    args = self._split_args(args_str)

                    # Expand each argument to resolve nested macros
                    expanded_args = []
                    for a in args:
                        ea = self.expand(a.strip(), max_iterations=10, _depth=_depth+1)
                        # Split expanded arg by commas in case it produced multiple values
                        sub_args = self._split_args(ea)
                        expanded_args.extend([s.strip() for s in sub_args if s.strip()])

                    if is_variadic and len(expanded_args) >= min_args:
                        expanded = body
                        for i, param in enumerate(named_params):
                            expanded = expanded.replace(param, expanded_args[i])
                        va_args = ', '.join(expanded_args[min_args:])
                        expanded = expanded.replace('__VA_ARGS__', va_args)
                        text = text[:start] + expanded + text[end:]
                    elif not is_variadic and len(expanded_args) == len(params):
                        expanded = body
                        for param, arg in zip(params, expanded_args):
                            expanded = expanded.replace(param, arg)
                        text = text[:start] + expanded + text[end:]
                    else:
                        break

            # Expand object-like macros
            obj_names = [(n, b) for n, (p, b) in self.macros.items() if p is None]
            obj_names.sort(key=lambda x: -len(x[0]))
            for name, body in obj_names:
                text = re.sub(r'\b' + re.escape(name) + r'\b', body, text)

            if text == old:
                break  # fixed point reached

            # Cycle detection
            h = hash(text)
            if h in seen:
                break
            seen.add(h)

        return text


# ─── Parser ──────────────────────────────────────────────────────────────

def preprocess_file(text):
    """Remove comments and join line continuations."""
    # Remove // comments
    text = re.sub(r'//[^\n]*', '', text)
    # Remove /* */ comments
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
    # Join line continuations
    text = re.sub(r'\\\n', '', text)
    return text


def parse_defines(text):
    """Extract #define macros from the source."""
    macros = {}

    # Process line by line, handling multi-line defines (backslash continuations already joined)
    for m in re.finditer(r'#\s*define\s+(\w+)(?:\(([^)]*)\))?\s+(.*)', text):
        name = m.group(1)
        param_str = m.group(2)
        body = m.group(3).strip()

        if param_str is not None:
            # Handle variadic macros: ... and __VA_ARGS__
            params = [p.strip() for p in param_str.split(',') if p.strip()]
        else:
            params = None

        macros[name] = (params, body)

    return macros


def parse_layers(source_text, preprocessor):
    """Parse layer definitions from keymaps array."""
    layers = []

    # First, expand macros in the entire source
    expanded_source = preprocessor.expand(source_text)

    # Find the keymaps array in expanded source
    keymap_match = re.search(
        r'const\s+uint16_t\s+PROGMEM\s+keymaps\s*\[.*?\]\s*=\s*\{(.*?)(?:\n\};|\};)',
        expanded_source, re.DOTALL
    )
    if not keymap_match:
        # Try alternative: look for LAYOUT_wrapper(...) entries in original source
        # and expand each one individually
        return parse_layers_from_defines(source_text, preprocessor)

    keymap_body = keymap_match.group(1)

    # Extract layer enum names from original source
    layer_names = {}
    enum_match = re.search(
        r'enum\s+\w*\s*\{([^}]+)\}',
        source_text, re.DOTALL
    )
    if enum_match:
        enum_body = enum_match.group(1)
        idx = 0
        for line in enum_body.split(','):
            line = line.strip()
            if not line or line.startswith('//'):
                continue
            parts = line.split('=')
            name = parts[0].strip()
            if len(parts) > 1:
                try:
                    idx = int(parts[1].strip())
                except ValueError:
                    pass
            layer_names[idx] = name
            idx += 1

    # Parse each layer entry with balanced paren matching
    layer_pattern = r'\[(\w+)\]\s*=\s*(?:LAYOUT_wrapper|LAYOUT)\s*\('
    for m in re.finditer(layer_pattern, keymap_body):
        layer_idx_str = m.group(1)
        paren_start = m.end()

        # Find matching closing paren
        depth = 1
        i = paren_start
        while i < len(keymap_body) and depth > 0:
            if keymap_body[i] == '(':
                depth += 1
            elif keymap_body[i] == ')':
                depth -= 1
            i += 1

        layer_body = keymap_body[paren_start:i-1].strip()

        try:
            layer_idx = int(layer_idx_str)
        except ValueError:
            layer_idx = len(layers)
            for idx, name in layer_names.items():
                if name == layer_idx_str:
                    layer_idx = idx
                    break

        layer_name = layer_names.get(layer_idx, f'layer_{layer_idx}')

        keycodes = split_keycodes(layer_body)

        layers.append({
            'index': layer_idx,
            'name': layer_name,
            'keycodes': keycodes,
        })

    layers.sort(key=lambda x: x['index'])
    return layers


def split_keycodes(s):
    """Split a comma-separated list of keycodes respecting nested parens."""
    args = []
    depth = 0
    current = []
    for ch in s:
        if ch == '(':
            depth += 1
            current.append(ch)
        elif ch == ')':
            depth -= 1
            current.append(ch)
        elif ch == ',' and depth == 0:
            args.append(''.join(current).strip())
            current = []
        else:
            current.append(ch)
    if current:
        args.append(''.join(current).strip())
    return [k for k in args if k]


def parse_layers_from_defines(source_text, preprocessor):
    """Fallback: parse layers from #define LAYOUT_LAYER_* and the keymaps array."""
    layers = []

    # Extract layer enum names
    layer_names = {}
    enum_match = re.search(
        r'enum\s+\w*\s*\{([^}]+)\}',
        source_text, re.DOTALL
    )
    if enum_match:
        enum_body = enum_match.group(1)
        idx = 0
        for line in enum_body.split(','):
            line = line.strip()
            if not line or line.startswith('//'):
                continue
            parts = line.split('=')
            name = parts[0].strip()
            if len(parts) > 1:
                try:
                    idx = int(parts[1].strip())
                except ValueError:
                    pass
            layer_names[idx] = name
            idx += 1

    # Find the keymaps array entries to know which layer index maps to which define
    keymap_section = re.search(
        r'const\s+uint16_t\s+PROGMEM\s+keymaps\s*\[.*?\]\s*=\s*\{(.*?)\};',
        source_text, re.DOTALL
    )
    if not keymap_section:
        return []

    keymap_body = keymap_section.group(1)

    # Parse each entry: [IDX] = LAYOUT_wrapper(MACRO_NAME) or LAYOUT(...)
    entry_pattern = r'\[(\w+)\]\s*=\s*(?:LAYOUT_wrapper|LAYOUT)\s*\('
    for m in re.finditer(entry_pattern, keymap_body):
        layer_idx_str = m.group(1)
        paren_start = m.end()

        # Find matching closing paren
        depth = 1
        i = paren_start
        while i < len(keymap_body) and depth > 0:
            if keymap_body[i] == '(':
                depth += 1
            elif keymap_body[i] == ')':
                depth -= 1
            i += 1

        inner = keymap_body[paren_start:i-1].strip()

        try:
            layer_idx = int(layer_idx_str)
        except ValueError:
            layer_idx = len(layers)
            for idx, name in layer_names.items():
                if name == layer_idx_str:
                    layer_idx = idx
                    break

        layer_name = layer_names.get(layer_idx, f'layer_{layer_idx}')

        # Try to expand this layer's content
        expanded = preprocessor.expand(inner)
        keycodes = split_keycodes(expanded)

        # If expansion didn't produce recognizable keycodes, try resolving
        # the inner macro name directly
        if len(keycodes) < 5:
            # inner might be like POINTER_MOD(HOME_ROW_MOD_GACS(LAYOUT_LAYER_BASE))
            # or just LAYOUT_LAYER_FUNCTION
            # Try to find the LAYOUT_LAYER_* define and expand from there
            layer_define_match = re.search(
                r'#\s*define\s+(LAYOUT_LAYER_' + re.escape(layer_name.upper()) + r')\b.*?\\\n((?:.*\\\n)*.*)',
                source_text, re.DOTALL
            )
            if not layer_define_match:
                # Try without LAYER_ prefix
                layer_define_match = re.search(
                    r'#\s*define\s+(LAYOUT_' + re.escape(layer_name.upper()) + r')\b.*?\\\n((?:.*\\\n)*.*)',
                    source_text, re.DOTALL
                )
            if layer_define_match:
                define_body = layer_define_match.group(2)
                define_body = re.sub(r'\\\n', '', define_body)
                define_body = re.sub(r'\s+', ' ', define_body).strip()
                expanded = preprocessor.expand(define_body)
                keycodes = split_keycodes(expanded)

        layers.append({
            'index': layer_idx,
            'name': layer_name,
            'keycodes': keycodes,
        })

    layers.sort(key=lambda x: x['index'])
    return layers


def classify_key(keycode):
    """Return (label, sub_label, key_type, layer_target) for a keycode."""
    label = keycode
    sub = ''
    key_type = 'alpha'
    layer_target = None

    # Special: transparent / dead
    if keycode in ('XXXXXXX', 'KC_NO', '_______', 'KC_TRNS', 'KC_TRANSPARENT'):
        return ('×' if 'X' in keycode or keycode == 'KC_NO' else '▽',
                '', 'dead', None)

    # Layer tap: LT(layer, key)
    m = re.match(r'LT\s*\(\s*(\w+)\s*,\s*(\w+)\s*\)', keycode)
    if m:
        layer_target = m.group(1)
        inner = m.group(2)
        inner_label = KC_MAP.get(inner, inner.replace('KC_', ''))
        layer_name = layer_target.replace('LAYER_', '').replace('_', ' ').title()
        return (inner_label, f'↕ {layer_name}', 'layer-trigger', layer_target)

    # LT with numeric layer index
    m = re.match(r'LT\s*\(\s*(\d+)\s*,\s*(\w+)\s*\)', keycode)
    if m:
        layer_idx = m.group(1)
        inner = m.group(2)
        inner_label = KC_MAP.get(inner, inner.replace('KC_', ''))
        return (inner_label, f'↕ Layer {layer_idx}', 'layer-trigger', f'layer_{layer_idx}')

    # MO(layer)
    m = re.match(r'MO\s*\(\s*(\w+)\s*\)', keycode)
    if m:
        layer_target = m.group(1)
        layer_name = layer_target.replace('LAYER_', '').replace('_', ' ').title()
        return (f'MO', f'→ {layer_name}', 'layer-trigger', layer_target)

    # TO(layer)
    m = re.match(r'TO\s*\(\s*(\w+)\s*\)', keycode)
    if m:
        layer_target = m.group(1)
        layer_name = layer_target.replace('LAYER_', '').replace('_', ' ').title()
        return ('TO', f'→ {layer_name}', 'layer-trigger', layer_target)

    # TG(layer)
    m = re.match(r'TG\s*\(\s*(\w+)\s*\)', keycode)
    if m:
        layer_target = m.group(1)
        layer_name = layer_target.replace('LAYER_', '').replace('_', ' ').title()
        return ('TG', f'↔ {layer_name}', 'layer-trigger', layer_target)

    # OSL(layer)
    m = re.match(r'OSL\s*\(\s*(\w+)\s*\)', keycode)
    if m:
        layer_target = m.group(1)
        layer_name = layer_target.replace('LAYER_', '').replace('_', ' ').title()
        return ('OSL', f'→ {layer_name}', 'layer-trigger', layer_target)

    # OSM(mod)
    m = re.match(r'OSM\s*\(\s*(\w+)\s*\)', keycode)
    if m:
        mod = m.group(1).replace('MOD_', '').replace('_T', '')
        return (mod, 'one-shot', 'mod', None)

    # Mod-tap: LGUI_T(kc), LALT_T(kc), etc.
    mod_tap_match = re.match(r'(\w+_T)\s*\(\s*(\w+)\s*\)', keycode)
    if mod_tap_match:
        mod_fn = mod_tap_match.group(1)
        inner = mod_tap_match.group(2)
        inner_label = KC_MAP.get(inner, inner.replace('KC_', ''))
        mod_name = mod_fn.replace('_T', '')
        mod_symbol = {
            'LGUI': '⌘', 'RGUI': '⌘', 'LALT': '⌥', 'RALT': '⌥',
            'LCTL': '⌃', 'RCTL': '⌃', 'LSFT': '⇧', 'RSFT': '⇧',
            'LOPT': '⌥', 'ROPT': '⌥', 'LCMD': '⌘', 'RCMD': '⌘',
        }.get(mod_name, mod_name)
        return (inner_label, f'{mod_symbol} {mod_name}', 'mod', None)

    # Standard KC code
    if keycode in KC_MAP:
        label = KC_MAP[keycode]
        key_type = KEY_TYPE_MAP.get(keycode, 'alpha')
        return (label, '', key_type, None)

    # QK_BOOT, etc.
    if keycode in KC_MAP:
        return (KC_MAP[keycode], '', KEY_TYPE_MAP.get(keycode, 'media'), None)

    # Fallback: clean up the name
    label = keycode.replace('KC_', '').replace('QK_', '').replace('_', ' ')
    return (label, '', 'alpha', None)


def detect_keyboard_layout(layers):
    """Try to detect the keyboard layout (rows/cols per side) from key count.
    Returns (rows, cols, thumb_per_side, left_keys_per_side, right_keys_per_side)."""
    if not layers:
        return 3, 5, 3, 18, 18

    keycodes = layers[0]['keycodes']
    n = len(keycodes)

    # Try asymmetric layouts too: total = rows*cols*2 + thumb_l + thumb_r
    best = None
    best_score = -1
    for rows in range(2, 6):
        for cols in range(3, 8):
            for thumb_l in range(0, 6):
                for thumb_r in range(0, 6):
                    total = rows * cols * 2 + thumb_l + thumb_r
                    if total == n:
                        score = (1 if rows == 3 else 0) + (1 if cols == 5 else 0) + (1 if thumb_l >= 2 else 0) + (1 if thumb_r >= 2 else 0)
                        if score > best_score:
                            best_score = score
                            best = (rows, cols, max(thumb_l, thumb_r), rows * cols + thumb_l, rows * cols + thumb_r)
    if best:
        return best

    # Fallback
    half = n // 2
    return 3, 5, max(0, half - 15), half, n - half


def parse_keymap(keymap_path):
    """Main parsing function. Returns structured data for visualization."""
    source = Path(keymap_path).read_text(encoding='utf-8')
    clean = preprocess_file(source)

    # Parse #defines
    defines = parse_defines(clean)
    preprocessor = Preprocessor()
    for name, (params, body) in defines.items():
        preprocessor.add_macro(name, params, body)

    # Parse layers
    layers = parse_layers(clean, preprocessor)

    if not layers:
        print("Error: No layers found in keymap.c", file=sys.stderr)
        sys.exit(1)

    # Detect layout
    rows, cols, thumbs, left_per_side, right_per_side = detect_keyboard_layout(layers)
    print(f"Detected layout: {rows} rows × {cols} cols + {thumbs} thumb keys per side "
          f"({len(layers[0]['keycodes'])} total keys per layer)", file=sys.stderr)
    print(f"Found {len(layers)} layers: {', '.join(l['name'] for l in layers)}",
          file=sys.stderr)

    # Classify each key in each layer
    processed_layers = []
    for layer in layers:
        all_kcs = layer['keycodes']

        def make_key(kc):
            label, sub, ktype, target = classify_key(kc)
            return {'label': label, 'sub': sub, 'type': ktype, 'layer': target, 'raw': kc}

        # Layout is interleaved: [top_L, top_R, mid_L, mid_R, bot_L, bot_R, thumb_L, thumb_R]
        left_rows = []
        right_rows = []
        for r in range(rows):
            row_offset = r * cols * 2
            left_row = [make_key(all_kcs[row_offset + c]) for c in range(cols)]
            right_row = [make_key(all_kcs[row_offset + cols + c]) for c in range(cols)]
            left_rows.append(left_row)
            right_rows.append(right_row)

        thumb_offset = rows * cols * 2
        left_thumbs = [make_key(all_kcs[thumb_offset + i]) for i in range(left_per_side - rows * cols)]
        right_thumbs_start = thumb_offset + (left_per_side - rows * cols)
        right_thumbs = [make_key(all_kcs[right_thumbs_start + i]) for i in range(right_per_side - rows * cols)]

        processed_layers.append({
            'index': layer['index'],
            'name': layer['name'],
            'left': {'rows': left_rows, 'thumbs': left_thumbs},
            'right': {'rows': right_rows, 'thumbs': right_thumbs},
        })

    return {
        'rows': rows,
        'cols': cols,
        'thumbs': thumbs,
        'layers': processed_layers,
    }


# ─── HTML Generation ────────────────────────────────────────────────────

def generate_html(data, title="QMK Keymap"):
    """Generate the interactive HTML visualization."""
    layers_json = json.dumps(data['layers'], indent=2)

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} — Keymap Visualizer</title>
<style>
  :root {{
    --bg: #0d1117; --surface: #161b22; --border: #30363d;
    --text: #c9d1d9; --text-dim: #8b949e; --accent: #58a6ff;
    --green: #3fb950; --orange: #d29922; --red: #f85149;
    --purple: #bc8cff; --pink: #f778ba; --cyan: #39d353; --yellow: #e3b341;
  }}
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{
    font-family: 'SF Mono','Fira Code','JetBrains Mono',monospace;
    background: var(--bg); color: var(--text);
    min-height:100vh; display:flex; flex-direction:column;
    align-items:center; padding:24px 16px;
  }}
  h1 {{ font-size:1.4rem; font-weight:600; margin-bottom:4px; color:var(--accent); }}
  .subtitle {{ font-size:0.8rem; color:var(--text-dim); margin-bottom:20px; }}
  .search-box {{ max-width:400px; width:100%; margin-bottom:16px; }}
  .search-box input {{
    width:100%; padding:8px 14px; border:1px solid var(--border);
    border-radius:6px; background:var(--surface); color:var(--text);
    font-family:inherit; font-size:0.85rem; outline:none;
  }}
  .search-box input:focus {{ border-color:var(--accent); }}
  .search-box input::placeholder {{ color:var(--text-dim); }}
  .layer-tabs {{ display:flex; flex-wrap:wrap; gap:5px; justify-content:center; margin-bottom:18px; max-width:900px; }}
  .layer-tab {{
    padding:5px 12px; border:1px solid var(--border); border-radius:6px;
    background:var(--surface); color:var(--text-dim); cursor:pointer;
    font-size:0.75rem; font-family:inherit; transition:all .15s;
  }}
  .layer-tab:hover {{ border-color:var(--accent); color:var(--text); }}
  .layer-tab.active {{ background:var(--accent); color:#000; border-color:var(--accent); font-weight:600; }}
  .layer-tab .idx {{ font-size:0.6rem; opacity:0.5; display:block; }}
  .keyboard {{ display:flex; gap:28px; align-items:flex-start; margin-bottom:20px; }}
  .half {{ display:flex; flex-direction:column; gap:4px; }}
  .half-label {{ font-size:0.65rem; color:var(--text-dim); text-align:center; margin-bottom:4px; text-transform:uppercase; letter-spacing:1px; }}
  .row {{ display:flex; gap:4px; }}
  .key {{
    width:62px; height:50px; border:1px solid var(--border); border-radius:6px;
    display:flex; flex-direction:column; align-items:center; justify-content:center;
    font-size:0.72rem; line-height:1.2; cursor:default; transition:all .15s;
    position:relative; background:var(--surface); user-select:none;
  }}
  .key:hover {{ border-color:var(--accent); transform:translateY(-1px); box-shadow:0 2px 8px rgba(88,166,255,.15); }}
  .key .label {{ font-weight:600; font-size:0.82rem; }}
  .key .sub {{ font-size:0.58rem; color:var(--text-dim); margin-top:1px; }}
  .thumb-row {{ display:flex; gap:4px; justify-content:center; margin-top:5px; }}
  .key.thumb {{ width:70px; height:42px; border-radius:8px; }}
  .key.layer-trigger {{ border-color:var(--accent); background:rgba(88,166,255,.08); cursor:pointer; }}
  .key.layer-trigger:hover {{ background:rgba(88,166,255,.18); }}
  .key.alpha {{ background:var(--surface); }}
  .key.mod {{ background:rgba(210,153,34,.12); border-color:rgba(210,153,34,.3); }}
  .key.mod .label {{ color:var(--orange); }}
  .key.fn {{ background:rgba(188,140,255,.1); border-color:rgba(188,140,255,.3); }}
  .key.fn .label {{ color:var(--purple); }}
  .key.nav {{ background:rgba(57,211,83,.1); border-color:rgba(57,211,83,.3); }}
  .key.nav .label {{ color:var(--cyan); }}
  .key.symbol {{ background:rgba(247,120,186,.1); border-color:rgba(247,120,186,.3); }}
  .key.symbol .label {{ color:var(--pink); }}
  .key.number {{ background:rgba(227,179,65,.1); border-color:rgba(227,179,65,.3); }}
  .key.number .label {{ color:var(--yellow); }}
  .key.mouse {{ background:rgba(248,81,73,.1); border-color:rgba(248,81,73,.3); }}
  .key.mouse .label {{ color:var(--red); }}
  .key.media {{ background:rgba(88,166,255,.08); border-color:rgba(88,166,255,.25); }}
  .key.media .label {{ color:var(--accent); }}
  .key.dead {{ background:transparent; border-color:rgba(48,54,61,.3); opacity:0.35; }}
  .key.dead:hover {{ transform:none; box-shadow:none; border-color:rgba(48,54,61,.3); }}
  .key.search-match {{ border-color:var(--accent)!important; box-shadow:0 0 8px rgba(88,166,255,.4); opacity:1!important; }}
  .key.search-dim {{ opacity:0.25; }}
  .legend {{ display:flex; flex-wrap:wrap; gap:10px; justify-content:center; margin-bottom:18px; }}
  .legend-item {{ display:flex; align-items:center; gap:5px; font-size:0.68rem; color:var(--text-dim); }}
  .legend-swatch {{ width:11px; height:11px; border-radius:3px; border:1px solid var(--border); }}
  .info-panel {{
    max-width:700px; width:100%; background:var(--surface);
    border:1px solid var(--border); border-radius:8px; padding:14px 18px;
  }}
  .info-panel h3 {{ font-size:0.85rem; color:var(--accent); margin-bottom:6px; }}
  .info-panel p {{ font-size:0.78rem; color:var(--text-dim); line-height:1.5; }}
  .info-panel .hl {{ color:var(--text); font-weight:600; }}
  @media(max-width:750px) {{
    .key {{ width:46px; height:38px; font-size:.6rem; }}
    .key .label {{ font-size:.65rem; }}
    .key .sub {{ font-size:.48rem; }}
    .key.thumb {{ width:54px; height:34px; }}
    .keyboard {{ gap:12px; }}
  }}
</style>
</head>
<body>
<h1>⌨️ Keymap Visualizer</h1>
<p class="subtitle">Generated from QMK keymap.c · {len(data['layers'])} layers · {data['rows']}×{data['cols']}+{data['thumbs']}</p>
<div class="search-box"><input type="text" id="search" placeholder="🔍 Search key..." autocomplete="off"></div>
<div class="layer-tabs" id="tabs"></div>
<div class="legend">
  <div class="legend-item"><div class="legend-swatch" style="background:var(--surface);border-color:var(--border)"></div>Alpha</div>
  <div class="legend-item"><div class="legend-swatch" style="background:rgba(210,153,34,.2);border-color:rgba(210,153,34,.4)"></div>Mod / HRM</div>
  <div class="legend-item"><div class="legend-swatch" style="background:rgba(188,140,255,.15);border-color:rgba(188,140,255,.4)"></div>Function</div>
  <div class="legend-item"><div class="legend-swatch" style="background:rgba(57,211,83,.15);border-color:rgba(57,211,83,.4)"></div>Navigation</div>
  <div class="legend-item"><div class="legend-swatch" style="background:rgba(247,120,186,.15);border-color:rgba(247,120,186,.4)"></div>Symbol</div>
  <div class="legend-item"><div class="legend-swatch" style="background:rgba(227,179,65,.15);border-color:rgba(227,179,65,.4)"></div>Number</div>
  <div class="legend-item"><div class="legend-swatch" style="background:rgba(88,166,255,.12);border-color:rgba(88,166,255,.4)"></div>Media</div>
  <div class="legend-item"><div class="legend-swatch" style="background:rgba(248,81,73,.15);border-color:rgba(248,81,73,.4)"></div>Mouse</div>
</div>
<div class="keyboard" id="kb"></div>
<div class="info-panel" id="info"></div>

<script>
const LAYERS = {layers_json};
let cur = 0, term = '';

function tabs() {{
  const el = document.getElementById('tabs');
  el.innerHTML = '';
  LAYERS.forEach((l, i) => {{
    const b = document.createElement('button');
    b.className = 'layer-tab' + (i === cur ? ' active' : '');
    b.innerHTML = l.name.replace(/_/g,' ').toUpperCase() + '<span class="idx">[' + l.index + ']</span>';
    b.onclick = () => {{ cur = i; render(); }};
    el.appendChild(b);
  }});
}}

function keyHTML(k, isThumb) {{
  const cls = ['key', k.type];
  if (isThumb) cls.push('thumb');
  if (k.layer) cls.push('layer-trigger');
  if (term) {{
    const match = k.label.toLowerCase().includes(term) || (k.sub && k.sub.toLowerCase().includes(term));
    if (match) cls.push('search-match');
    else if (k.type !== 'dead') cls.push('search-dim');
  }}
  const sub = k.sub ? '<span class="sub">' + k.sub + '</span>' : '';
  const title = [k.label, k.sub, k.raw].filter(Boolean).join(' · ');
  return '<div class="' + cls.join(' ') + '" title="' + title.replace(/"/g,'&quot;') + '"'
    + (k.layer ? ' data-layer="' + k.layer + '"' : '')
    + '><span class="label">' + k.label + '</span>' + sub + '</div>';
}}

function halfHTML(h, sideLabel) {{
  let html = '<div class="half"><div class="half-label">' + sideLabel + '</div>';
  h.rows.forEach(row => {{
    html += '<div class="row">';
    row.forEach(k => html += keyHTML(k, false));
    html += '</div>';
  }});
  if (h.thumbs && h.thumbs.length) {{
    html += '<div class="thumb-row">';
    h.thumbs.forEach(k => html += keyHTML(k, true));
    html += '</div>';
  }}
  return html + '</div>';
}}

function render() {{
  tabs();
  const l = LAYERS[cur];
  const kb = document.getElementById('kb');
  kb.innerHTML = halfHTML(l.left, '← Left') + halfHTML(l.right, 'Right →');
  // Click layer triggers
  kb.querySelectorAll('.key.layer-trigger').forEach(el => {{
    el.onclick = () => {{
      const target = el.dataset.layer;
      if (!target) return;
      const idx = LAYERS.findIndex(l => l.name === target);
      if (idx >= 0) {{ cur = idx; render(); }}
    }};
  }});
  // Info
  document.getElementById('info').innerHTML =
    '<h3>' + l.name.replace(/_/g,' ').toUpperCase() + ' Layer [' + l.index + ']</h3>'
    + '<p>Layer index: <span class="hl">' + l.index + '</span></p>';
}}

document.getElementById('search').addEventListener('input', e => {{
  term = e.target.value.toLowerCase().trim();
  render();
}});

render();
</script>
</body>
</html>'''


# ─── CLI ─────────────────────────────────────────────────────────────────

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
    html = generate_html(data, title)

    # Output
    if args.output:
        out_path = Path(args.output)
    else:
        out_path = keymap_path.parent / 'keymap_viz.html'

    out_path.write_text(html, encoding='utf-8')
    print(f"✓ Generated: {out_path}", file=sys.stderr)
    print(str(out_path))


if __name__ == '__main__':
    main()
