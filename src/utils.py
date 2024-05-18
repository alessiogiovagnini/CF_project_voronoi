import sys
import bpy
import mathutils  # import mathutils after bpy !!!!
import numpy as np
from pathlib import Path


def clear_scene():
    for obj in bpy.data.objects:
        bpy.data.objects.remove(obj, do_unlink=True)


def import_file_obj(file: Path):
    if file.is_file():
        bpy.ops.wm.obj_import(filepath=file.as_posix())
    else:
        print(f"selected obj file: {file} is not valid")
        sys.exit(1)


# find the minimum distance between any point in the array, is there a way to make it faster than O(n^2)???
def find_minimum_distance(points: np.array) -> tuple[float, np.array, np.array]:
    point1 = None
    point2 = None
    min_distance: float = sys.float_info.max
    for p1 in points:
        for p2 in points:
            dist = np.linalg.norm(p1 - p2)
            if dist > 0:
                if dist < min_distance:
                    min_distance = dist
                    point1 = p1
                    point2 = p2
    return min_distance, point1, point2


def get_point_from_obj(obj: bpy.types.Object) -> np.array:
    return np.array([[v.co[0], v.co[1], v.co[2]] for v in obj.data.vertices])


def import_file_stl(file: Path):
    if file.is_file():
        bpy.ops.import_mesh.stl(filepath=file.as_posix())
    else:
        print(f"selected file: {file.as_posix()} is invalid")
        sys.exit(1)


def export_stl_file(output: Path):
    # TODO, need to select the object???
    bpy.ops.export_mesh.stl(filepath=output.as_posix())


def get_bounding_box(obj: bpy.types.Object) -> tuple[mathutils.Vector, mathutils.Vector]:
    box = obj.bound_box
    p = [obj.matrix_world @ mathutils.Vector(corner) for corner in box]
    sp = sorted(p, key=lambda k: [k[0], k[1], k[2]])  # sort so that the first and last element are the corners
    return sp[0], sp[-1]


def bounding_box_size(corner_min: mathutils.Vector, corner_max: mathutils.Vector) -> tuple[float, float, float]:
    x_size: float = corner_max[0] - corner_min[0]
    y_size: float = corner_max[1] - corner_min[1]
    z_size: float = corner_max[2] - corner_min[2]
    return abs(x_size), abs(y_size), abs(z_size)


# read all vertices of an object, this can be used to generate points in case the object is a mesh where every
# vertex is a disconnected point
def get_points_from_object(obj: bpy.types.Object) -> list[mathutils.Vector]:
    points: list[mathutils.Vector] = []
    for v in obj.data.vertices:
        points.append(v.co)
    return points


# TODO need to check if this works
def get_oriented_bounding_box(obj: bpy.types.Object):
    oj = bpy.context.object
    verts = [v.co for v in oj.data.vertices]

    points = np.asarray(verts)
    means = np.mean(points, axis=1)

    cov = np.cov(points, y=None, rowvar=0, bias=1)

    v, vect = np.linalg.eig(cov)

    tvect = np.transpose(vect)
    points_r = np.dot(points, np.linalg.inv(tvect))

    co_min = np.min(points_r, axis=0)
    co_max = np.max(points_r, axis=0)

    xmin, xmax = co_min[0], co_max[0]
    ymin, ymax = co_min[1], co_max[1]
    zmin, zmax = co_min[2], co_max[2]

    xdif = (xmax - xmin) * 0.5
    ydif = (ymax - ymin) * 0.5
    zdif = (zmax - zmin) * 0.5

    cx = xmin + xdif
    cy = ymin + ydif
    cz = zmin + zdif

    corners = np.array([
        [cx - xdif, cy - ydif, cz - zdif],
        [cx - xdif, cy + ydif, cz - zdif],
        [cx - xdif, cy + ydif, cz + zdif],
        [cx - xdif, cy - ydif, cz + zdif],
        [cx + xdif, cy + ydif, cz + zdif],
        [cx + xdif, cy + ydif, cz - zdif],
        [cx + xdif, cy - ydif, cz + zdif],
        [cx + xdif, cy - ydif, cz - zdif],
    ])

    corners = np.dot(corners, tvect)
    center = np.dot([cx, cy, cz], tvect)

    corners = [mathutils.Vector((el[0], el[1], el[2])) for el in corners]

    print("local space:")
    for el in corners: print(el)

    print("")
    print("world space:")
    mat = oj.matrix_world
    for el in corners: print(mat @ el)


