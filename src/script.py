import numpy as np
from src import utils
from pathlib import Path
import bpy
import mathutils
import sys
from scipy.spatial import Voronoi
from src.voronoi import make_segments, generate_n_random_points
from src.geometry import (make_voronoi_structure, check_intersection, join_all_objects, boolean_operation,
                          wireframe_operation, merge_doubles)
import json
from src.utils import import_file_stl, get_bounding_box, export_blend, clear_scene, export_stl_file, remove_objects


def script_from_json(json_path: Path, out: Path):
    file = open(json_path)
    data = json.load(file)
    file.close()

    thickness: float = data.get("thickness")  # radius
    original_file: str = data.get("original")   # original un-subdivided mesh
    mesh_list: list = data.get("meshes")        # separated meshes
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

    #  7) remove original objects
    original_objects: list[bpy.types.Object] = [bpy.data.objects[name] for name in original_mesh_names]
    remove_objects(original_objects)
    
    #  7.1) import original mesh to use
    original_path: Path = Path(original_file)
    original_name: str = original_path.stem
    import_file_stl(file=original_path)

    #  8) boolean operation between voronoi mesh and joined original
    boolean_operation(name_a=voronoi_structure_name, name_b=original_name)

    #  8.1) extra wireframe of the original
    wireframe_operation(name=original_name, thickness=thickness*2)

    # export_blend(file_path=out.as_posix())

    final_objects: list[bpy.types.Object] = [bpy.data.objects[original_name],
                                             bpy.data.objects[voronoi_structure_name]]
    #  9) merge and export result as stl
    final_name: str = "output"
    join_all_objects(selected_objects=final_objects, new_name=final_name)

    #  10) merge closest vertex
    merge_doubles(object_name=final_name, max_dist=thickness/2)

    export_stl_file(output=Path(out))

    sys.exit(0)

