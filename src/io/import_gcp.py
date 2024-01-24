# image_name, gcp_name, image_u, image_v
# IMG_0001.JPG,point 1,100,200
# IMG_0001.JPG,point 2,345,400
# IMG_0002.JPG,point 2,786,211

import Metashape


def getMarker(chunk, label):
    for marker in chunk.markers:
        if marker.label == label:
            return marker
    return None


def getCamera(chunk, label):
    for camera in chunk.cameras:
        if camera.label == label:
            return camera
    return None


def main():
    path = Metashape.app.getOpenFileName("Select output folder:")

    chunk = Metashape.app.document.chunk

    with open(path, "rt") as input:
        content = input.readlines()

    for line in content:
        c_label, m_label, x_proj, y_proj = line.split(",")

        camera = getCamera(chunk, c_label)
        if not camera:
            print(f"{c_label} camera not found in project")
            continue

        marker = getMarker(chunk, m_label)
        if not marker:
            marker = chunk.addMarker()
            marker.label = m_label

        marker.projections[camera] = Metashape.Marker.Projection(
            Metashape.Vector([float(x_proj), float(y_proj)]), True
        )
        print(f"Added projection for {m_label} on {c_label}")


Metashape.app.addMenuItem("Scripts/import GCPs", main)
