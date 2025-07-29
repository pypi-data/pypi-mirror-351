"""Image class."""

from pathlib import Path
from typing import Tuple, Union

import cv2
import zarr


class Image:

    def __init__(self, filepath: Union[str, Path], mag:float=0.00254):
        """Create an Image class instance."""

        self.filepath: Path = Path(filepath)
        self.mag: float = mag
        self.width: int = self.shape[1]
        self.height: int = self.shape[0]

    @property
    def shape(self) -> Tuple[int, int]:
        """Return width and height of an image."""

        try:

            z = zarr.open(str(self.filepath))
            return z.shape

        except AttributeError:
            
            img = cv2.imread(str(self.filepath))
            return img.shape
            
        
