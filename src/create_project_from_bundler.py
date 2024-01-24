from pathlib import Path

import Metashape
from easydict import EasyDict as edict

from .utils.io import read_gcp_file
from .utils.utils import (
    add_markers,
    cameras_from_bundler,
    create_new_project,
    save_project,
)


def create_project(cfg):
    # Define project
    if cfg.create_new_project:
        doc = create_new_project(str(cfg.project_name))
        if cfg.force_overwrite_projects:
            doc.read_only = False
        chunk = doc.chunk
        print(f"Created project {str(cfg.project_name)}.")
    else:
        chunk = Metashape.app.document.chunk

    # Add images
    p = cfg.im_path.glob("*." + cfg.im_ext)
    images = [str(x) for x in p if x.is_file()]
    chunk.addPhotos(images)

    # Add cameras and tie points from bundler output
    cameras_from_bundler(
        chunk=chunk,
        fname=cfg.bundler_file_path,
        image_list=cfg.bundler_im_list,
    )

    # Fix Camera location to reference
    if len(cfg.cam_accuracy) == 1:
        accuracy = Metashape.Vector(
            (cfg.cam_accuracy, cfg.cam_accuracy, cfg.cam_accuracy)
        )
    elif len(cfg.cam_accuracy) == 3:
        accuracy = cfg.cam_accuracy
    else:
        print(
            "Wrong input type for accuracy parameter. Provide a list of floats (it can be a list of a single element or of three elements)."
        )
        return
    for i, camera in enumerate(chunk.cameras):
        camera.reference.location = Metashape.Vector(cfg.camera_location[i])
        camera.reference.accuracy = accuracy
        camera.reference.enabled = True

    # Add GCPs
    gcps = read_gcp_file(cfg.gcp_filename)
    for point in gcps:
        add_markers(
            chunk,
            point["world"],
            point["projections"],
            point["label"],
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
        print(f"sensor {sensor} loaded.")

    # Optimize Cameras
    if cfg.optimize_cameras:
        chunk.optimizeCameras(fit_f=True, tiepoint_covariance=True)

    # Build Dense Cloud
    if cfg.build_dense:
        chunk.buildDepthMaps(
            downscale=1,
            filter_mode=Metashape.FilterMode.ModerateFiltering,
            reuse_depth=False,
            max_neighbors=16,
            subdivide_task=True,
            workitem_size_cameras=20,
            max_workgroup_size=100,
        )
        chunk.buildDenseCloud(
            point_colors=True,
            point_confidence=True,
            keep_depth=True,
            max_neighbors=2,
            subdivide_task=True,
            workitem_size_cameras=20,
            max_workgroup_size=100,
        )
        chunk.exportPoints(
            path=str(cfg.dense_path / cfg.dense_name),
            source_data=Metashape.DataSource.DenseCloudData,
        )

    # Save project
    if cfg.create_new_project:
        save_project(doc, str(cfg.project_name))

    print("Script ended successfully")


if __name__ == "__main__":
    root_dir = Path("/home/photogrammetry/belpy/")
    # root_dir = Path('/mnt/d/metashape/')
    # root_dir =  Path('C:/Users/Francesco/metashape/'),

    projects = []
    im_paths = []
    bundler_paths = []
    bundler_im_lists = []
    gcp_filenames = []
    dense_names = []
    for epoch in range(27):
        projects.append(root_dir / f"metashape/epoch_{epoch}/belpy_epoch_{epoch}.psx")
        im_paths.append(root_dir / f"metashape/epoch_{epoch}/data/images/")
        bundler_paths.append(root_dir / f"res/bundler_output/belpy_epoch_{epoch}.out")
        bundler_im_lists.append(root_dir / f"metashape/epoch_{epoch}/data/im_list.txt")
        gcp_filenames.append(root_dir / f"metashape/epoch_{epoch}/data/gcps.txt")
        dense_names.append(f"dense_epoch_{epoch}.ply")

    cfg = edict(
        {
            "create_new_project": True,  # False,  #
            "project_name": root_dir / "test.psx",
            "im_path": root_dir / "data/images/",
            "bundler_file_path": root_dir / "data/belpy_epoch_0.out",
            "bundler_im_list": root_dir / "data/list.txt",
            "gcp_filename": root_dir / "data/gcps.txt",
            "calib_filename": [
                root_dir / "metashape/calib/belpy_35mm_280722_selfcal_all.xml",
                root_dir / "metashape/calib/belpy_24mm_280722_selfcal_all.xml",
            ],
            "im_ext": "jpg",
            "camera_location": [
                [309.261, 301.051, 135.008],  # IMG_1289
                [151.962, 99.065, 91.643],  # IMG_2814
            ],
            "gcp_accuracy": [0.01, 0.01, 0.01],
            "cam_accuracy": [0.001, 0.001, 0.001],
            "prm_to_fix": ["Cx", "Cy", "B1", "B2", "K1", "K2", "K3", "K4", "P1", "P2"],
            "optimize_cameras": True,
            "build_dense": True,
            "dense_path": root_dir / "metashape/dense_clouds",
            "dense_name": "dense.ply",
            "force_overwrite_projects": True,
        }
    )

    print("Processing started:")
    print("-----------------------")

    for epoch, project in enumerate(projects):
        print("-----------------------\n")
        print(f"Processing epoch {epoch}")

        cfg.project_name = project
        cfg.im_path = im_paths[epoch]
        cfg.bundler_file_path = bundler_paths[epoch]
        cfg.bundler_im_list = bundler_im_lists[epoch]
        cfg.gcp_filename = gcp_filenames[epoch]
        cfg.dense_name = dense_names[epoch]

        create_project(cfg)

        print(f"Epoch {epoch} completed.\n")
