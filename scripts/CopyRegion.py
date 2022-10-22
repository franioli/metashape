import Metashape
import sys
import os

def copy_region():
    doc = Metashape.app.document
    region = doc.chunk.region
    for chunk in doc.chunks:
        chunk.region = region


label = "Plugins/Copy/Copy current region"
Metashape.app.addMenuItem(label, copy_region)
print("To execute this script press {}".format(label))