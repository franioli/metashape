import Metashape
import sys
import os
import math
import tkinter
import tempfile
from tkinter import filedialog
from zipfile import ZipFile
from pathlib import Path

if Metashape.app.activated:
    print("Metashape is activated: ", Metashape.app.activated)
else:
    print(
        "No licence found. Please check that you linked your license (floating or standalone) wih the Metashape python module."
    )
    exit()


def importPrj(fname, chunkName):
    doc = Metashape.app.document
    if chunkName is None:
        doc.clear()

    tempdir = tempfile.mkdtemp()
    with ZipFile(fname, "r") as zip:
        zip.extractall(tempdir)
        print("Extracted zip files to dir " + tempdir)

    if not os.path.isfile(os.path.join(tempdir, "file_list.txt")):
        print("ERROR!!!")
        exit()

    file_list = ReadFileList(os.path.join(tempdir, "file_list.txt"))

    chunk = doc.addChunk()
    if chunkName is not None:
        chunk.label = chunkName

    prjType = file_list[0]
    image_point_file = os.path.join(tempdir, file_list[1])
    bundler_file_list = os.path.join(tempdir, file_list[2])
    img_table = os.path.join(tempdir, file_list[3])
    markers_file = os.path.join(tempdir, file_list[5])
    cameras_file = os.path.join(tempdir, file_list[7])

    sensors = dict()
    for line in range(9, len(file_list) - 1):
        sensor_file = os.path.join(tempdir, file_list[line])
        id = line - 9
        s = AddSensor(chunk, sensor_file)
        sensors[id] = s

    AddImages(chunk, bundler_file_list, img_table, sensors, prjType)

    if prjType == "MultiCamera":
        chunk.importCameras(
            path=image_point_file, format=Metashape.CamerasFormat.CamerasFormatBundler
        )
    else:
        chunk.importCameras(
            path=image_point_file,
            format=Metashape.CamerasFormat.CamerasFormatBundler,
            image_list=bundler_file_list,
            load_image_list=True,
        )

    chunk.triangulatePoints(10000)

    ##chunk.importMarkers(markers_file)
    ImportMarkers(markers_file, chunk)
    chunk.importReference(
        cameras_file,
        columns="nxyzabco",
        delimiter=" ",
        group_delimiters=False,
        skip_rows=0,
        ignore_labels=False,
        create_markers=False,
    )

    # EnableCP(sys.argv[4], chunk)
    # EnableMarkers(sys.argv[5])

    # Optimize(sys.argv[5], chunk)

    # if sys.argv[6].endswith("psx"):
    #    doc.save(sys.argv[6])
    # else:
    #    chunk.exportCameras(sys.argv[6], format=Metashape.CamerasFormat.CamerasFormatBundler)
    #    outcalib = sys.argv[6].replace(".out", ".xml")
    #    chunk.cameras[0].sensor.calibration.save(outcalib, format=Metashape.CalibrationFormat.CalibrationFormatXML)
    #    outgcp = sys.argv[6].replace(".out", ".gcp")
    #    chunk.exportReference(outgcp, format=Metashape.ReferenceFormat.ReferenceFormatCSV,\
    #       items=Metashape.ReferenceItems.ReferenceItemsMarkers, columns='nxyzuvw',delimiter=' ')
    #    outcp = sys.argv[6].replace(".out", ".cp")
    #    chunk.exportReference(outcp, format=Metashape.ReferenceFormat.ReferenceFormatCSV, \
    #        items=Metashape.ReferenceItems.ReferenceItemsCameras, columns='noxyzuvw',delimiter=' ')


def AddImages(chunk, fname, img_table, sensors, prjType):
    lineList = [line.rstrip("\n") for line in open(fname, encoding="utf-8")]
    imgTable = [line.rstrip("\n") for line in open(img_table, encoding="utf-8")]

    if prjType == "MultiCamera":
        for sensor in chunk.sensors:
            chunk.remove(sensor)

        ptr = 0
        camptr = -1
        lastFile = ""
        for i in range(1, len(lineList)):
            camptr = camptr + 1
            f = lineList[i]
            if f == lastFile:
                ptr = ptr + 1
            else:
                chunk.addPhotos([f], layout=Metashape.MultiplaneLayout)
                ptr = 0
                print("Cameras tot: " + str(len(chunk.cameras)))
            lastFile = f
            # chunk.cameras[camptr].sensor = sensors[ptr]
        # for i in range(0, len(chunk.sensors)):
        #    sensor = chunk.sensors[i]
        #    sensor.layer_index = sensor.key - 9
        #    CopySensor(sensor, sensors[i])
        # return True
    else:
        for i in range(0, len(lineList)):
            f = lineList[i]
            items = imgTable[i].split("\t")
            cam = chunk.addCamera(sensors[int(items[2])])
            # if (len(sensors) == 1):
            #    cam = chunk.addCamera(sensors[0])
            # else:
            #    cam = chunk.addCamera(sensors[i])
            cam.label = Path(f).stem
            cam.photo = Metashape.Photo()
            cam.photo.open(f)
        # return False

    for line in imgTable:
        items = line.split("\t")
        cam = chunk.cameras[int(items[1])]
        if not (cam.label == items[0]):
            raise Exception()

        CopySensor(cam.sensor, sensors[int(items[2])])


def CopySensor(s1, s2):
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


def AddSensor(chunk, fname):
    lineList = [line.rstrip("\n") for line in open(fname)]
    sensor = chunk.addSensor()
    sensor.type = Metashape.Sensor.Type.Frame
    sensor.fixed = True
    s = sensor.calibration
    sensor.width = int(lineList[2])
    sensor.height = int(lineList[3])
    s.width = int(lineList[2])
    s.height = int(lineList[3])
    s.f = float(lineList[4])
    s.cx = float(lineList[5])
    s.cy = float(lineList[6])
    s.k1 = float(lineList[7])
    s.k2 = float(lineList[8])
    s.k3 = float(lineList[9])
    s.k4 = float(lineList[10])
    s.p1 = float(lineList[11])
    s.p2 = float(lineList[12])
    s.b1 = float(lineList[13])
    s.b2 = float(lineList[14])
    sensor.user_calib = s

    if lineList[15].startswith("Master:"):
        sensor.fixed_location = False
        sensor.fixed_rotation = False
        sensor.reference.location = Metashape.Vector(
            [float(lineList[16]), float(lineList[17]), float(lineList[18])]
        )
        sensor.reference.location_accuracy = Metashape.Vector(
            [0.0000001, 0.0000001, 0.0000001]
        )
        sensor.reference.location_enabled = True
        sensor.reference.rotation = Metashape.Vector(
            [float(lineList[19]), float(lineList[20]), float(lineList[21])]
        )
        sensor.reference.rotation_accuracy = Metashape.Vector(
            [0.0000001, 0.0000001, 0.0000001]
        )
        sensor.reference.rotation_enabled = True
        sensor.reference.enabled = True
        sensor.location = sensor.reference.location
        sensor.rotation = Metashape.Utils.opk2mat(sensor.reference.rotation)
    return sensor


def EnableCP(fname, chunk):
    for cam in chunk.cameras:
        cam.Reference.enabled = False
    with open(fname) as fp:
        for line in fp:
            chunk.cameras[int(line)].Reference.enabled = True


def EnableMarkers(fname, chunk):
    for mark in chunk.markers:
        mark.Reference.enabled = False
    with open(fname) as fp:
        for line in fp:
            chunk.markers[int(line)].Reference.enabled = True


def ImportMarkers(fname, chunk):
    with open(fname) as fp:
        for line in fp:
            items = line.rsplit(";")
            marker = chunk.addMarker()
            marker.label = items[0]
            marker.enabled = True
            marker.reference.enabled = items[1] == "1"
            marker.reference.location = Metashape.Vector(
                (float(items[2]), float(items[3]), float(items[4]))
            )
            nimg = int(items[5])
            for i in range(0, nimg):
                marker.projections[
                    chunk.cameras[int(items[6 + i * 3])]
                ] = Metashape.Marker.Projection(
                    Metashape.Vector(
                        (float(items[7 + i * 3]), float(items[8 + i * 3]))
                    ),
                    True,
                )


def Optimize(fname, chunk):
    lineList = [line.rstrip("\n") for line in open(fname)]
    f = bool(lineList[0])
    cx = bool(lineList[1])
    cy = bool(lineList[2])
    b1 = bool(lineList[3])
    b2 = bool(lineList[4])
    k1 = bool(lineList[5])
    k2 = bool(lineList[6])
    k3 = bool(lineList[7])
    p1 = bool(lineList[8])
    p2 = bool(lineList[9])
    chunk.optimizeCameras(
        fit_f=f,
        fit_cx=cx,
        fit_cy=cy,
        fit_b1=b1,
        fit_b2=b2,
        fit_k1=k1,
        fit_k2=k2,
        fit_k3=k3,
        fit_k4=False,
        fit_p1=p1,
        fit_p2=p2,
        fit_p3=False,
        fit_p4=False,
        adaptive_fitting=False,
        tiepoint_covariance=False,
    )


def ReadFileList(fname):
    with open(fname) as file:
        lines = file.readlines()
        lines = [line.rstrip() for line in lines]
    return lines


# Checking compatibility
compatible_major_version = "1.8"
found_major_version = ".".join(Metashape.app.version.split(".")[:2])
if found_major_version != compatible_major_version:
    raise Exception(
        "Incompatible Metashape version: {} != {}".format(
            found_major_version, compatible_major_version
        )
    )

if len(sys.argv) == 2:
    importPrj(sys.argv[1], None, None)
elif len(sys.argv) == 3:
    importPrj(sys.argv[1], sys.argv[2])
else:
    print("Usage: ImportProjectCore.py <import_file.zip> [chunk_name]")

print("Script finished. Project imported!")
