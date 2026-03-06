# 64-Tetrahedron Grid — Voice to OmniCAD v0.4.0
# Nassim Haramein's central unified-field geometry.
# 8 star tetrahedra (each = 2 interlocked tetrahedra) placed at
# the 8 vertices of a cube → 64 individual tetrahedra total.
# First-mover: no existing Blender addon ships this geometry.

import bpy
import bmesh
from mathutils import Vector


def _tetrahedron_verts(centre, size, flip=False):
    """Return 4 verts of a regular tetrahedron centred at *centre*."""
    s = size
    raw = [
        Vector(( 1,  1,  1)) * s,
        Vector(( 1, -1, -1)) * s,
        Vector((-1,  1, -1)) * s,
        Vector((-1, -1,  1)) * s,
    ]
    if flip:
        raw = [Vector((-v.x, -v.y, -v.z)) for v in raw]
    return [centre + v for v in raw]


def _add_tetrahedron(bm, verts):
    bm_verts = [bm.verts.new(v) for v in verts]
    for face_ids in [(0,1,2),(0,1,3),(0,2,3),(1,2,3)]:
        try:
            bm.faces.new([bm_verts[i] for i in face_ids])
        except ValueError:
            pass


def create_sixty_four_tetrahedron_grid(
    name="64-Tetrahedron Grid",
    grid_size=1.0,
    tet_size=0.45,
    collection_name="Haramein Suite",
):
    """
    64-Tetrahedron Grid (Haramein).

    8 star tetrahedra at the corners of a cube of half-edge grid_size.
    Each star tet = 2 interlocked tetrahedra (up + down) = 8 total tets
    per node x 8 nodes = 64 tetrahedra — Haramein's vacuum structure.
    """
    g = grid_size
    centres = [
        Vector(( g,  g,  g)), Vector(( g,  g, -g)),
        Vector(( g, -g,  g)), Vector(( g, -g, -g)),
        Vector((-g,  g,  g)), Vector((-g,  g, -g)),
        Vector((-g, -g,  g)), Vector((-g, -g, -g)),
    ]

    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    for c in centres:
        _add_tetrahedron(bm, _tetrahedron_verts(c, tet_size, flip=False))
        _add_tetrahedron(bm, _tetrahedron_verts(c, tet_size, flip=True))
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
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
    return obj
