"""This module defines the 'RichText' class and the 'rt' instance."""

from typing import Literal


class RichText:

    _codes = {
        'reset': '0',
        'bold': '1',
        'faint': '2',
        'italic': '3',
        'underline': '4',
        'blink': '5',
        'reverse': '7',
        'strikethrough': '9',
        'black': '30',
        'red': '31',
        'green': '32',
        'yellow': '33',
        'blue': '34',
        'magenta': '35',
        'cyan': '36',
        'white': '37',
        'gray': '90',
        'grey': '90',
        'brightred': '91',
        'brightgreen': '92',
        'brightyellow': '93',
        'brightblue': '94',
        'brightmagenta': '95',
        'brightcyan': '96',
        'brightwhite': '97',
    }
    StyleColor = Literal['red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white', 'gray', 'grey',
                        'black', 'brightred', 'brightgreen', 'brightyellow', 'brightblue', 'brightmagenta',
                        'brightcyan', 'brightwhite']

    def __init__(self, sequence=''):
        self.sequence = sequence

    def __str__(self):
        return self.sequence

    def __add__(self, other):
        if isinstance(other, str):
            return self.sequence + other
        elif isinstance(other, RichText):
            return RichText(self.sequence + other.sequence)
        return NotImplemented

    def __getattr__(self, name):
        if name in self._codes:
            return f'\x1b[{self._codes[name]}m'
        raise AttributeError(f'No such style: {name}')

    def __repr__(self):
        return f'RichText(styles={list(type(self)._codes.keys())})'

    def __getitem__(self, key):
        code = self._codes.get(key)
        if code is None:
            raise KeyError(f'No such style: {key}')
        return f'\x1b[{code}m'

    def __setitem__(self, key, value):
        if not isinstance(value, str):
            raise TypeError(f'Expected str, got {type(value)}')
        self._codes[key] = value


    @property
    def bold(self):
        return RichText(self.sequence + "\x1b[1m")

    @property
    def faint(self):
        return RichText(self.sequence + "\x1b[2m")

    @property
    def italic(self):
        return RichText(self.sequence + "\x1b[3m")

    @property
    def underline(self):
        return RichText(self.sequence + "\x1b[4m")

    @property
    def blink(self):
        return RichText(self.sequence + "\x1b[5m")

    @property
    def reverse(self):
        return RichText(self.sequence + "\x1b[7m")

    @property
    def strikethrough(self):
        return RichText(self.sequence + "\x1b[9m")

    @property
    def black(self):
        return RichText(self.sequence + "\x1b[30m")

    @property
    def red(self):
        return RichText(self.sequence + "\x1b[31m")

    @property
    def green(self):
        return RichText(self.sequence + "\x1b[32m")

    @property
    def yellow(self):
        return RichText(self.sequence + "\x1b[33m")

    @property
    def blue(self):
        return RichText(self.sequence + "\x1b[34m")

    @property
    def magenta(self):
        return RichText(self.sequence + "\x1b[35m")

    @property
    def cyan(self):
        return RichText(self.sequence + "\x1b[36m")

    @property
    def white(self):
        return RichText(self.sequence + "\x1b[37m")

    @property
    def gray(self):
        return RichText(self.sequence + "\x1b[90m")

    @property
    def grey(self):
        return RichText(self.sequence + "\x1b[90m")

    @property
    def brightred(self):
        return RichText(self.sequence + "\x1b[91m")

    @property
    def brightgreen(self):
        return RichText(self.sequence + "\x1b[38;5;118m")

    @property
    def brightyellow(self):
        return RichText(self.sequence + "\x1b[38;5;226m")

    @property
    def brightblue(self):
        return RichText(self.sequence + "\x1b[94m")

    @property
    def brightmagenta(self):
        return RichText(self.sequence + "\x1b[95m")

    @property
    def brightcyan(self):
        return RichText(self.sequence + "\x1b[96m")

    @property
    def brightwhite(self):
        return RichText(self.sequence + "\x1b[97m")

    @property
    def reset(self):
        return "\x1b[0m"

    def colorize(self, text, color: StyleColor) -> str:
        """Adds color to text.
        :param text: The text to colorize.
        :param color: The color of the text.
        :return: The colorized text.
        """
        if color in self._codes:
            color_code = self._codes[color]
            return f'\x1b[{color_code}m{text}{self.reset}'
        else:
            raise ValueError(
                f"Invalid color code: {color}. Valid color codes are {self.StyleColor}"
            )

    def italicize(self, text) -> str:
        """Adds italic text to text.
        :param text: The text to italic.
        :return: The italic text.
        """
        return f'{self.italic}{text}{self.reset}'

    def boldize(self, text) -> str:
        """Adds bold text to text.
        :param text: The text to bold.
        :return: The bold text.
        """
        return f'{self.bold}{text}{self.reset}'

    def underlinedize(self, text) -> str:
        """Underlines text.
        :param text: The text to underline.
        :return: The underlined text.
        """
        return f'{self.underline}{text}{self.reset}'

    def blinkdize(self, text) -> str:
        """Slow blinks text.
        :param text: The text to blink.
        :return: The blinking text.
        """
        return f'{self.blink}{text}{self.reset}'

    def reversedize(self, text) -> str:
        """Reverses text.
        :param text: The text to reverse.
        :return: The reversed text.
        """
        return f'{self.reverse}{text}{self.reset}'

    def custom_foreground(self, text, r:int, g:int, b:int, hex_color:str=None) -> str:
        """Adds custom foreground to text.
        :param text: The text to color.
        :param r: Red on the RGB scale.
        :param g: Green on the RGB scale.
        :param b: Blue on the RGB scale.
        :param hex_color: The hex color for custom foreground.
        :return: The colorized text.
        """
        if hex_color and any(value is not None for value in (r, g, b)):
            raise ValueError('Provide either hex_color or RGB values (r, g, b), not both.')
        if hex_color:
            r, g, b = self._hex_converter(hex_color)
        self._rgb_validate(r, g, b)
        return f'\x1b[38;2;{r};{g};{b}m{text}{self.reset}'

    def custom_background(self, text, r:int, g:int, b:int, hex_color:str=None) -> str:
        """Adds custom background to text.
        :param text: The text to a background color.
        :param r: Red on the RGB scale.
        :param g: Green on the RGB scale.
        :param b: Blue on the RGB scale.
        :param hex_color: The hex color of the background.
        :return: The text with custom background color.
        """
        if hex_color and any(value is not None for value in (r, g, b)):
            raise ValueError('Provide either hex_color or RGB values (r, g, b), not both.')
        if hex_color:
            r, g, b = self._hex_converter(hex_color)
        self._rgb_validate(r, g, b)
        return f'\x1b[48;2;{r};{g};{b}m{text}{self.reset}'

    def custom_underline(self, text, r:int, g:int, b:int, hex_color:str=None) -> str:
        """Underlines text with custom color line.
        :param text: The text to underline.
        :param r: Red on the RGB scale.
        :param g: Green on the RGB scale.
        :param b: Blue on the RGB scale.
        :return: The text underlined with a custom color.
        :param hex_color: The hex color of the text.
        Please note: This is not supported in all editors.
        """
        if hex_color and any(value is not None for value in (r, g, b)):
            raise ValueError('Provide either hex_color or RGB values (r, g, b), not both.')
        if hex_color:
            r, g, b = self._hex_converter(hex_color)
        self._rgb_validate(r, g, b)
        return f'\x1b[58;2;{r};{g};{b}m{text}{self.reset}'

    def style(self, text, color:StyleColor=None, bold:bool=False, italic:bool=False, underline:bool=False, blink:bool=False, reverse:bool=False, strikethrough:bool=None, r:int=None, g:int=None, b:int=None, hex_color:str=None) -> str:
        """Styles text
        :param text: The text to style
        :param color: The color of the text.
        :param bold: Bold the text.
        :param italic: Italic the text.
        :param underline: Underline the text.
        :param blink: Blink the text.
        :param reverse: Reverse the text.
        :param strikethrough: Strikethrough the text.
        :param r: Red on the RGB scale.
        :param g: Green on the RGB scale.
        :param b: Blue on the RGB scale.
        :param hex_color: The hex color of the text.
        :return: The styled text.
        """
        codes = []

        for flag, enabled in [('bold', bold), ('italic', italic), ('underline', underline), ('blink', blink), ('reverse', reverse), ('strikethrough', strikethrough)]:
            if enabled:
                codes.append(self._codes[flag])

        if hex_color:
            r, g, b = self._hex_converter(hex_color)

        if color and color in self._codes:
            codes.append(self._codes[color])
        elif color and color not in self._codes:
            raise ValueError('Invalid color code.')
        elif r is not None and g is not None and b is not None:
            self._rgb_validate(r, g, b)
            codes.append(f'38;2;{r};{g};{b}')

        # Return text if no style selected
        if not codes:
            return text

        return f'\x1b[{";".join(codes)}m{text}{self.reset}'

    def ok(self, message) -> str:
        """Returns text with green color.
        :param message: The text to color.
        :return: The text with green color.
        """
        return f'{rt.green}{message}{self.reset}'

    def warn(self, message) -> str:
        """Returns text with bright yellow color.
        :param message: The text to color.
        :return: The text with bright yellow color.
        """
        return f'{rt.brightyellow}{message}{self.reset}'

    def error(self, message) -> str:
        """Returns text with red color.
        :param message: The text to color.
        :return: The text with red color.
        """
        return f'{rt.red}{message}{self.reset}'

    @staticmethod
    def _rgb_validate(r, g, b):
        """Validates that RGB values are both integers and between 0 and 255."""
        try:
            r_value = int(r)
            g_value = int(g)
            b_value = int(b)
        except ValueError:
            raise ValueError('RGB values must be integers or strings convertible to integers.')

        for value, name in zip((r_value, g_value, b_value), ('r', 'g', 'b')):
            if value is not None and not (0 <= value < 256):
                raise ValueError(f'{name} must be between 0 and 255')

    @staticmethod
    def _hex_converter(hex_color) -> tuple:
        """Converts hex color to RGB values."""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) != 6:
            raise ValueError('Hex color must be 6 characters long (e.g., "#ffcc00").')
        try:
            r, g, b = [int(hex_color[i:i+2], 16) for i in (0, 2, 4)]
        except ValueError:
            raise ValueError('Hex color must contain valid hexadecimal digits.')
        return r, g, b


rt = RichText()
__all__ = ['rt', 'RichText']