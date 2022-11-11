import Metashape
import numpy as np

from typing import List
from typing import Union
from pathlib import Path

from lib.io import read_opencv_calibration

""" License """


def check_license() -> None:
    if Metashape.app.activated:
        print("Metashape is activated: ", Metashape.app.activated)
    else:
        raise Exception(
            "No licence found. Please check that you linked your license (floating or standalone) wih the Metashape python module."
        )


""" Project """


def save_project(
    document: Metashape.app.document,
    project_name: str,
) -> None:
    try:
        document.save(project_name)
    except RuntimeError:
        Metashape.app.messageBox("Can't save project")


def clear_all_sensors(chunk) -> None:
    for sensor in chunk.sensors:
        chunk.remove(sensor)


def create_new_chunk(doc: Metashape.app.document, chunk_name: str = None) -> None:
    chunk = doc.addChunk()
    if chunk_name is not None:
        chunk.label = chunk_name


def create_new_project(
    project_name: str,
    chunk_name: str = None,
    read_only: bool = False,
) -> Metashape.app.document:

    doc = Metashape.Document()
    doc.read_only = read_only
    create_new_chunk(doc, chunk_name)
    save_project(doc, project_name)

    return doc


def cameras_from_bundler(
    chunk: Metashape.Chunk,
    fname: str,
    image_list: str,
) -> None:
    if image_list:
        chunk.importCameras(
            str(fname),
            format=Metashape.CamerasFormat.CamerasFormatBundler,
            load_image_list=True,
            image_list=str(image_list),
        )
        print("Cameras loaded successfully from Bundler .out, using image list file.")
    else:
        chunk.importCameras(
            str(fname),
            format=Metashape.CamerasFormat.CamerasFormatBundler,
        )
        print("Cameras loaded successfully from Bundler .out.")


""" Get objects"""


def get_marker(chunk, label):
    for marker in chunk.markers:
        if marker.label == label:
            return marker
    return None


def get_camera(chunk, label):
    for camera in chunk.cameras:
        if camera.label.lower() == label.lower():
            return camera
    return None


"""Markers"""


def add_markers(
    chunk: Metashape.Chunk,
    X: np.ndarray,
    projections: dict,
    label: str = None,
    accuracy: Union[float, np.ndarray] = None,
) -> None:

    # Create Markers given its 3D object coordinates
    X = Metashape.Vector(X)
    X_ = chunk.transform.matrix.inv().mulp(X)
    marker = chunk.addMarker(X_)

    # Add projections on images given image coordinates in a  dictionary, as  {im_name: (x,y)}
    for k, v in projections.items():
        cam = get_camera(chunk, k.split(".")[0])
        marker.projections[cam] = Metashape.Marker.Projection(Metashape.Vector(v))

    # If provided, add label and a-priori accuracy
    if label:
        marker.label = label
    if accuracy:
        marker.reference.accuracy = accuracy
    marker.enabled = True
    marker.reference.enabled = True


"""Sensors"""


def read_sensor_from_file(
    fname: str,
    fix_parameters: bool = True,
) -> Metashape.Sensor:
    """Read sensor information from file, containing image size, full K matrix and distortion vector, according to OpenCV standards, and organized in one line, as follow:
    fx 0. cx 0. fy cy 0. 0. 1. k1, k2, p1, p2, [k3, [k4, k5, k6
    Values must be float(include the . after integers) and divided by a white space.
    Parameters
    ----------
    fname (str): file path
    fix_parameters (bool): Fix all parameters
    -------
    Returns:  Metashape.Sensor object
    """
    cam_prm = read_opencv_calibration(fname)
    sensor = Metashape.Sensor
    sensor.type = Metashape.Sensor.Type.Frame
    sensor.width = int(cam_prm["width"])
    sensor.height = int(cam_prm["height"])
    sensor.user_calib.f = cam_prm["f"]
    sensor.user_calib.cx = cam_prm["cx"]
    sensor.user_calib.cy = cam_prm["cy"]
    sensor.user_calib.k1 = cam_prm["k1"]
    sensor.user_calib.k2 = cam_prm["k2"]
    sensor.user_calib.k3 = cam_prm["k3"]
    sensor.user_calib.k4 = cam_prm["k4"]
    sensor.user_calib.p1 = cam_prm["p1"]
    sensor.user_calib.p2 = cam_prm["p2"]
    sensor.user_calib.b1 = cam_prm["b1"]
    sensor.user_calib.b2 = cam_prm["b2"]
    sensor.fixed = fix_parameters

    return sensor


def sensors_from_files(
    sensor_list: List[str],
    chunk: Metashape.Chunk = None,
) -> dict:
    """Create sensor dictionary from filenames.
    Parameters
    ----------
    sensor_list (list):
    chunk (Metashape.Chunk, default = None): If not None, chunk where to add the sensors.
    -------
    Returns: sensors (dict)
    """
    sensors = dict()
    for id, file in enumerate(sensor_list):
        s = read_sensor_from_file(file)
        s.label = Path(file).stem
        s.type = Metashape.Sensor.Frame
        s.fixed = True
        sensors[id] = s
        if chunk:
            chunk.addSensor(s)
    return sensors


def AddSensor(
    chunk: Metashape.Chunk,
    fname: str,
    fix_parameters: bool = True,
) -> None:
    """Deprecated function. Use sensors_from_files instead."""
    cam_prm = read_opencv_calibration(fname)
    sensor = chunk.addSensor()
    sensor.type = Metashape.Sensor.Type.Frame
    sensor.width = int(cam_prm["width"])
    sensor.height = int(cam_prm["height"])
    sensor.fixed = fix_parameters

    usr_cal = sensor.calibration
    usr_cal.width = cam_prm["width"]
    usr_cal.height = cam_prm["height"]
    usr_cal.f = cam_prm["f"]
    usr_cal.cx = cam_prm["cx"]
    usr_cal.cy = cam_prm["cy"]
    usr_cal.k1 = cam_prm["k1"]
    usr_cal.k2 = cam_prm["k2"]
    usr_cal.k3 = cam_prm["k3"]
    usr_cal.k4 = cam_prm["k4"]
    usr_cal.p1 = cam_prm["p1"]
    usr_cal.p2 = cam_prm["p2"]
    usr_cal.b1 = cam_prm["b1"]
    usr_cal.b2 = cam_prm["b2"]
    sensor.user_calib = usr_cal

    # if (lineList[15].startswith("Master:")):
    #     sensor.fixed_location = False
    #     sensor.fixed_rotation = False
    #     sensor.reference.location = Metashape.Vector(
    #         [float(lineList[16]), float(lineList[17]), float(lineList[18])])
    #     sensor.reference.location_accuracy = Metashape.Vector(
    #         [0.0000001, 0.0000001, 0.0000001])
    #     sensor.reference.location_enabled = True
    #     sensor.reference.rotation = Metashape.Vector(
    #         [float(lineList[19]), float(lineList[20]), float(lineList[21])])
    #     sensor.reference.rotation_accuracy = Metashape.Vector(
    #         [0.0000001, 0.0000001, 0.0000001])
    #     sensor.reference.rotation_enabled = True
    #     sensor.reference.enabled = True
    #     sensor.location = sensor.reference.location
    #     sensor.rotation = Metashape.Utils.opk2mat(sensor.reference.rotation)
    return sensor


def match_images_sensors(
    chunk: Metashape.Chunk,
    sensors: dict,
    camera_table: dict,
) -> None:
    for cam in chunk.cameras:
        label = camera_table[cam.label + ".jpg"]
        id = get_sensor_id_by_label(sensors, label)
        if id is not None:
            copy_sensor(cam.sensor, sensors[id])
            print(f"Sensor associated. Camera: {cam.label} -> sensor: {label} {id}")
        else:
            raise Exception("Sensor not found.")


def copy_sensor(
    s1: Metashape.Sensor,
    s2: Metashape.Sensor,
):
    s1.type = s2.type
    s1.fixed = s2.fixed
    c1 = s1.calibration
    c2 = s2.calibration
    s1.width = s2.width
    s1.height = s2.height
    c1.width = c2.width
    c1.height = c2.height
    c1.f = c2.f
    c1.cx = c2.cx
    c1.cy = c2.cy
    c1.k1 = c2.k1
    c1.k2 = c2.k2
    c1.k3 = c2.k3
    c1.k4 = c2.k4
    c1.p1 = c2.p1
    c1.p2 = c2.p2
    c1.b1 = c2.b1
    c1.b2 = c2.b2
    # s1.calibration = c1
    s1.user_calib = c1

    s1.fixed_location = s2.fixed_location
    s1.fixed_rotation = s2.fixed_rotation
    s1.reference.location = s2.reference.location
    s1.reference.location_accuracy = s2.reference.location_accuracy
    s1.reference.location_enabled = s2.reference.location_enabled
    s1.reference.rotation = s2.reference.rotation
    s1.reference.rotation_accuracy = s2.reference.rotation_accuracy
    s1.reference.rotation_enabled = s2.reference.rotation_enabled
    s1.reference.enabled = s2.reference.enabled
    s1.location = s2.location
    s1.rotation = s2.rotation


def copy_camera_estimated_to_reference(
    chunk: Metashape.Chunk,
    copy_rotations: bool = False,
    accuracy: List[float] = None,
) -> None:

    # Get Chunk transformation matrix
    T = chunk.transform.matrix

    if len(accuracy) == 1:
        accuracy = Metashape.Vector((accuracy, accuracy, accuracy))
    elif len(accuracy) != 3:
        print(
            "Wrong input type for accuracy parameter. Provide a list of floats (it can be a list of a single element or of three elements)."
        )
        return

    for camera in chunk.cameras:
        cam_T = T * camera.transform
        camera.reference.location = cam_T.translation()
        camera.reference.enabled = True
        if copy_rotations:
            chunk.euler_angles = Metashape.EulerAnglesOPK
            camera.reference.rotation = Metashape.utils.mat2opk(cam_T.rotation())
            camera.reference.rotation_enabled = True
        if accuracy:
            camera.reference.accuracy = accuracy


def get_sensor_id_by_label(
    sensors: List[Metashape.Sensor],
    sensor_label: str,
) -> int:
    for s_id in sensors:
        sensor = sensors[s_id]
        if sensor.label == sensor_label:
            return s_id


""" MISCELLANEOUS """


def make_homogeneous(
    v: Metashape.Vector,
) -> Metashape.Vector:

    vh = Metashape.Vector([1.0 for x in range(v.size + 1)])
    for i, x in enumerate(v):
        vh[i] = x

    return vh


def make_inomogenous(
    vh: Metashape.Vector,
) -> Metashape.Vector:
    v = vh / vh[vh.size - 1]
    return v[: v.size - 1]
