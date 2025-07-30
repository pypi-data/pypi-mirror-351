from typing import Literal
from PIL import Image, ImageFont, ImageDraw
from .tools import split_string
from .colors import ColorMappings

# Dummy image for measuring text
dummy_img = Image.new('RGBA', (0, 0))
dummy_draw = ImageDraw.Draw(dummy_img)


def load_font(font_file: str, font_size: int) -> ImageFont.FreeTypeFont:
    """
    Loads a TrueType font from a file.

    Parameters:
        font_file (str): Path to the .ttf font file.
        font_size (int): Desired font size.

    Returns:
        ImageFont.FreeTypeFont: Loaded font object.
    """
    return ImageFont.truetype(font_file, font_size)


def calc_shadow_color(rgb: tuple) -> tuple[int, int, int]:
    """
    Calculates a shadow color by reducing the brightness of the input color.

    Parameters:
        rgb (tuple): An (R, G, B) color tuple.

    Returns:
        tuple[int, int, int]: Darkened shadow color.
    """
    return tuple(int(c * 0.25) for c in rgb)


def get_text_len(text: str, font: ImageFont.ImageFont) -> float:
    """
    Measures the pixel width of the text using the given font.

    Parameters:
        text (str): Text to measure.
        font (ImageFont.ImageFont): Font used for measuring.

    Returns:
        float: Text width in pixels.
    """
    return dummy_draw.textlength(text, font=font)


def get_actual_text(text: str) -> str:
    """
    Extracts the visible characters from color-formatted text.

    Parameters:
        text (str): Text possibly containing color codes.

    Returns:
        str: The raw text without formatting codes.
    """
    split_chars = tuple(ColorMappings.color_codes)
    bits = split_string(text, split_chars)
    return ''.join([bit[0] for bit in bits])


def get_start_point(
    text: str = None,
    font: ImageFont.ImageFont = None,
    align: Literal['left', 'center', 'right'] = 'left',
    pos: int = 0,
    text_len: int = None
) -> int:
    """
    Calculates the X-coordinate where text drawing should start based on alignment.

    Parameters:
        text (str): Text to be rendered.
        font (ImageFont.ImageFont): Font used for measuring.
        align (str): Text alignment - 'left', 'center', or 'right'.
        pos (int): Reference X position.
        text_len (int): Pre-calculated text length (optional).

    Returns:
        int: Adjusted X position to start rendering.
    """
    assert (text, font, text_len).count(None) > 0

    if text_len is None:
        text_len = get_text_len(text, font)

    if align in ('default', 'left'):
        return pos
    elif align in ('center', 'middle'):
        return round(pos - text_len / 2)
    elif align == 'right':
        return round(pos - text_len)
    
    return 0


def render_mc_text(
    text: str,
    position: tuple[int, int],
    image: Image.Image,
    font: ImageFont.ImageFont = None,
    font_size: int = None,
    font_path: str = None,
    shadow_offset: tuple[int, int] = None,
    align: Literal['left', 'center', 'right'] = 'left'
) -> int:
    """
    Renders Minecraft-style colored text onto a given image.

    Supports in-line color formatting based on predefined color codes.

    Parameters:
        text (str): Text to render, possibly including color codes.
        position (tuple[int, int]): (x, y) coordinates for text placement.
        image (PIL.Image.Image): Image to draw onto.
        font (ImageFont.ImageFont, optional): Preloaded font object.
        font_size (int, optional): Font size to load if `font` is not provided.
        font_path (str): Path to a TTF font file. Used if `font` is not provided.
        shadow_offset (tuple[int, int], optional): (x, y) offset for drop shadow.
        align (str): Text alignment - 'left', 'center', or 'right'.

    Returns:
        int: Final X-coordinate after rendering the text.

    Example:
        render_mc_text(
            text="Hello§aWorld",
            position=(100, 50),
            image=img,
            font_size=16,
            font_path="assets/fonts/minecraft.ttf",
            shadow_offset=(1, 1),
            align="center"
        )
    """
    assert (font, font_size).count(None) > 0

    if font is None:
        font = load_font(font_path, font_size)

    split_chars = tuple(ColorMappings.color_codes)
    bits = tuple(split_string(text, split_chars))
    actual_text = ''.join([bit[0] for bit in bits])

    draw = ImageDraw.Draw(image)

    x, y = position
    x = get_start_point(text=actual_text, font=font, align=align, pos=x)

    for text, color_code in bits:
        color = ColorMappings.color_codes.get(color_code, ColorMappings.white)

        if shadow_offset is not None:
            off_x, off_y = shadow_offset
            shadow_color = calc_shadow_color(color)
            draw.text((x + off_x, y + off_y), text, fill=shadow_color, font=font)

        draw.text((x, y), text, fill=color, font=font)
        x += int(draw.textlength(text, font=font))

    return x