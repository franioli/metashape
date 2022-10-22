import Metashape
import sys
import os
import math
import tkinter
from tkinter import EXCEPTION, filedialog
from PySide2 import QtGui, QtCore, QtWidgets
 
def isMasterSensor(sensor):
    isMaster = sensor.master == sensor;
    return 1 if (isMaster) else 0;

def export(filename):
    doc = Metashape.app.document
    chunk1 = doc.chunk

    f = open(filename, "w", encoding='utf-8')
    try:
        point_cloud = chunk1.point_cloud
        points = point_cloud.points

        T = chunk1.transform.matrix
        crs = chunk1.crs


        f.write("################    GROUND POINT COORDINATE    ################\n")
        for pt in points:
            coord = Metashape.Vector((pt.coord.x, pt.coord.y, pt.coord.z))
            point  = crs.project(T.mulp(coord))
            f.write("{:d}\t{:.8f}\t{:.8f}\t{:.8f}\n".format(pt.track_id, point.x, point.y, point.z))

        npoints = len(points)
        projections = chunk1.point_cloud.projections

        point_ids = [-1] * len(point_cloud.tracks)

        for point_id in range(0, npoints):
            point_ids[points[point_id].track_id] = point_id

        f.write("################    SENSORS    ################\n")
        for sensor in chunk1.sensors:
            f.write("Sensor:\t{:s}\t{:d}\t{:s}\t{:d}\n".format(sensor.label, sensor.key, str(sensor.type), isMasterSensor(sensor)))
            f.write("{:d}\t{:d}\t{:.8f}\t{:.8f}\t{:.8f}\n".format(sensor.width, sensor.height, sensor.calibration.f, sensor.calibration.cx, sensor.calibration.cy))
            f.write("{:.8e}\t{:.8e}\t{:.8e}\t{:.8e}\n".format(sensor.calibration.k1, sensor.calibration.k2, sensor.calibration.k3, sensor.calibration.k4))
            f.write("{:.8e}\t{:.8e}\t{:.8e}\t{:.8e}\n".format(sensor.calibration.p1, sensor.calibration.p2, sensor.calibration.p3, sensor.calibration.p4))
            f.write("{:.8e}\t{:.8e}\n".format(sensor.calibration.b1, sensor.calibration.b2))
            if (not (isMasterSensor(sensor))):
                f.write("Master sensor:\t{:d}\n".format(sensor.master.key))
                R = Metashape.Utils.mat2opk(sensor.rotation)
                f.write("{:.8f}\t{:.8f}\t{:.8f}\n".format(sensor.location.x, sensor.location.y, sensor.location.z))                
                f.write("{:.8f}\t{:.8f}\t{:.8f}\n".format(R.x, R.y, R.z))
                if (not (sensor.reference.location is None or sensor.reference.rotation is None)):
                    f.write("{:.8f}\t{:.8f}\t{:.8f}\n".format(sensor.reference.location.x, sensor.reference.location.y, sensor.reference.location.z))                
                    f.write("{:.8f}\t{:.8f}\t{:.8f}\n".format(sensor.reference.rotation.x, sensor.reference.rotation.y, sensor.reference.rotation.z))


        f.write("################    CAMERAS    ################\n")
        R180 = Metashape.Utils.opk2mat(Metashape.Vector((180,0,0)))
        for camera in chunk1.cameras:
            if not camera.type == Metashape.Camera.Type.Regular: #skipping camera track keyframes
                continue
            if not camera.transform: #skipping NA cameras
                continue
            f.write("Camera:\t{:s}\t{:s}\t{:d}\t{:d}\t".format(camera.label, camera.photo.path, camera.key, camera.sensor.key))
            coord = camera.center
            point  = crs.project(T.mulp(coord))
            #rot =  T * camera.transform
            #ang = Metashape.Utils.mat2opk(R180 * rot.rotation())

            m = chunk1.crs.localframe(T.mulp(camera.center)) #transformation matrix to the LSE coordinates in the given point
            R = m * T * camera.transform * Metashape.Matrix().Diag([1, -1, -1, 1])
            row = list()
            for j in range (0, 3): #creating normalized rotation matrix 3x3
                row.append(R.row(j))
                row[j].size = 3
                row[j].normalize()
            R = Metashape.Matrix([row[0], row[1], row[2]])
            ang = Metashape.Utils.mat2opk(R)

            f.write("{:.8f}\t{:.8f}\t{:.8f}\t".format(point.x, point.y, point.z))
            f.write("{:.8f}\t{:.8f}\t{:.8f}\n".format(ang.x, ang.y, ang.z))


        f.write("################  IMAGE POINTS  ################\n")
        for camera in chunk1.cameras:
            if not camera.type == Metashape.Camera.Type.Regular: #skipping camera track keyframes
                continue
            if not camera.transform: #skipping NA cameras
                continue  
            for proj in projections[camera]:
                track_id = proj.track_id
                point_id = point_ids[track_id]
                if point_id < 0:
                    continue
                if not points[point_id].valid:
                    continue
                f.write("ImagePoint:\t{:s}\t{:d}\t{:d}\t{:.8f}\t{:.8f}\n".format(camera.label, camera.key, track_id, proj.coord.x, proj.coord.y))
    
        f.write("################  MARKER LIST  ################\n")
        for marker in chunk1.markers:
            f.write("{:s}\t{:d}\t{:s}\n".format(marker.label, marker.key, str(marker.reference.enabled)))
            if (marker.reference is None or marker.reference.location is None):
                f.write("n/a\tn/a\tn/a\n")
            else:
                f.write("{:.4f}\t{:.4f}\t{:.4f}\n".format(marker.reference.location.x, marker.reference.location.y, marker.reference.location.z))
            if (marker.reference.accuracy == None):
                f.write("-1\t-1\t-1\n")
            else:
                f.write("{:.4f}\t{:.4f}\t{:.4f}\n".format(marker.reference.accuracy.x, marker.reference.accuracy.y, marker.reference.accuracy.z))

        f.write("################  MARKER IMAGE COORDINATE  ################\n")
        for marker in chunk1.markers:
            for camera in marker.projections.keys():
                proj=marker.projections[camera]
                line=("{:s}\t{:d}\t{:d}\t{:.2f}\t{:.2f}\n".format(camera.label, camera.key, marker.key, proj.coord.x, proj.coord.y))
                f.write(line)

        f.write("################  END  ################\n")
        print("Success!")
    except Exception as e:
        print("##############   An exception occurred!!!   ##############")
        print(e)
    finally:
        f.close()

if (len(sys.argv) == 2):
    export(sys.argv[1])