import bpy
import bmesh
import numpy as np
import mathutils
from math import atan, pi, sqrt


def check_intersection(vertices: list, obj: bpy.types.Object) -> list[mathutils.Vector]:
    """
    https://blender.stackexchange.com/questions/31693/how-to-find-if-a-point-is-inside-a-mesh
    filter points such that only the one inside the mesh are returned
    :param vertices: list of vertices
    :param obj: blender object
    :return: list of vertices that are inside the mesh
    """
    me = obj.data   # make object to mesh
    bm = bmesh.new()
    bm.from_mesh(me)

    points_inside: list[mathutils.Vector] = []

    bvh = mathutils.bvhtree.BVHTree.FromBMesh(bm, epsilon=0.0)
    for vertex in vertices:
        v = mathutils.Vector((vertex[0], vertex[1], vertex[2]))  # maybe pass the list as vectors already???
        location, normal, index, distance = bvh.find_nearest(v)
        p2 = location - v
        res = p2.dot(normal)
        if not res < 0.0:
            points_inside.append(v)

    bm.free()

    return points_inside


def make_voronoi_structure(name: str, vertices: np.array, segments: list[tuple], radius: float):
    # TODO: optimize this by making it multi-threaded???
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    bm = bmesh.new()

    for v in vertices:
        make_sphere(bm=bm, position=v, radius=radius)

    print("finished making spheres")

    counter = 0
    for s in segments:
        print(f"made {counter}/{len(segments)} segment")
        vertex1 = vertices[s[0]]
        vertex2 = vertices[s[1]]
        v1 = mathutils.Vector((vertex1[0], vertex1[1], vertex1[2]))
        v2 = mathutils.Vector((vertex2[0], vertex2[1], vertex2[2]))
        make_cylinder(bm=bm, v1=v1, v2=v2, radius=radius)
        counter += 1
    print("finished making segment")
    bm.to_mesh(mesh)
    bm.free()


def make_sphere(bm: bmesh.types.BMesh, position: list or np.array or tuple = (0, 0, 0), radius: float = 1):
    """
    generate a sphere at coordinate specified by position
    :param bm: bmesh instance
    :param position: list or array of coordinates x, y, z
    :param radius: radius of the sphere
    """
    vertices = bmesh.ops.create_uvsphere(bm, u_segments=8, v_segments=7, radius=radius)
    bmesh.ops.translate(bm, vec=position, verts=vertices["verts"])


def make_cylinder(bm: bmesh.types.BMesh, v1: mathutils.Vector, v2: mathutils.Vector, radius: float = 1):
    """
    generate a cylinder with one center end on v1 and the other on v2
    :param bm: bmesh instance
    :param v1: center of one side of the cylinder
    :param v2: center of the other side of the cylinder
    :param radius: radius of cylinder
    """
    diff = v1 - v2
    x = diff.x
    y = diff.y
    z = diff.z
    size = diff.length

    mag = sqrt(x ** 2 + y ** 2)

    if x == 0:
        beta = 0
    else:
        beta = atan(y / x)
    if (x <= 0 <= y) or (x <= 0 and y <= 0):
        beta = pi + beta
    if mag == 0:
        theta = pi / 2
    else:
        theta = atan(z / mag)

    eul = mathutils.Euler((0.0, -theta + pi / 2, beta), 'XYZ')  # rotation euler matrix
    rotation_mat = eul.to_matrix()
    rotation_mat.resize_4x4()

    new_pos = v1 + (v2 - v1) / 2  # position where to translate the new geometry center

    vertices = bmesh.ops.create_cone(bm,
                                     cap_ends=False,  # should there be caps????
                                     segments=8,  # resolution
                                     radius1=radius,
                                     radius2=radius,
                                     depth=size,
                                     matrix=mathutils.Matrix.Identity(4))
    bmesh.ops.translate(bm, vec=new_pos, verts=vertices['verts'])  # translate geometry
    bmesh.ops.rotate(bm,
                     cent=new_pos,
                     matrix=rotation_mat,
                     verts=vertices["verts"])  # align geometry with line passing through v1 and v2


def join_all_objects(selected_objects: list[bpy.types.Object], new_name: str):
    """
    join multiple objects together
    :param selected_objects: list of python objects
    :param new_name: name of new object
    """
    new_mesh = bpy.data.meshes.new(new_name)
    new_object = bpy.data.objects.new(new_name, new_mesh)

    bm = bmesh.new()
    for obj in selected_objects:
        if obj.type == 'MESH':
            mesh = obj.data
            matrix = obj.matrix_world

            mesh_copy = mesh.copy()
            mesh_copy.transform(matrix)

            bm.from_mesh(mesh_copy)

    bm.to_mesh(new_mesh)
    # bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.1)  # TODO this might be useful,
    #  but need to adjust the distance dynamically as to not merge beams
    bm.free()

    bpy.context.scene.collection.objects.link(new_object)

    # Delete the original selected objects
    for obj in selected_objects:
        bpy.data.objects.remove(obj, do_unlink=True)


# TODO test and finish this
def boolean_operation(name_a, name_b, new_one_name):
    # Create a boolean modifier named 'my_bool_mod' for the cube.
    mod_bool = bpy.data.objects[name_a].modifiers.new('my_bool_mod', 'BOOLEAN')
    # Set the mode of the modifier to DIFFERENCE.
    mod_bool.operation = 'UNION'  # 'DIFFERENCE'
    # Set the object to be used by the modifier.
    mod_bool.object = bpy.data.objects[name_b]
    bpy.context.view_layer.objects.active = bpy.data.objects[name_a]
    # Apply the modifier.
    res = bpy.ops.object.modifier_apply(apply_as='DATA', modifier='my_bool_mod')

    bpy.data.objects[name_b].select_set(True)  # 2.8+
    bpy.ops.object.delete()
    bpy.data.objects[name_a].name = new_one_name
    return res


def merge_doubles(object_name: str):
    bm = bmesh.new()
    # TODO need to finish this if is going to be useful
    bmesh.ops.remove_doubles(bm, verts=[], dist=0)

    bm.free()
