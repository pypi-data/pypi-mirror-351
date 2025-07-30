from io import BytesIO
from typing import Literal, TypedDict
from PIL import Image

from .text import render_mc_text


class TextOptions(TypedDict, total=False):
    """
    Options used for rendering text onto an image.
    
    Keys:
        font_size (int): Size of the text.
        font_path (str): Path to the font file to be used.
        position (tuple[int, int]): (x, y) coordinates where text should be drawn.
        shadow_offset (tuple[int, int] | None): Optional offset for drawing a text shadow.
        align (Literal["left", "right", "center"]): Horizontal alignment of the text.
    """

    font_size: int
    font_path: str 
    position: tuple[int, int]
    shadow_offset: tuple[int, int] | None
    align: Literal["left", "right", "center"]

    @staticmethod
    def default() -> 'TextOptions':
        """
        Returns a default set of text rendering options.

        Returns:
            TextOptions: A dictionary with default font size, position, shadow, and alignment.
        """
        return {
            "font_size": 16,
            "position": (0, 0),
            "shadow_offset": None,
            "align": "left"
        }


class ImageRender:
    """
    A utility class for composing and exporting images with optional text overlays.
    """

    def __init__(self, base_image: Image.Image):
        """
        Initializes the renderer with a base image.

        Parameters:
            base_image (PIL.Image.Image): The background image to draw on.
        """
        self._image: Image.Image = base_image.convert("RGBA")
        self.text = TextRender(self._image)

    def overlay_image(self, overlay_image: Image.Image) -> None:
        """
        Overlays another image on top of the base image.

        Parameters:
            overlay_image (PIL.Image.Image): The image to composite on top.
        """
        self._image.alpha_composite(overlay_image.convert("RGBA"))

    def to_bytes(self) -> bytes:
        """
        Converts the image to bytes in PNG format.

        Returns:
            bytes: The binary PNG data.
        """
        image_bytes = BytesIO()
        self._image.save(image_bytes, format='PNG')
        image_bytes.seek(0)
        return image_bytes

    def save(self, filepath: str, **kwargs) -> None:
        """
        Saves the image to disk.

        Parameters:
            filepath (str): The destination file path.
            **kwargs: Additional keyword arguments for PIL.Image.save.
        """
        self._image.save(filepath, **kwargs)

    @property
    def size(self) -> tuple[int, int]:
        """
        Gets the dimensions of the image.

        Returns:
            tuple[int, int]: Width and height of the image.
        """
        return self._image.size


class TextRender:
    """
    A helper class for rendering Minecraft-style formatted text onto an image.
    """

    def __init__(self, image: Image.Image) -> None:
        """
        Initializes the text renderer with an image reference.

        Parameters:
            image (PIL.Image.Image): The image to render text on.
        """
        self._image = image

    def draw(
        self,
        text: str,
        text_options: TextOptions = None
    ) -> None:
        """
        Draws a single piece of formatted text onto the image.

        Parameters:
            text (str): The text string to render.
            text_options (TextOptions): A dictionary of rendering options. If not provided,
                                        default options are used.
        """
        if text_options is None:
            text_options = TextOptions.default()
        elif "position" not in text_options:
            text_options["position"] = (0, 0)

        render_mc_text(text, image=self._image, **text_options)

    def draw_many(
        self,
        text_info: list[tuple[str, TextOptions]],
        default_text_options: TextOptions
    ) -> None:
        """
        Draws multiple pieces of text using a shared set of default options.

        Parameters:
            text_info (list): A list of (text, text_options) tuples for each line of text.
            default_text_options (TextOptions): Default options to merge with each individual item.
        """
        for text, text_options in text_info:
            combined_options = {**default_text_options, **text_options}
            self.draw(text, combined_options)
