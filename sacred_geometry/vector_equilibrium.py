# Vector Equilibrium (Cuboctahedron) — Voice to OmniCAD v0.4.0
# Buckminster Fuller named it; Haramein calls it the zero-point
# vacuum structure — the geometry where all forces balance.
# 12 vertices equidistant from centre AND from each neighbour.
# First-mover: no existing Blender addon ships this as a named
# sacred / Haramein geometry with radial-line scaffolding.

import bpy
import bmesh
import math
from mathutils import Vector


# Cuboctahedron vertices: 12 permutations of (0, ±1, ±1)
_CUBOCTA_VERTS_UNIT = [
    Vector(( 0,  1,  1)), Vector(( 0,  1, -1)),
    Vector(( 0, -1,  1)), Vector(( 0, -1, -1)),
    Vector(( 1,  0,  1)), Vector(( 1,  0, -1)),
    Vector((-1,  0,  1)), Vector((-1,  0, -1)),
    Vector(( 1,  1,  0)), Vector(( 1, -1,  0)),
    Vector((-1,  1,  0)), Vector((-1, -1,  0)),
]

# 8 triangular faces + 6 square faces (cuboctahedron topology)
_TRI_FACES = [
    (0, 4, 8), (0, 6, 10), (3, 5, 9), (3, 7, 11),
    (1, 5, 8), (1, 7, 10), (2, 4, 9), (2, 6, 11),
]
_QUAD_FACES = [
    (0, 8, 1, 10), (0, 4, 2, 6), (8, 5, 9, 4),
    (10, 7, 11, 6), (1, 5, 3, 7), (2, 9, 3, 11),
]


def create_vector_equilibrium(
    name="Vector Equilibrium",
    radius=1.0,
    add_radial_lines=True,
    collection_name="Haramein Suite",
):
    """
    Vector Equilibrium / Cuboctahedron (Haramein / Fuller).

    radius         : circumradius of the cuboctahedron
    add_radial_lines : add 12 spokes from centre to each vertex
                       (visualises the equal-length radii property)
    """
    scale = radius / math.sqrt(2)  # unit verts have length sqrt(2)
    verts = [v * scale for v in _CUBOCTA_VERTS_UNIT]

    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bm_verts = [bm.verts.new(v) for v in verts]
    for f in _TRI_FACES + _QUAD_FACES:
        try:
            bm.faces.new([bm_verts[i] for i in f])
        except ValueError:
            pass
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()

    obj = bpy.data.objects.new(name, mesh)
    col = bpy.data.collections.get(collection_name)
    if col is None:
        col = bpy.data.collections.new(collection_name)
        bpy.context.scene.collection.children.link(col)
    col.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    if add_radial_lines:
        _add_radial_lines(verts, collection_name)

    return obj


def _add_radial_lines(verts, collection_name):
    """Add 12 spoke edges from origin to each vertex as a separate mesh."""
    mesh = bpy.data.meshes.new("VE_Radii")
    bm = bmesh.new()
    origin = bm.verts.new(Vector((0, 0, 0)))
    for v in verts:
        tip = bm.verts.new(v)
        bm.edges.new((origin, tip))
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    spoke_obj = bpy.data.objects.new("VE_Radii", mesh)
    col = bpy.data.collections.get(collection_name)
    if col:
        col.objects.link(spoke_obj)
