# Flower of Life — Voice to OmniCAD
# 7-circle hexagonal seed pattern (proper parametric implementation)

import bpy
import bmesh
import math
from mathutils import Vector


def _add_circle_mesh(name, cx, cy, radius, segments=64, z=0.0):
    """Create a single circle as a mesh object at world (cx, cy, z)."""
    bm = bmesh.new()
    verts = []
    for i in range(segments):
        angle = 2 * math.pi * i / segments
        verts.append(bm.verts.new(Vector((cx + radius * math.cos(angle),
                                          cy + radius * math.sin(angle),
                                          z))))
    # Close the loop with an edge from last → first
    for i in range(segments):
        bm.edges.new((verts[i], verts[(i + 1) % segments]))

    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def create_flower_of_life(radius=1.0, location=(0.0, 0.0, 0.0), rings=1):
    """
    Create Flower of Life pattern.

    Args:
        radius:   Circle radius.
        location: World-space centre of the pattern.
        rings:    1 = classic 7-circle seed; 2 = 19-circle first ring extension.

    Returns:
        List of created objects.
    """
    bpy.ops.object.select_all(action='DESELECT')
    ox, oy, oz = location
    objects = []

    # Centre circle
    objects.append(_add_circle_mesh("FoL_centre", ox, oy, radius, z=oz))

    # Ring 1 — 6 circles at distance = radius from centre
    for i in range(6):
        angle = math.pi / 3 * i
        cx = ox + radius * math.cos(angle)
        cy = oy + radius * math.sin(angle)
        objects.append(_add_circle_mesh(f"FoL_r1_{i}", cx, cy, radius, z=oz))

    # Ring 2 (optional — 12 more circles)
    if rings >= 2:
        for i in range(6):
            # Outer radial circles
            angle = math.pi / 3 * i
            cx = ox + 2 * radius * math.cos(angle)
            cy = oy + 2 * radius * math.sin(angle)
            objects.append(_add_circle_mesh(f"FoL_r2a_{i}", cx, cy, radius, z=oz))
            # Inter-radial circles
            angle2 = math.pi / 3 * i + math.pi / 6
            r2 = radius * math.sqrt(3)
            cx2 = ox + r2 * math.cos(angle2)
            cy2 = oy + r2 * math.sin(angle2)
            objects.append(_add_circle_mesh(f"FoL_r2b_{i}", cx2, cy2, radius, z=oz))

    # Parent all under empty
    bpy.ops.object.empty_add(location=location)
    parent = bpy.context.active_object
    parent.name = "FlowerOfLife"
    for o in objects:
        o.parent = parent

    return objects
