from pathlib import Path
from PIL import Image


class BackgroundImageLoader:
    """
    Utility class for loading background images from a user-defined directory.
    
    Users must specify both the directory path and default filename.
    """

    def __init__(self, dir: str, default_filename: str) -> None:
        """
        Initializes the loader with a directory and a default image filename.

        Parameters:
            dir (str): Path to the directory where images are located.
            default_filename (str): Filename of the default background image.
        """
        self._dir = Path(dir)
        self._default_filename = default_filename
        self._default_img_path = self._dir / default_filename

    def __load_image(self, image_path: str) -> Image.Image:
        """
        Opens an image from the specified directory (internal use).

        Parameters:
            image_path (str): Filename or relative path under the provided directory.

        Returns:
            Image.Image: Opened image object.
        """
        return Image.open(self._dir / image_path)

    def load_image(self, image_path: str) -> Image.Image:
        """
        Loads an image and returns a copy to avoid modifying the original.

        Parameters:
            image_path (str): Filename or relative path under the provided directory.

        Returns:
            Image.Image: Copied image object.
        """
        return self.__load_image(image_path).copy()

    def load_default_background(self) -> Image.Image:
        """
        Loads the default background image.

        Returns:
            Image.Image: Default background image as a copy.
        """
        return self.load_image(self._default_filename)