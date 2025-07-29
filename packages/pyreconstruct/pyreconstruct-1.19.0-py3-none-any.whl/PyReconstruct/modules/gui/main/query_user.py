"""Helper functions to query users various requests."""


import os
from typing import List

from PyReconstruct.modules.gui.utils import notify
from PyReconstruct.modules.gui.dialog import FileDialog


def query_for_images(mainwindow, zarr: bool=False) -> List[str]:
    """Query users for images."""

    image_locations = []

    if zarr:
            
        valid_zarr = False
            
        while not valid_zarr:
            
            zarr_fp = FileDialog.get("dir", mainwindow, "Select Zarr")

            if not zarr_fp:
                break
                
            ## Get image names from zarr
            if "scale_1" in os.listdir(zarr_fp):
                    
                for f in os.listdir(os.path.join(zarr_fp, "scale_1")):
                    if not f.startswith("."):
                        image_locations.append(os.path.join(zarr_fp, "scale_1", f))

                valid_zarr = True
                            
            else:
                    
                notify("Please select a valid zarr.")
                    
    else:

        image_types = "*.jpg *.jpeg *.png *.tif *.tiff *.bmp"

        image_locations = FileDialog.get(
            "files", mainwindow, "Select Images", filter=image_types
        )
            
    return image_locations
