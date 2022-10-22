import os
import numpy as np
import Metashape

from pathlib import Path
from typing import Union

from lib.utils import get_marker, get_camera


def copy_camera_estimate_to_reference(
    chunk: Metashape.Chunk,
    accuracy: float = 0.000001,
) -> None:
    T = chunk.transform.matrix
    acc = Metashape.Vector((accuracy, accuracy, accuracy))
    for camera in chunk.cameras:
        cam_T = T * camera.transform
        camera.reference.location = cam_T.translation()
        camera.reference.rotation = cam_T.rotation()
        camera.reference.rotation_enabled = True
        camera.reference.accuracy = acc


def add_markers(
    chunk: Metashape.Chunk,
    X: np.ndarray,
    projections: dict,
    label: str = None,
    accuracy: Union[float, np.ndarray] = None
) -> None:

    # Create Markers given its 3D object coordinates
    X = Metashape.Vector(X)
    X_ = chunk.transform.matrix.inv().mulp(X)
    marker = chunk.addMarker(X_)

    # Add projections on images given image coordinates in a  dictionary, as  {im_name: (x,y)}
    for k, v in projections.items():
        cam = get_camera(chunk, k)
        marker.projections[cam] = Metashape.Marker.Projection(
            Metashape.Vector(v))

    # If provided, add label and a-priori accuracy
    if label:
        marker.label = label
    if accuracy:
        marker.reference.accuracy = accuracy
    marker.enabled = True


im_ext = 'jpg'
im_path = Path('/home/francesco/lib/metashape/data/images')
bundler_out_path = Path('/home/francesco/lib/metashape/belpy.out')

X = (49.6488, 192.0875, 71.7466)
cams = ['IMG_2814', 'IMG_1289']
projections = {
    cams[0]: (4006.6104, 3543.7073),
    cams[1]: (1007.1367, 3858.9214),
}
label = 'F2'
accuracy = [0.001, 0.001, 0.001]


p = im_path.glob('*.'+im_ext)
images = [str(x) for x in p if x.is_file()]

chunk = Metashape.app.document.chunk
chunk.addPhotos(images)

chunk.importCameras(
    str(bundler_out_path),
    format=Metashape.CamerasFormat.CamerasFormatBundler,
    load_image_list=True,
    image_list=str(bundler_out_path.parent/'list.txt'),
)

add_markers(chunk, X, projections, label, accuracy)


# copy_camera_estimate_to_reference(chunk)

print("Script ended successfully")
