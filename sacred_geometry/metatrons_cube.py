# Metatron's Cube — Voice to OmniCAD
# 13 circles (Fruit of Life) + all connecting lines = Metatron's Cube

import bpy
import bmesh
import math
from mathutils import Vector


def _add_circle(name, cx, cy, radius, segments=64, z=0.0):
    bm = bmesh.new()
    verts = [bm.verts.new(Vector((
        cx + radius * math.cos(2 * math.pi * i / segments),
        cy + radius * math.sin(2 * math.pi * i / segments),
        z))) for i in range(segments)]
    for i in range(segments):
        bm.edges.new((verts[i], verts[(i + 1) % segments]))
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def _add_line(name, p1, p2):
    """Create a single edge between two 3-D points."""
    bm = bmesh.new()
    v1 = bm.verts.new(Vector(p1))
    v2 = bm.verts.new(Vector(p2))
    bm.edges.new((v1, v2))
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def create_metatrons_cube(radius=1.0, location=(0.0, 0.0, 0.0)):
    """
    Create Metatron's Cube.

    13 circles (Fruit of Life — 1 centre + 6 inner + 6 outer)
    + all straight lines connecting every circle centre to every other.

    Args:
        radius:   Radius of each circle.
        location: World-space origin.

    Returns:
        List of created objects.
    """
    bpy.ops.object.select_all(action='DESELECT')
    ox, oy, oz = location
    objects = []
    centres = []

    # ── 13 circle centres ────────────────────────────────────────────────────
    # Centre
    centres.append((ox, oy))

    # Inner ring — 6 circles, radius apart
    for i in range(6):
        a = math.pi / 3 * i
        centres.append((ox + radius * math.cos(a), oy + radius * math.sin(a)))

    # Outer ring — 6 circles, 2*radius from centre
    for i in range(6):
        a = math.pi / 3 * i
        centres.append((ox + 2 * radius * math.cos(a), oy + 2 * radius * math.sin(a)))

    # Draw circles
    for idx, (cx, cy) in enumerate(centres):
        objects.append(_add_circle(f"MC_circle_{idx}", cx, cy, radius, z=oz))

    # ── Connecting lines (n*(n-1)/2 = 78) ───────────────────────────────────
    for i in range(len(centres)):
        for j in range(i + 1, len(centres)):
            x1, y1 = centres[i]
            x2, y2 = centres[j]
            objects.append(_add_line(f"MC_line_{i}_{j}",
                                      (x1, y1, oz), (x2, y2, oz)))

    # Parent
    bpy.ops.object.empty_add(location=location)
    parent = bpy.context.active_object
    parent.name = "MetatronsCube"
    for o in objects:
        o.parent = parent

    return objects
