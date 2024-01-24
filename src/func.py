import math
import random

import Metashape


def save_sparse(
    chunk: Metashape.Chunk,
    file_path: str,
    save_color: bool = True,
    save_cov: bool = True,
    sep: str = ",",
    header: bool = True,
):
    points = chunk.point_cloud.points
    T = chunk.transform.matrix
    if (
        chunk.transform.translation
        and chunk.transform.rotation
        and chunk.transform.scale
    ):
        T = chunk.crs.localframe(T.mulp(chunk.region.center)) * T
    R = T.rotation() * T.scale()

    with open(file_path, "w") as f:
        if header:
            header = [
                "track_id",
                "x",
                "y",
                "z",
            ]
            if save_color:
                header.extend(["r", "g", "b"])
            if save_cov:
                header.extend(
                    [
                        "sX",
                        "sY",
                        "sZ",
                        "covXX",
                        "covXY",
                        "covXZ",
                        "covYY",
                        "covYZ",
                        "covZZ",
                        "var",
                    ]
                )
            f.write(f"{sep.join(header)}\n")
        for point in points:
            if not point.valid:
                continue

            coord = point.coord
            coord = T * coord
            line = [
                point.track_id,
                coord.x,
                coord.y,
                coord.z,
            ]
            if save_color:
                track_id = point.track_id
                color = chunk.point_cloud.tracks[track_id].color
                line.extend([color[0], color[1], color[2]])
            if save_cov:
                cov = point.cov
                cov = R * cov * R.t()
                u, s, v = cov.svd()
                var = math.sqrt(sum(s))  # variance vector length
                line.extend(
                    [
                        math.sqrt(cov[0, 0]),
                        math.sqrt(cov[1, 1]),
                        math.sqrt(cov[2, 2]),
                        cov[0, 0],
                        cov[0, 1],
                        cov[0, 2],
                        cov[1, 1],
                        cov[1, 2],
                        cov[2, 2],
                        var,
                    ]
                )
            f.write(f"{sep.join([str(x) for x in line])}\n")


def compute_coordinate_offset(chunk: Metashape.Chunk):
    crs = chunk.crs
    if crs is None:
        raise ValueError("Chunk coordinate system is not set")

    points = [point.coord for point in chunk.point_cloud.points if point.valid]

    if not points:
        return Metashape.Vector([0, 0, 0])

    npoints = len(points)
    pts_offset = Metashape.Vector(map(sum, zip(*points))) / npoints

    pts_offset = crs.project(chunk.transform.matrix.mulp(pts_offset[:3]))
    pts_offset = Metashape.Vector(round(coord, -2) for coord in pts_offset)

    return pts_offset


def add_cameras_gauss_noise(chunk: Metashape.Chunk):
    for cam in chunk.cameras:
        # Skip cameras without a transform
        if not cam.transform:
            continue

        # If no sigma is provided for each camera, use the chunk's camera accuracy
        if not cam.reference.accuracy:
            sigma = chunk.camera_location_accuracy
        else:
            sigma = cam.reference.accuracy

        # Compute the noise vector
        noise = Metashape.Vector([random.gauss(0, s) for s in sigma])

        # Add the noise to the camera location
        cam.reference.location += noise


def add_markers_gauss_noise(chunk: Metashape.Chunk):
    for marker in chunk.markers:
        if not marker.reference.accuracy:
            sigma = chunk.marker_location_accuracy
        else:
            sigma = marker.reference.accuracy

        noise = Metashape.Vector([random.gauss(0, s) for s in sigma])
        marker.reference.location += noise


def add_observations_gauss_noise(chunk: Metashape.Chunk):
    tie_proj_x_stdev = chunk.tiepoint_accuracy / math.sqrt(2)
    tie_proj_y_stdev = chunk.tiepoint_accuracy / math.sqrt(2)
    marker_proj_x_stdev = chunk.marker_projection_accuracy / math.sqrt(2)
    marker_proj_y_stdev = chunk.marker_projection_accuracy / math.sqrt(2)
    point_proj = chunk.point_cloud.projections

    for camera in chunk.cameras:
        # Skip cameras without a transform
        if not camera.transform:
            continue

        # Tie points (matches)
        projections = point_proj[camera]
        for proj in projections:
            noise = Metashape.Vector(
                [random.gauss(0, tie_proj_x_stdev), random.gauss(0, tie_proj_y_stdev)]
            )
            proj.coord += noise

        # Markers
        for marker in chunk.markers:
            if not marker.projections[camera]:
                continue
            noise = Metashape.Vector(
                [
                    random.gauss(0, marker_proj_x_stdev),
                    random.gauss(0, marker_proj_y_stdev),
                ]
            )
            marker.projections[camera].coord += noise
