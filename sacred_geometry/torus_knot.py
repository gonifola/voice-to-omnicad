# Torus Knot — Voice to OmniCAD
# Parametric (p,q) torus knot, default 3-2 trefoil

import bpy
import math


def create_torus_knot(p=3, q=2, R=1.0, r_tube=0.3, resolution=256,
                       scale=1.0, location=(0,0,0)):
    """Parametric (p,q) torus knot as a POLY curve.
    Default: p=3, q=2 = trefoil knot.
    Try p=5,q=2 (cinquefoil) or p=7,q=3 for more complex knots.
    """
    curve_data = bpy.data.curves.new(f"TorusKnot_{p}_{q}", type="CURVE")
    curve_data.dimensions   = "3D"
    curve_data.resolution_u = 12
    curve_data.bevel_depth  = r_tube * scale * 0.3
    curve_data.bevel_resolution = 8
    curve_data.use_fill_caps = True

    spline = curve_data.splines.new("POLY")
    spline.points.add(resolution)   # resolution+1 total

    for i in range(resolution + 1):
        t  = 2 * math.pi * i / resolution
        # Standard torus knot parametric equations
        x = scale * (R + r_tube * math.cos(q * t)) * math.cos(p * t)
        y = scale * (R + r_tube * math.cos(q * t)) * math.sin(p * t)
        z = scale * r_tube * math.sin(q * t)
        spline.points[i].co = (x, y, z, 1.0)

    # Close the curve
    spline.use_cyclic_u = True

    obj = bpy.data.objects.new(f"TorusKnot_{p}_{q}", curve_data)
    obj.location = location
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj

    # Iridescent material
    mat = bpy.data.materials.new(f"TorusKnot_Mat")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value    = (0.2, 0.5, 1.0, 1.0)
    bsdf.inputs["Metallic"].default_value      = 1.0
    bsdf.inputs["Roughness"].default_value     = 0.05
    bsdf.inputs["Anisotropic"].default_value   = 0.8
    out = nodes.new("ShaderNodeOutputMaterial")
    mat.node_tree.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    obj.data.materials.append(mat)

    print(f"[OmniCAD] Torus Knot ({p},{q}) created")
    return obj
