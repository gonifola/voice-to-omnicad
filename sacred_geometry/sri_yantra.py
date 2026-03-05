# Sri Yantra — Voice to OmniCAD
# 9 interlocking triangles + lotus petals, parametric

import bpy
import math


PHI = (1 + math.sqrt(5)) / 2


def _add_triangle(verts, faces, pts, z=0.0):
    base = len(verts)
    for p in pts:
        verts.append((p[0], p[1], z))
    faces.append([base, base+1, base+2])


def create_sri_yantra(scale=1.0, location=(0, 0, 0)):
    """9-triangle Sri Yantra — 4 upward + 5 downward pointing."""
    import bmesh

    bm = bmesh.new()

    R = scale  # circumradius of outer triangle

    # Build 9 triangles: alternating up/down, shrinking
    ratios_up   = [1.0, 0.65, 0.45, 0.28]   # 4 upward pointing
    ratios_down = [0.82, 0.56, 0.38, 0.22, 0.12]  # 5 downward pointing

    z = 0.0

    def tri_up(r, z_off):
        h = r * math.sqrt(3)
        return [
            (0,  2*r/math.sqrt(3), z_off),
            (-r, -r/math.sqrt(3),  z_off),
            ( r, -r/math.sqrt(3),  z_off),
        ]

    def tri_down(r, z_off):
        h = r * math.sqrt(3)
        return [
            (0,  -2*r/math.sqrt(3), z_off),
            (-r,  r/math.sqrt(3),   z_off),
            ( r,  r/math.sqrt(3),   z_off),
        ]

    all_tris = []
    for i, r in enumerate(ratios_up):
        all_tris.append(tri_up(R * r, z + i * 0.01))
    for i, r in enumerate(ratios_down):
        all_tris.append(tri_down(R * r, z + (i + 4) * 0.01))

    # Add outer circle (lotus ring) as edge loop
    segs = 16
    circle_verts = []
    for i in range(segs):
        a = 2 * math.pi * i / segs
        v = bm.verts.new((R * 1.2 * math.cos(a), R * 1.2 * math.sin(a), 0))
        circle_verts.append(v)

    # Close circle
    for i in range(segs):
        bm.edges.new([circle_verts[i], circle_verts[(i+1) % segs]])

    # Add triangles as edge loops
    for pts in all_tris:
        tri_verts = [bm.verts.new(p) for p in pts]
        for i in range(3):
            bm.edges.new([tri_verts[i], tri_verts[(i+1) % 3]])

    # Central bindu point
    bm.verts.new((0, 0, 0.001))

    bm.verts.ensure_lookup_table()

    mesh = bpy.data.meshes.new("SriYantra")
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new("SriYantra", mesh)
    obj.location = location
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj

    # Gold emission material
    mat = bpy.data.materials.new("SriYantra_Gold")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    em = nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (1.0, 0.78, 0.0, 1.0)
    em.inputs["Strength"].default_value = 2.0
    out = nodes.new("ShaderNodeOutputMaterial")
    mat.node_tree.links.new(em.outputs["Emission"], out.inputs["Surface"])
    obj.data.materials.append(mat)

    print("[OmniCAD] Sri Yantra created")
    return obj
