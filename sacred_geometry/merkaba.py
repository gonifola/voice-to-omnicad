# Merkaba — Voice to OmniCAD
# Two counter-rotating tetrahedra (Star Tetrahedron), φ-exact

import bpy
import math
import bmesh


PHI = (1 + math.sqrt(5)) / 2


def _tetrahedron_verts(r, invert=False):
    """Return 4 vertices of a tetrahedron inscribed in sphere of radius r."""
    sign = -1 if invert else 1
    # Three base verts + apex
    base_r = r * math.sqrt(2/3)
    h      = r / math.sqrt(3)
    verts  = []
    for i in range(3):
        a = 2 * math.pi * i / 3 + (math.pi / 6)
        verts.append((base_r * math.cos(a), base_r * math.sin(a), -sign * h))
    verts.append((0, 0, sign * r * math.sqrt(2/3) * math.sqrt(2)))
    return verts


def create_merkaba(scale=1.0, location=(0, 0, 0)):
    """Star Tetrahedron (Merkaba) — two interlocked tetrahedra."""
    bm = bmesh.new()

    def add_tet(verts_list, mat_idx):
        verts = [bm.verts.new(v) for v in verts_list]
        faces_idx = [(0,1,2), (0,1,3), (0,2,3), (1,2,3)]
        for fi in faces_idx:
            try:
                f = bm.faces.new([verts[i] for i in fi])
                f.material_index = mat_idx
            except Exception:
                pass

    v_up   = _tetrahedron_verts(scale, invert=False)
    v_down = _tetrahedron_verts(scale, invert=True)

    add_tet(v_up,   0)
    add_tet(v_down, 1)

    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()

    mesh = bpy.data.meshes.new("Merkaba")
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new("Merkaba", mesh)
    obj.location = location
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj

    # Two materials — cyan up / magenta down
    for name, color in [("Merkaba_Up", (0.0, 0.8, 1.0, 0.7)), ("Merkaba_Down", (1.0, 0.0, 0.8, 0.7))]:
        mat = bpy.data.materials.new(name)
        mat.use_nodes = True
        mat.blend_method = "BLEND"
        nodes = mat.node_tree.nodes
        nodes.clear()
        bsdf = nodes.new("ShaderNodeBsdfPrincipled")
        bsdf.inputs["Base Color"].default_value  = color
        bsdf.inputs["Alpha"].default_value       = 0.7
        bsdf.inputs["Roughness"].default_value   = 0.1
        bsdf.inputs["Metallic"].default_value    = 0.8
        out = nodes.new("ShaderNodeOutputMaterial")
        mat.node_tree.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
        obj.data.materials.append(mat)

    print("[OmniCAD] Merkaba created")
    return obj
