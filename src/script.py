import numpy as np

from src import utils
from pathlib import Path
import bpy
import sys
from scipy.spatial import Voronoi
from src.voronoi import make_segments
from src.geometry import make_voronoi_structure
import mathutils
import json


def script_from_points(source: Path, output: Path, point_file: Path):
    utils.clear_scene()
    utils.import_file_obj(file=point_file)
    objects_in_scene = bpy.data.objects
    if len(objects_in_scene) > 1 or len(objects_in_scene) == 0:
        print("imported file should contain 1 mesh only (for now)")
        sys.exit(1)
    points = utils.get_point_from_obj(obj=objects_in_scene[0])
    voronoi = Voronoi(points=points)
    voronoi_ridge_vertices = voronoi.ridge_vertices

    # these two are needed to construct the geometry
    voronoi_vertices: np.array = voronoi.vertices
    voronoi_segments: list[tuple] = make_segments(ridge_vertices=voronoi_ridge_vertices)
    print("made segments")
    #min_distance, _, _ = utils.find_minimum_distance(voronoi_vertices)
    radius: float = 0.01#min_distance/2
    print("calculated radius")
    utils.clear_scene()
    print("starting making voronoi structure")
    make_voronoi_structure(name="voronoi_structure", vertices=voronoi_vertices, segments=voronoi_segments, radius=radius)

    utils.export_stl_file(output=output)


# density is the number of point per 1 unit of volume
def script_start(source: Path, output: Path, density: int = 100, radius: float = 1, points_file: Path = None):
    utils.clear_scene()  # in case we have the default cube, camera and light

    utils.import_file_stl(file=source)

    # TODO for now the imported file should contain only one object/mesh
    objects_in_scene = len(bpy.data.objects)
    if objects_in_scene > 1 or objects_in_scene == 0:
        print("imported file should contain 1 mesh only (for now)")
        sys.exit(1)

    b_box_min, b_box_max = utils.get_bounding_box(obj=bpy.data.objects[0])

    x_size, y_size, z_size = utils.bounding_box_size(corner_min=b_box_min, corner_max=b_box_max)

    volume = x_size * y_size * z_size

    total_num_points: int = int(density * volume)


def script_from_json(json_path: Path):
    file = open(json_path)
    data = json.load(file)
    file.close()

    thickness: float = data.get("thickness")
    mesh_list: list = data.get("meshes")
    for current_mesh in mesh_list:
        density: int = current_mesh.get("density")  # density is number of points for unit cube
        mesh_path: Path = Path(current_mesh.get("path"))

        # TODO:
        #  1) import mesh
        #  2) calculate bounding box
        #  3) filter pints inside mesh
        #  4) append together all points from all meshes
        #  5) calculate voronoi from points
        #  6) create voronoi geometry
        #  7) join original meshes together (or is better to have an extra one already joined???)
        #  8) boolean operation between voronoi mesh and joined original
        #  extra: should we also include the wireframe of the original????
        #  9) export result as stl



