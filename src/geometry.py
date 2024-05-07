import bpy
import bmesh
import numpy as np
import mathutils
from math import atan, pi, sqrt


def make_sphere(name: str, position: list | np.array | tuple = (0, 0, 0), radius: float = 1):
    """
    generate a sphere at coordinate specified by position
    :param position: list or array of coordinates x, y, z
    :param name: name of the object that blender uses as unique identifier
    :param radius: radius of the sphere
    """
    mesh = bpy.data.meshes.new(name)
    basic_sphere = bpy.data.objects.new(name, mesh)

    bpy.context.collection.objects.link(basic_sphere)

    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=8, v_segments=7, radius=radius)
    bmesh.ops.translate(bm, vec=position, verts=bm.verts)
    bm.to_mesh(mesh)
    bm.free()


def make_cylinder(name: str, v1: mathutils.Vector, v2: mathutils.Vector, radius: float = 1):
    """
    generate a cylinder with one center end on v1 and the other on v2
    :param name: name of the object that blender uses as unique identifier
    :param v1: center of one side of the cylinder
    :param v2: center of the other side of the cylinder
    :param radius: radius of cylinder
    """
    mesh = bpy.data.meshes.new(name)
    basic_sphere = bpy.data.objects.new(name, mesh)

    bpy.context.collection.objects.link(basic_sphere)

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

    bm = bmesh.new()
    bmesh.ops.create_cone(bm,
                          cap_ends=False,  # should there be caps????
                          segments=8,  # resolution
                          radius1=radius,
                          radius2=radius,
                          depth=size,
                          matrix=mathutils.Matrix.Identity(4))
    bmesh.ops.translate(bm, vec=new_pos, verts=bm.verts)  # translate geometry
    bmesh.ops.rotate(bm,
                     cent=new_pos,
                     matrix=rotation_mat,
                     verts=bm.verts)  # align geometry with line passing through v1 and v2
    bm.to_mesh(mesh)
    bm.free()


def join_all_objects():

    selected_objects = bpy.context.selected_objects  # TODO select all sphere and cylinder in the scene

    new_mesh = bpy.data.meshes.new("final")
    new_object = bpy.data.objects.new("final", new_mesh)

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


