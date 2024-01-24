import csv
import math
import os
import random

# Import the functions from func.py
# add path to Python Path in order to import from src
import sys

import Metashape

sys.path.append("src")

from func import (
    add_cameras_gauss_noise,
    add_markers_gauss_noise,
    add_observations_gauss_noise,
    compute_coordinate_offset,
    save_sparse,
)

NaN = float("NaN")


# ###############################  SETUP #######################################
# Update the parameters below to tailor the script to your project.

# Directory where output will be stored and active control file is saved.
# Note use of '/' in the path (not '\'); end the path with '/'
# The files will be generated in a sub-folder named "Monte_Carlo_output"
# Change the path to the one you want, but there's no need to change act_ctrl_file.
dir_path = "data/square"
act_ctrl_file = "active_ctrl_indices.txt"

# Define how many times bundle adjustment (Metashape 'optimisation') will be carried out.
# 4000 used in original work, as a reasonable starting point.
num_randomisations = 200

# Define the camera parameter set to optimise in the bundle adjustment.
optimise_intrinsics = {
    "f": True,
    "cx": True,
    "cy": True,
    "b1": False,
    "b2": False,
    "k1": True,
    "k2": True,
    "k3": False,
    "k4": False,
    "p1": True,
    "p2": True,
}

# Points are exported as floats in binary ply files for speed and size, and thus cannot represent very small changes in large geographic coordinates.
# Thus, the offset below can be set to form a local origin and ensure numerical
# precision is not lost when coordinates are saved as floats.
# The offset will be subtracted from point coordinates.
# [RECOMMENDED] - Leave as NaN; the script will automatically calculate and apply a suitable offset, which will be saved as a text file for further processing, OR edit the line to impose a specific offset of your choice -
# e.g.  pts_offset = Metashape.Vector( [266000, 4702000, 0] )
pts_offset = Metashape.Vector([NaN, NaN, NaN])

###############################   END OF SETUP   ###############################
################################################################################

# Initialisation
ref_project_path = os.path.join(dir_path, "enrich_square_GT.psx")
ref_doc = Metashape.Document()
ref_doc.open(ref_project_path)

doc = ref_doc.copy()
doc.save(os.path.join(dir_path, "dummy.psx"))
del ref_doc

# Get the chunk from the document
chunk = doc.chunk

# Need CoordinateSystem object, but MS only returns 'None' if an arbitrary coordinate system is being used
# thus need to set manually in this case; otherwise use the Chunk coordinate system.
if chunk.crs is None:
    crs = Metashape.CoordinateSystem(
        'LOCAL_CS["Local Coordinates (m)",LOCAL_DATUM["Local Datum",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]]]'
    )
    chunk.crs = crs
else:
    crs = chunk.crs

# Find which markers are enabled for use as control points in the bundle adjustment
act_marker_flags = [m.reference.enabled for m in chunk.markers]
num_act_markers = sum(act_marker_flags)

# Find which camera orientations are enabled for use as control in the bundle adjustment
act_cam_orient_flags = [cam.reference.enabled for cam in chunk.cameras]
num_act_cam_orients = sum(act_cam_orient_flags)

# Reset the random seed, so that all equivalent runs of this script are started identically
random.seed(1)

# Carry out an initial bundle adjustment to ensure that everything subsequent has a consistent reference starting point.
chunk.optimizeCameras(
    fit_f=optimise_intrinsics["f"],
    fit_cx=optimise_intrinsics["cx"],
    fit_cy=optimise_intrinsics["cy"],
    fit_b1=optimise_intrinsics["b1"],
    fit_b2=optimise_intrinsics["b2"],
    fit_k1=optimise_intrinsics["k1"],
    fit_k2=optimise_intrinsics["k2"],
    fit_k3=optimise_intrinsics["k3"],
    fit_k4=optimise_intrinsics["k4"],
    fit_p1=optimise_intrinsics["p1"],
    fit_p2=optimise_intrinsics["p2"],
    tiepoint_covariance=True,
)

# Compute sigma02 for the sparse points
print("Computing sparse point sigma0...")
proj = chunk.point_cloud.projections


# Compute the re-projection error
# chunk = doc.chunk
# point_cloud = chunk.point_cloud
# points = point_cloud.points
# error, tie_points = [], []
# cam_list, cam_rmse, cam_std, cam_min, cam_max, cam_std = [], [], [], [], [], []
# for camera in [cam for cam in doc.chunk.cameras if cam.transform]:
#     point_index = 0
#     photo_num = 0
#     cam_error = []
#     for proj in doc.chunk.point_cloud.projections[camera]:
#         track_id = proj.track_id
#         while point_index < len(points) and points[point_index].track_id < track_id:
#             point_index += 1
#         if point_index < len(points) and points[point_index].track_id == track_id:
#             if not points[point_index].valid:
#                 continue
#             dist = camera.error(points[point_index].coord, proj.coord).norm() ** 2
#             error.append(dist)
#             cam_error.append(dist)
#             photo_num += 1
#     tie_points.append(photo_num)
#     cam_list.append(camera.label)
#     cam_rmse.append(round(math.sqrt(sum(error) / len(error)), 3))
#     cam_std.append(round(statistics.stdev(error), 3))
#     cam_max.append(round(max(error), 3))
#     cam_min.append(round(min(error), 3))


save_sparse(
    chunk,
    dir_path + "sparse_pts_reference_cov.csv",
    save_color=True,
    save_cov=True,
    sep=",",
)

# If required, calculate the mean point coordinate to use as an offset
if math.isnan(pts_offset[0]):
    # TODO: test this function with UTM coordinates
    pts_offset = compute_coordinate_offset(chunk)

# Save the used offset to text file
with open(dir_path + "_coordinate_local_origin.txt", "w") as f:
    fwriter = csv.writer(f, dialect="excel-tab", lineterminator="\n")
    fwriter.writerow(pts_offset)
    f.close()

# Export a text file of observation distances and ground dimensions of pixels from which relative precisions can be calculated
# File will have one row for each observation, and three columns:
# cameraID	  ground pixel dimension (m)   observation distance (m)
points = chunk.point_cloud.points
npoints = len(points)
camera_index = 0
with open(dir_path + "_observation_distances.txt", "w") as f:
    fwriter = csv.writer(f, dialect="excel-tab", lineterminator="\n")
    for camera in chunk.cameras:
        camera_index += 1
        if not camera.transform:
            continue

        fx = camera.sensor.calibration.f

        point_index = 0
        for proj in chunk.point_cloud.projections[camera]:
            track_id = proj.track_id
            while point_index < npoints and points[point_index].track_id < track_id:
                point_index += 1
            if point_index < npoints and points[point_index].track_id == track_id:
                if not points[point_index].valid:
                    continue
                dist = (
                    chunk.transform.matrix.mulp(camera.center)
                    - chunk.transform.matrix.mulp(
                        Metashape.Vector(
                            [
                                points[point_index].coord[0],
                                points[point_index].coord[1],
                                points[point_index].coord[2],
                            ]
                        )
                    )
                ).norm()
                fwriter.writerow(
                    [camera_index, "{0:.4f}".format(dist / fx), "{0:.2f}".format(dist)]
                )

    f.close()

# Export a text file with the coordinate system
with open(dir_path + "_coordinate_system.txt", "w") as f:
    fwriter = csv.writer(f, dialect="excel-tab", lineterminator="\n")
    fwriter.writerow([crs])
    f.close()

# Make a copy of the chunk to use as a zero-error reference chunk
original_chunk = chunk.copy()
original_chunk.label = "original_chunk"

# Set the original_marker locations be zero error, from which we can add simulated error
for original_marker in original_chunk.markers:
    if original_marker.position is not None:
        original_marker.reference.location = crs.project(
            original_chunk.transform.matrix.mulp(original_marker.position)
        )

# Set the original_marker and point projections to be zero error, from which we can add simulated error
original_points = original_chunk.point_cloud.points
original_point_proj = original_chunk.point_cloud.projections
npoints = len(original_points)
for camera in original_chunk.cameras:
    if not camera.transform:
        continue

    point_index = 0
    for original_proj in original_point_proj[camera]:
        track_id = original_proj.track_id
        while (
            point_index < npoints and original_points[point_index].track_id < track_id
        ):
            point_index += 1
        if point_index < npoints and original_points[point_index].track_id == track_id:
            if not original_points[point_index].valid:
                continue
            original_proj.coord = camera.project(original_points[point_index].coord)

    # Set the original marker points be zero error, from which we can add simulated error
    # Note, need to set from chunk because original_marker.position will be continuously updated
    for markerIDx, original_marker in enumerate(original_chunk.markers):
        if (not original_marker.projections[camera]) or (
            not chunk.markers[markerIDx].position
        ):
            continue
        original_marker.projections[camera].coord = camera.project(
            chunk.markers[markerIDx].position
        )

# Export this 'zero error' marker data to file
original_chunk.exportMarkers(dir_path + "referenceMarkers.xml")

# Derive x and y components for image measurement precisions
tie_proj_x_stdev = chunk.tiepoint_accuracy / math.sqrt(2)
tie_proj_y_stdev = chunk.tiepoint_accuracy / math.sqrt(2)
marker_proj_x_stdev = chunk.marker_projection_accuracy / math.sqrt(2)
marker_proj_y_stdev = chunk.marker_projection_accuracy / math.sqrt(2)

# Carry out an adjustment with a fixed camera to define a benchmark set of sparse points for later comparison.
# Ideally, this should be the same as the sparse points in the zero-error chunk, but there do seem to be some differences.
# Make a copy of the zero-error reference chunk to run the adjustment on
temp_chunk = original_chunk.copy()

# Carry out a bundle adjustment with a fixed camera model.
temp_chunk.optimizeCameras(
    fit_f=False,
    fit_cx=False,
    fit_cy=False,
    fit_b1=False,
    fit_b2=False,
    fit_k1=False,
    fit_k2=False,
    fit_k3=False,
    fit_k4=False,
    fit_p1=False,
    fit_p2=False,
    tiepoint_covariance=False,
)

# Export the sparse point cloud
temp_chunk.exportPoints(
    dir_path + "sparse_pts_reference.ply",
    source_data=Metashape.DataSource.PointCloudData,
    save_normals=False,
    save_colors=False,
    format=Metashape.PointsFormatPLY,
    crs=crs,
    shift=pts_offset,
)

# Delete this chunk
doc.remove([temp_chunk])

# Save the project
doc.read_only = False


###############################################################################
# Counter for the number of bundle adjustments carried out, to prepend to files
file_idx = 1

# Make the ouput directory if it doesn't exist
dir_path = dir_path + "_Monte_Carlo_output/"
os.makedirs(dir_path, exist_ok=True)

# Main set of nested loops which control the repeated bundle adjustment
for line_ID in range(0, num_randomisations):
    # Copy original chunk and set label
    chunk = original_chunk.copy()
    chunk.label = f"MC_{file_idx:04d}"
    doc.chunk = chunk
    point_proj = chunk.point_cloud.projections

    # Reset the camera coordinates if they are used for georeferencing
    if num_act_cam_orients > 0:
        add_cameras_gauss_noise(chunk)

    # add noise to the marker locations
    add_markers_gauss_noise(chunk)

    # add noise to the observations
    add_observations_gauss_noise(chunk)

    # Construct the output file names
    out_file = f"{file_idx:04d}_MA{chunk.marker_location_accuracy[0]:0.5f}_PA{chunk.marker_projection_accuracy:0.5f}_TA{chunk.tiepoint_accuracy:0.5f}_NAM{num_act_markers:03d}_LID{line_ID + 1:03d}"
    out_gc_file = out_file + "_GC.txt"
    out_cams_c_file = out_file + "_cams_c.txt"
    out_cam_file = out_file + "_cams.xml"
    print(out_gc_file)

    # Bundle adjustment
    chunk.optimizeCameras(
        fit_f=optimise_intrinsics["f"],
        fit_cx=optimise_intrinsics["cx"],
        fit_cy=optimise_intrinsics["cy"],
        fit_b1=optimise_intrinsics["b1"],
        fit_b2=optimise_intrinsics["b2"],
        fit_k1=optimise_intrinsics["k1"],
        fit_k2=optimise_intrinsics["k2"],
        fit_k3=optimise_intrinsics["k3"],
        fit_k4=optimise_intrinsics["k4"],
        fit_p1=optimise_intrinsics["p1"],
        fit_p2=optimise_intrinsics["p2"],
        tiepoint_covariance=True,
    )

    # Export the control (catch and deal with legacy syntax)
    try:
        chunk.exportReference(
            dir_path + out_gc_file,
            Metashape.ReferenceFormatCSV,
            items=Metashape.ReferenceItemsMarkers,
        )
        chunk.exportReference(
            dir_path + out_cams_c_file,
            Metashape.ReferenceFormatCSV,
            items=Metashape.ReferenceItemsCameras,
        )
    except:
        chunk.exportReference(dir_path + out_gc_file, "csv")

    # Export the cameras
    chunk.exportCameras(
        dir_path + out_cam_file, format=Metashape.CamerasFormatXML, crs=crs
    )  # , rotation_order=Metashape.RotationOrderXYZ)

    # Export the calibrations [NOTE - only one camera implemented in export here]
    for sensorIDx, sensor in enumerate(chunk.sensors):
        sensor.calibration.save(
            dir_path + out_file + "_cal" + "{0:01d}".format(sensorIDx + 1) + ".xml"
        )

    # Export the sparse point cloud
    chunk.exportPoints(
        dir_path + out_file + "_pts.ply",
        source_data=Metashape.DataSource.PointCloudData,
        save_normals=False,
        save_colors=False,
        format=Metashape.PointsFormatPLY,
        crs=crs,
        shift=pts_offset,
    )

    # Increment the file counter
    file_idx = file_idx + 1

    # Delete the chunk
    doc.remove([chunk])

    # Save the project
    doc.read_only = False
    doc.save()

    # Temporary disable scalebars
    # # Reset the scalebar lengths and add noise
    # for scalebarIDx, scalebar in enumerate(chunk.scalebars):
    #     if scalebar.reference.distance:
    #         if not scalebar.reference.accuracy:
    #             scalebar.reference.distance = original_chunk.scalebars[
    #                 scalebarIDx
    #             ].reference.distance + random.gauss(0, chunk.scalebar_accuracy)
    #         else:
    #             scalebar.reference.distance = original_chunk.scalebars[
    #                 scalebarIDx
    #             ].reference.distance + random.gauss(0, scalebar.reference.accuracy)
