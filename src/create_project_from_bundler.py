import numpy as np
import Metashape

from pathlib import Path

from lib.utils import (
    create_new_project,
    cameras_from_bundler,
    add_markers,
    copy_camera_estimated_to_reference,
    sensors_from_files,
    match_images_sensors,
)
from lib.io import read_gcp_file

if __name__ == "__main__":

    # im_path = Path('/home/francesco/lib/metashape/data/images')
    # bundler_out_path = Path('/home/francesco/lib/metashape/data/belpy.out')
    im_path = Path("C:/Users/Francesco/metashape/data/images")
    bundler_out_path = Path("C:/Users/Francesco/metashape/data/belpy_epoch_0.out")
    gcp_filename = "C:/Users/Francesco/metashape/data/gcps.txt"
    im_ext = "jpg"
    gcp_accuracy = [0.01, 0.01, 0.01]

    p = im_path.glob("*." + im_ext)
    images = [str(x) for x in p if x.is_file()]

    # SENSOR_LIST = ["p1", "p2"]
    # IMG_LIST = ["IMG_2814.jpg", "IMG_1289.jpg"]
    # camera_table = {IMG_LIST[0]: SENSOR_LIST[0], IMG_LIST[1]: SENSOR_LIST[1]}

    # doc = create_new_project("C:/Users/Francesco/metashape/data/test.psx")
    # chunk = doc.chunk
    chunk = Metashape.app.document.chunk
    chunk.addPhotos(images)

    # Cameras
    cameras_from_bundler(
        chunk=chunk,
        fname=bundler_out_path,
        image_list=str(bundler_out_path.parent / "list.txt"),
    )
    copy_camera_estimated_to_reference(chunk, accuracy=0.15)

    # GCPs
    gcps = read_gcp_file(gcp_filename)
    for point in gcps:
        add_markers(
            chunk, point["world"], point["projections"], point["label"], gcp_accuracy
        )

    # Sensor calibraion
    # sensors = sensors_from_files(
    #     [f"C:/Users/Francesco/metashape/data/{s}.txt" for s in SENSOR_LIST]
    #     )
    # match_images_sensors(chunk, sensors, camera_table)

    print("Script ended successfully")
