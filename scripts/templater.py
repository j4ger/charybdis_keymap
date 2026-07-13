"""Mini templater: substitute {{ name }} placeholders, leave single { } literal.

Uses a single regex pass; substituted values are NOT re-scanned, so braces
inside CSS/JS/JSON values stay literal. Unknown matched keys raise KeyError
at build time. A `{{` not followed by `\\w+ }}` is left literal (safer than
raising).
"""
import re

_PLACEHOLDER = re.compile(r'\{\{\s*(\w+)\s*\}\}')


def render_template(text, context):
    """Replace {{ name }} with context['name']. Single { } are literal.

    Substituted values are not re-scanned. Unknown keys raise KeyError.
    """
    def repl(m):
        key = m.group(1)
        if key not in context:
            raise KeyError(f"template variable {key!r} not in context")
        return str(context[key])
    return _PLACEHOLDER.sub(repl, text)
