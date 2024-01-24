import Metashape
import os
from pathlib import Path

from lib.utils import (
    check_license,
    create_new_project,
    save_project,
    read_sensors_data,
    match_images_sensors,
)

check_license()

PROJECT_NAME = "test.psx"
CHUNK_NAME = "test"

SENSOR_LIST = ["p1", "p2"]
IMG_LIST = ["IMG_2814.jpg", "IMG_1289.jpg"]

camera_table = {IMG_LIST[0]: SENSOR_LIST[0], IMG_LIST[1]: SENSOR_LIST[1]}

doc = create_new_project(PROJECT_NAME, CHUNK_NAME)
chunk = doc.chunk

chunk.addPhotos(IMG_LIST)  # , layout=Metashape.MultiplaneLayout
print(f"Cameras tot: {len(chunk.cameras)}")

sensors = read_sensors_data([s + ".txt" for s in SENSOR_LIST])
match_images_sensors(chunk, sensors, camera_table)

save_project(document=doc, project_name=PROJECT_NAME)
