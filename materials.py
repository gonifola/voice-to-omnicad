# Material Presets — Voice to OmniCAD
# Gold, Crystal, Obsidian + utility apply function

import bpy


def apply_gold(obj):
    """Polished gold PBR material."""
    mat = _get_or_create("OmniCAD_Gold")
    nodes = mat.node_tree.nodes
    bsdf = _get_bsdf(nodes)
    bsdf.inputs["Base Color"].default_value  = (1.0, 0.766, 0.336, 1.0)
    bsdf.inputs["Metallic"].default_value    = 1.0
    bsdf.inputs["Roughness"].default_value   = 0.1
    _assign(obj, mat)
    print(f"[OmniCAD] Gold applied to {obj.name}")


def apply_crystal(obj):
    """Crystal / glass transmission material."""
    mat = _get_or_create("OmniCAD_Crystal")
    mat.blend_method = "BLEND"
    nodes = mat.node_tree.nodes
    bsdf = _get_bsdf(nodes)
    bsdf.inputs["Base Color"].default_value        = (0.85, 0.95, 1.0, 1.0)
    bsdf.inputs["Metallic"].default_value          = 0.0
    bsdf.inputs["Roughness"].default_value         = 0.0
    bsdf.inputs["IOR"].default_value               = 1.45
    bsdf.inputs["Alpha"].default_value             = 0.15
    try:
        bsdf.inputs["Transmission Weight"].default_value = 1.0
    except KeyError:
        pass
    _assign(obj, mat)
    print(f"[OmniCAD] Crystal applied to {obj.name}")


def apply_obsidian(obj):
    """Dark volcanic glass — deep black with slight gloss."""
    mat = _get_or_create("OmniCAD_Obsidian")
    nodes = mat.node_tree.nodes
    bsdf = _get_bsdf(nodes)
    bsdf.inputs["Base Color"].default_value  = (0.02, 0.02, 0.03, 1.0)
    bsdf.inputs["Metallic"].default_value    = 0.0
    bsdf.inputs["Roughness"].default_value   = 0.05
    bsdf.inputs["Specular IOR Level"].default_value = 0.9
    _assign(obj, mat)
    print(f"[OmniCAD] Obsidian applied to {obj.name}")


def apply_preset(obj, preset_name):
    """Apply preset by name string. preset_name: 'gold' | 'crystal' | 'obsidian'"""
    name = preset_name.lower().strip()
    if name == "gold":
        apply_gold(obj)
    elif name in ("crystal", "glass"):
        apply_crystal(obj)
    elif name in ("obsidian", "dark", "black"):
        apply_obsidian(obj)
    else:
        print(f"[OmniCAD] Unknown preset '{preset_name}'. Try: gold, crystal, obsidian")


# ── Helpers ─────────────────────────────────────────────────

def _get_or_create(name):
    if name in bpy.data.materials:
        mat = bpy.data.materials[name]
    else:
        mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    return mat


def _get_bsdf(nodes):
    for n in nodes:
        if n.type == "BSDF_PRINCIPLED":
            return n
    nodes.clear()
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    out  = nodes.new("ShaderNodeOutputMaterial")
    nodes.id_data.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return bsdf


def _assign(obj, mat):
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)
