import numpy as np
from src import utils
from pathlib import Path
import bpy
import mathutils
import sys
from scipy.spatial import Voronoi
from src.voronoi import make_segments, generate_n_random_points
from src.geometry import make_voronoi_structure, check_intersection, join_all_objects
import json
from src.utils import import_file_stl, get_bounding_box, export_blend, clear_scene


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


def script_from_json(json_path: Path, out: Path):
    file = open(json_path)
    data = json.load(file)
    file.close()

    thickness: float = data.get("thickness")  # radius
    mesh_list: list = data.get("meshes")
    original_mesh_names: list[str] = []
    all_random_points: list[mathutils.Vector] = []
    #  0) clean blender scene (remove default cube, light, camera)
    clear_scene()
    for current_mesh in mesh_list:
        density: int = current_mesh.get("density")  # density is number of points for unit cube of blender
        mesh_path: Path = Path(current_mesh.get("path"))
        mesh_name = mesh_path.stem  # if is a stl then the name of the mesh is the name of the file!!!

        #  1) import mesh
        import_file_stl(file=mesh_path)
        original_mesh_names.append(mesh_name)  # for later when merging

        #  2) calculate bounding box
        current_object = bpy.data.objects[mesh_name]
        corner1, corner2 = get_bounding_box(obj=current_object)

        min_x, min_y, min_z = corner1[0], corner1[1], corner1[2]
        max_x, max_y, max_z = corner2[0], corner2[1], corner2[2]

        volume = abs(max_x - min_x) * abs(max_y - min_y) * abs(max_z - min_z)  # the abs function should not
        # really be necessary as max should be greater than min

        n_points: int = int(density * volume)  # total number of points to be created

        random_points = generate_n_random_points(n=n_points,
                                                 min_x=min_x,
                                                 max_x=max_x,
                                                 min_y=min_y,
                                                 max_y=max_y,
                                                 min_z=min_z,
                                                 max_z=max_z)

        #  3) filter pints inside mesh
        filtered_points: list[mathutils.Vector] = check_intersection(vertices=random_points, obj=current_object)
        #  4) append together all points from all meshes
        all_random_points.extend(filtered_points)

    compatible_points = [np.array((p[0], p[1], p[2])) for p in all_random_points]
    print(f"N of random points: {len(compatible_points)}")
    #  5) calculate voronoi from points
    voronoi = Voronoi(points=compatible_points)

    voronoi_ridge_vertices = voronoi.ridge_vertices

    # these two are needed to construct the geometry
    voronoi_vertices: np.array = voronoi.vertices
    voronoi_segments: list[tuple] = make_segments(ridge_vertices=voronoi_ridge_vertices)
    print(f"N vertices: {len(voronoi_vertices)}")
    print(f"N segment: {len(voronoi_segments)}")

    #  6) create voronoi geometry
    voronoi_structure_name: str = "voronoi_structure"
    make_voronoi_structure(name=voronoi_structure_name,
                           vertices=voronoi_vertices, segments=voronoi_segments, radius=thickness)

    #  7) join original meshes together (or is better to have an extra one already joined???)
    original_objects: list[bpy.types.Object] = [bpy.data.objects[name] for name in original_mesh_names]
    join_all_objects(selected_objects=original_objects, new_name="merged_objects")

    export_blend(file_path=out.as_posix())
    # TODO:
    #  8) boolean operation between voronoi mesh and joined original
    #  extra: should we also include the wireframe of the original????
    #  9) export result as stl

    sys.exit(0)

