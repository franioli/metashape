import shutil

import Metashape

doc = Metashape.app.document


def main():
    dest_path = Metashape.app.getExistingDirectory("Select output folder:")
    chunk = doc.chunk
    print("Exporting selected cameras ...")
    for camera in chunk.cameras:
        if camera.selected:
            print(camera.photo.path)
            shutil.copy2(camera.photo.path, dest_path)

    print(f"Images exported to {dest_path}.\n")


Metashape.app.addMenuItem("Scripts/Export selected images", main)
