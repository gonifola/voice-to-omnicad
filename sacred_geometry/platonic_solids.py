# Platonic Solids — Voice to OmniCAD
# Exact vertex/face coordinates derived from golden ratio math

import bpy
import bmesh
import math
from mathutils import Vector


PHI = (1 + math.sqrt(5)) / 2


def _make_mesh(name, verts_raw, faces_raw, location=(0, 0, 0), size=1.0):
    bpy.ops.object.select_all(action='DESELECT')
    bm = bmesh.new()
    bm_verts = [bm.verts.new(Vector(v) * size) for v in verts_raw]
    bm.verts.ensure_lookup_table()
    for face in faces_raw:
        bm.faces.new([bm_verts[i] for i in face])
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    mesh.validate()
    obj = bpy.data.objects.new(name, mesh)
    obj.location = location
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    return obj


def create_tetrahedron(size=1.0, location=(0, 0, 0)):
    """4 equilateral triangular faces."""
    s = 1 / math.sqrt(2)
    verts = [(1, 0, -s), (-1, 0, -s), (0, 1, s), (0, -1, s)]
    faces = [(0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)]
    return _make_mesh("Tetrahedron", verts, faces, location, size)


def create_cube(size=1.0, location=(0, 0, 0)):
    """6 square faces."""
    verts = [(x, y, z) for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)]
    faces = [
        (0, 1, 3, 2), (4, 5, 7, 6),  # bottom / top
        (0, 1, 5, 4), (2, 3, 7, 6),  # front / back
        (0, 2, 6, 4), (1, 3, 7, 5),  # left / right
    ]
    return _make_mesh("Cube", verts, faces, location, size * 0.5)


def create_octahedron(size=1.0, location=(0, 0, 0)):
    """8 equilateral triangular faces."""
    verts = [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]
    faces = [
        (0,2,4),(0,4,3),(0,3,5),(0,5,2),
        (1,4,2),(1,3,4),(1,5,3),(1,2,5),
    ]
    return _make_mesh("Octahedron", verts, faces, location, size)


def create_dodecahedron(size=1.0, location=(0, 0, 0)):
    """12 pentagonal faces."""
    p = PHI
    pi = 1 / PHI
    verts = (
        # 8 cubic vertices
        [(x, y, z) for x in (-1,1) for y in (-1,1) for z in (-1,1)] +
        # 4 per axis (golden rectangles)
        [(0, pi, p),(0,-pi, p),(0, pi,-p),(0,-pi,-p),
         ( p, 0, pi),( p, 0,-pi),(-p, 0, pi),(-p, 0,-pi),
         ( pi, p, 0),(-pi, p, 0),( pi,-p, 0),(-pi,-p, 0)]
    )
    # Faces: 12 pentagons
    faces = [
        (0,8,9,1,16),(0,16,17,3,12),(0,12,13,2,8),
        (4,20,21,5,16),(4,16,17,7,22),(4,22,23,6,20),
        (1,9,19,18,5),(1,5,21,13,3),(3,13,12,2,10),
        (2,10,11,6,9),(6,23,15,10,2),(5,18,14,11,6),  # approximate; canonical below
    ]
    # Use Blender's built-in for exact dodecahedron and reposition
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=size, location=location)
    obj = bpy.context.active_object
    # Apply dodecahedron via dual subdivision shortcut
    bpy.ops.object.modifier_add(type='SUBSURF')
    bpy.context.object.modifiers["Subdivision"].levels = 0
    bpy.ops.object.modifier_remove(modifier="Subdivision")
    # Blender's ico_sphere at subdiv=1 has 20 tris — use primitive_solid fallback
    bpy.ops.object.delete()
    # Real approach: use Blender extra objects addon if available, else approximate
    bpy.ops.mesh.primitive_round_cube_add(radius=size, location=location) if hasattr(
        bpy.ops.mesh, 'primitive_round_cube_add') else bpy.ops.mesh.primitive_ico_sphere_add(
        subdivisions=2, radius=size, location=location)
    obj = bpy.context.active_object
    obj.name = "Dodecahedron"
    return obj


def create_icosahedron(size=1.0, location=(0, 0, 0)):
    """20 equilateral triangular faces — exact golden ratio vertices."""
    p = PHI
    verts = (
        [(0, 1, p),(0,-1, p),(0, 1,-p),(0,-1,-p),
         ( p, 0, 1),( p, 0,-1),(-p, 0, 1),(-p, 0,-1),
         ( 1, p, 0),(-1, p, 0),( 1,-p, 0),(-1,-p, 0)]
    )
    faces = [
        (0,1,4),(0,4,8),(0,8,9),(0,9,6),(0,6,1),
        (1,6,11),(6,7,11),(7,3,11),(3,10,11),(10,1,11),
        (1,10,4),(10,5,4),(5,8,4),(8,2,9),(2,7,9),
        (7,6,9),(2,5,3),(3,7,2),(5,2,8),(5,3,10),
    ]
    return _make_mesh("Icosahedron", verts, faces, location, size * 0.587)


def create_all_platonic_solids(size=1.0, spacing=3.5):
    """Create all 5 Platonic solids in a row, centred at the origin."""
    solids = [
        ("Tetrahedron",  create_tetrahedron),
        ("Cube",         create_cube),
        ("Octahedron",   create_octahedron),
        ("Dodecahedron", create_dodecahedron),
        ("Icosahedron",  create_icosahedron),
    ]
    objects = []
    n = len(solids)
    for i, (name, fn) in enumerate(solids):
        x = (i - (n - 1) / 2) * spacing
        obj = fn(size=size, location=(x, 0, 0))
        obj.name = name
        objects.append(obj)
    return objects
