import numpy as np
import Metashape

from pathlib import Path
from easydict import EasyDict as edict

from lib.utils import (
    create_new_project,
    save_project,
    cameras_from_bundler,
    add_markers,
    copy_camera_estimated_to_reference,
)
from lib.io import read_gcp_file


def create_project(cfg):

    # Define project
    if cfg.create_new_project:
        doc = create_new_project(str(cfg.new_project_name))
        chunk = doc.chunk
    else:
        chunk = Metashape.app.document.chunk

    # Add images
    p = cfg.im_path.glob('*.' + cfg.im_ext)
    images = [str(x) for x in p if x.is_file()]
    chunk.addPhotos(images)

    # Add cameras and tie points from bundler output
    cameras_from_bundler(
        chunk=chunk,
        fname=cfg.bundler_out_path,
        image_list=str(cfg.bundler_out_path.parent / 'list.txt'),
    )

    # Fix Camera location to reference
    if len(cfg.cam_accuracy) == 1:
        accuracy = Metashape.Vector(
            (cfg.cam_accuracy, cfg.cam_accuracy, cfg.cam_accuracy))
    elif len(cfg.cam_accuracy) == 3:
        accuracy = cfg.cam_accuracy
    else:
        print("Wrong input type for accuracy parameter. Provide a list of floats (it can be a list of a single element or of three elements).")
        return
    for i, camera in enumerate(chunk.cameras):
        camera.reference.location = Metashape.Vector(cfg.camera_location[i])
        camera.reference.accuracy = accuracy
        camera.reference.enabled = True

        # copy_camera_estimated_to_reference(
        #     chunk=chunk,
        #     copy_rotations=False,
        #     accuracy=cfg.cam_accuracy
        # )

        # Add GCPs
    gcps = read_gcp_file(cfg.gcp_filename)
    for point in gcps:
        add_markers(
            chunk,
            point['world'],
            point['projections'],
            point['label'],
            cfg.gcp_accuracy,
        )

    # Sensor calibraion
    for i, sensor in enumerate(chunk.sensors):
        cal = Metashape.Calibration()
        cal.load(str(cfg.calib_filename[i]))
        sensor.user_calib = cal
        sensor.fixed_calibration = True
        if cfg.prm_to_fix:
            sensor.fixed_params = cfg.prm_to_fix
        print(f'sensor {sensor} loaded.')

    if cfg.optimize_cameras:
        chunk.optimizeCameras(fit_f=True, tiepoint_covariance=True)

    # Save project
    if cfg.create_new_project:
        save_project(doc, str(cfg.new_project_name))

    print('Script ended successfully')


if __name__ == '__main__':

    root_dir = Path('/mnt/d/metashape/')
    # root_dir =  Path('C:/Users/Francesco/metashape/'),

    cfg = edict({
        'create_new_project': False,  # False,  #
        'new_project_name': root_dir / 'test.psx',

        'im_path': root_dir / 'data/images/',
        'bundler_out_path': root_dir / 'data/belpy_epoch_0.out',
        'gcp_filename': root_dir / 'data/gcps.txt',
        'calib_filename': [
            root_dir / 'data/belpy_35mm_280722_selfcal_all.xml',
            root_dir / 'data/belpy_24mm_280722_selfcal_all.xml',
        ],

        'im_ext': 'jpg',
        'camera_location': [
            [309.261, 301.051, 135.008],    # IMG_1289
            [151.962, 99.065, 91.643],      # IMG_2814
        ],
        'gcp_accuracy': [0.01, 0.01, 0.01],
        'cam_accuracy': [0.001, 0.001, 0.001],
        'prm_to_fix': ['Cx', 'Cy', 'B1', 'B2', 'K1', 'K2', 'K3', 'K4', 'P1', 'P2'],

        'optimize_cameras': True,
    })

    create_project(cfg)
