# Fibonacci Spiral — Voice to OmniCAD
# Golden ratio spiral + squares, parametric

import bpy
import math
import bmesh


PHI = (1 + math.sqrt(5)) / 2


def create_fibonacci_spiral(turns=6, resolution=200, scale=1.0, location=(0,0,0)):
    """Logarithmic golden-ratio spiral as a 3D curve object."""

    # Create Bezier/Poly curve
    curve_data = bpy.data.curves.new("FibonacciSpiral", type="CURVE")
    curve_data.dimensions   = "3D"
    curve_data.resolution_u = 12

    spline = curve_data.splines.new("POLY")

    points = []
    steps  = resolution
    for i in range(steps + 1):
        t   = turns * 2 * math.pi * i / steps
        r   = scale * math.pow(PHI, t / (math.pi / 2))   # r = φ^(θ/(π/2))
        x   = r * math.cos(t)
        y   = r * math.sin(t)
        z   = 0.0
        points.append((x, y, z, 1.0))   # x, y, z, weight

    spline.points.add(len(points) - 1)
    for i, pt in enumerate(points):
        spline.points[i].co = pt

    curve_data.bevel_depth    = 0.015 * scale
    curve_data.bevel_resolution = 4

    obj = bpy.data.objects.new("FibonacciSpiral", curve_data)
    obj.location = location
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj

    # Gold material
    mat = bpy.data.materials.new("FibSpiral_Gold")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = (1.0, 0.78, 0.0, 1.0)
    bsdf.inputs["Metallic"].default_value   = 0.9
    bsdf.inputs["Roughness"].default_value  = 0.1
    out  = nodes.new("ShaderNodeOutputMaterial")
    mat.node_tree.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    obj.data.materials.append(mat)

    print(f"[OmniCAD] Fibonacci Spiral created ({turns} turns)")
    return obj
