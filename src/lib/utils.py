import Metashape

from typing import List
from pathlib import Path

from lib.io import read_opencv_calibration


def check_license() -> None:
    if Metashape.app.activated:
        print("Metashape is activated: ", Metashape.app.activated)
    else:
        raise Exception(
            "No licence found. Please check that you linked your license (floating or standalone) wih the Metashape python module."
        )


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


def create_new_chunk(
    doc: Metashape.app.document,
    chunk_name: str = None
) -> None:
    chunk = doc.addChunk()
    if (chunk_name is not None):
        chunk.label = chunk_name


def create_new_project(
    project_name: str,
    chunk_name: str = None
) -> Metashape.app.document:

    doc = Metashape.Document()
    create_new_chunk(doc, chunk_name)
    save_project(doc, project_name)

    return doc


'''Sensors'''


def AddSensor(chunk, fname):
    cam_prm = read_opencv_calibration(fname)
    sensor = chunk.addSensor()
    sensor.type = Metashape.Sensor.Type.Frame
    sensor.fixed = True
    s = sensor.calibration
    sensor.width = int()
    sensor.height = int()
    s.width = cam_prm['width']
    s.height = cam_prm['heigth']
    s.f = cam_prm['f']
    s.cx = cam_prm['cx']
    s.cy = cam_prm['cy']
    s.k1 = cam_prm['k1']
    s.k2 = cam_prm['k2']
    s.k3 = cam_prm['k3']
    s.k4 = cam_prm['k4']
    s.p1 = cam_prm['p1']
    s.p2 = cam_prm['p2']
    s.b1 = cam_prm['b1']
    s.b2 = cam_prm['b2']
    sensor.user_calib = s

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


def read_sensors_data(
    sensor_list: List[str],
) -> dict:

    sensors = dict()
    doc = Metashape.Document()
    chunk = doc.addChunk()

    for id, file in enumerate(sensor_list):
        s = AddSensor(chunk, file)
        s.label = Path(file).stem
        s.type = Metashape.Sensor.Frame
        s.fixed = True
        sensors[id] = s
    return sensors


def match_images_sensors(
    chunk: Metashape.Chunk,
    sensors: dict,
    camera_table: dict,
) -> None:
    for cam in chunk.cameras:
        label = camera_table[cam.label+'.jpg']
        id = retrieve_sensor_id_by_label(
            sensors, label
        )
        if id is not None:
            CopySensor(cam.sensor, sensors[id])
            print(
                f'Sensor associated. Camera: {cam.label} -> sensor: {label} {id}')
        else:
            raise Exception('Sensor not found.')


def CopySensor(
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
    #s1.calibration = c1
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


def retrieve_sensor_id_by_label(
    sensors: List[Metashape.Sensor],
    sensor_label: str,
) -> int:
    for s_id in sensors:
        sensor = sensors[s_id]
        if sensor.label == sensor_label:
            return s_id
