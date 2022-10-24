import os
import numpy as np
import Metashape

from pathlib import Path
from typing import Union

from lib.utils import (
    create_new_project,
    cameras_from_bundler,
    get_marker,
    get_camera,
    add_markers,
    copy_camera_estimated_to_reference,
)

if __name__ == "__main__":

    im_ext = "jpg"
    # im_path = Path('/home/francesco/lib/metashape/data/images')
    # bundler_out_path = Path('/home/francesco/lib/metashape/data/belpy.out')
    im_path = Path("C:/Users/Francesco/metashape/data/images")
    bundler_out_path = Path("C:/Users/Francesco/metashape/data/belpy.out")

    X = (49.6488, 192.0875, 71.7466)
    cams = ["IMG_2814", "IMG_1289"]
    projections = {
        cams[0]: (4006.6104, 3543.7073),
        cams[1]: (1007.1367, 3858.9214),
    }
    label = "F2"
    accuracy = [0.001, 0.001, 0.001]

    p = im_path.glob("*." + im_ext)
    images = [str(x) for x in p if x.is_file()]

    chunk = Metashape.app.document.chunk
    # doc = create_new_project("C:/Users/Francesco/metashape/src/data/test.psx")
    # chunk = doc.chunk
    chunk.addPhotos(images)

    cameras_from_bundler(
        chunk=chunk,
        fname=bundler_out_path,
        image_list=str(bundler_out_path.parent / "list.txt"),
    )

    add_markers(chunk, X, projections, label, accuracy)

    # copy_camera_estimated_to_reference(chunk)

    print("Script ended successfully")
