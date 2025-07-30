"""
RichText Package

Provides:
 - 'rt': a ready-to-use RichText instance
 - 'RichText': the base class for custom styling logic

Usage:
    from richtext import rt
    print(f'{rt.green}Success!{rt.reset}')
    print(f'{rt['green']}Success!{rt['reset]}')
"""

from .richtext import rt, RichText

colorize = rt.colorize
style = rt.style
ok = rt.ok
warn = rt.warn
error = rt.error
underlinedize = rt.underlinedize
blinkdize = rt.blinkdize
reversedize = rt.reversedize
italicize = rt.italicize
boldize = rt.boldize
custom_foreground = rt.custom_foreground
custom_background = rt.custom_background
custom_underline = rt.custom_underline


__all__ = ['rt', 'RichText', 'colorize', 'style', 'ok', 'warn', 'error', 'underlinedize', 'blinkdize', 'reversedize', 'italicize', 'boldize', 'custom_foreground', 'custom_background', 'custom_underline']