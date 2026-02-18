# Stellated Icosahedron-Dodecahedron Compound Generator
# Paste this entire script into Blender's Python Console or Text Editor > Run Script
# Creates a compound of great icosahedron + great stellated dodecahedron
# All coordinates derived from golden ratio phi

import bpy
import bmesh
import math
from mathutils import Vector

# ============================================================
# GOLDEN RATIO CONSTANTS
# ============================================================
PHI = (1 + math.sqrt(5)) / 2        # 1.618033988749895
PHI_INV = 1 / PHI                     # 0.618033988749895
SCALE = 2.0                           # Overall scale factor

# ============================================================
# VERTEX COORDINATES
# ============================================================

def icosahedron_vertices():
    """12 vertices of icosahedron (even permutations of (0, +/-1, +/-phi))"""
    verts = []
    # (0, +/-1, +/-phi)
    for s1 in [1, -1]:
        for s2 in [1, -1]:
            verts.append(Vector((0, s1 * 1, s2 * PHI)))
    # (phi, 0, +/-1) — cyclic permutation
    for s1 in [1, -1]:
        for s2 in [1, -1]:
            verts.append(Vector((s1 * PHI, 0, s2 * 1)))
    # (+/-1, +/-phi, 0) — cyclic permutation
    for s1 in [1, -1]:
        for s2 in [1, -1]:
            verts.append(Vector((s1 * 1, s2 * PHI, 0)))
    return verts

def dodecahedron_vertices():
    """20 vertices of dodecahedron (cube + golden rectangles)"""
    verts = []
    # 8 cubic vertices: (+/-1, +/-1, +/-1)
    for x in [1, -1]:
        for y in [1, -1]:
            for z in [1, -1]:
                verts.append(Vector((x, y, z)))
    # 12 vertices from golden rectangles:
    # (0, +/-phi_inv, +/-phi)
    for s1 in [1, -1]:
        for s2 in [1, -1]:
            verts.append(Vector((0, s1 * PHI_INV, s2 * PHI)))
    # (+/-phi, 0, +/-phi_inv)
    for s1 in [1, -1]:
        for s2 in [1, -1]:
            verts.append(Vector((s1 * PHI, 0, s2 * PHI_INV)))
    # (+/-phi_inv, +/-phi, 0)
    for s1 in [1, -1]:
        for s2 in [1, -1]:
            verts.append(Vector((s1 * PHI_INV, s2 * PHI, 0)))
    return verts

# ============================================================
# FACE CONNECTIVITY
# ============================================================

def icosahedron_faces(verts):
    """20 triangular faces of the icosahedron.
    Finds faces by checking that all 3 edges have the correct length."""
    edge_len = 2.0  # edge length for unit icosahedron
    tol = 0.01
    faces = []
    n = len(verts)
    for i in range(n):
        for j in range(i+1, n):
            if abs((verts[i] - verts[j]).length - edge_len) > tol:
                continue
            for k in range(j+1, n):
                if (abs((verts[i] - verts[k]).length - edge_len) < tol and
                    abs((verts[j] - verts[k]).length - edge_len) < tol):
                    faces.append((i, j, k))
    return faces

def dodecahedron_faces(verts):
    """12 pentagonal faces of the dodecahedron.
    Finds faces by checking edge length and planarity."""
    edge_len = 2 * PHI_INV  # edge length for this coordinate set
    tol = 0.01
    n = len(verts)
    
    # Build adjacency: edges of correct length
    adj = {i: set() for i in range(n)}
    for i in range(n):
        for j in range(i+1, n):
            if abs((verts[i] - verts[j]).length - edge_len) < tol:
                adj[i].add(j)
                adj[j].add(i)
    
    # Find 5-cycles (pentagons)
    faces = []
    visited_sets = set()
    
    for start in range(n):
        for second in adj[start]:
            if second <= start:
                continue
            for third in adj[second]:
                if third == start:
                    continue
                for fourth in adj[third]:
                    if fourth == start or fourth == second:
                        continue
                    for fifth in adj[fourth]:
                        if fifth == start and fifth != second and fifth != third:
                            if start in adj[fifth]:
                                face = tuple(sorted([start, second, third, fourth, fifth]))
                                if face not in visited_sets:
                                    # Check coplanarity
                                    pts = [verts[start], verts[second], verts[third], verts[fourth], verts[fifth]]
                                    normal = (pts[1] - pts[0]).cross(pts[2] - pts[0]).normalized()
                                    coplanar = all(abs(normal.dot(pts[i] - pts[0])) < tol for i in range(3, 5))
                                    if coplanar:
                                        visited_sets.add(face)
                                        # Order vertices around the face
                                        ordered = [start, second, third, fourth]
                                        # fifth connects back to start
                                        faces.append((start, second, third, fourth, fifth))
    return faces

# ============================================================
# MESH CREATION
# ============================================================

def create_mesh(name, verts, faces, color):
    """Create a Blender mesh object with material."""
    mesh = bpy.data.meshes.new(name + '_mesh')
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    
    # Scale vertices
    scaled_verts = [v * SCALE for v in verts]
    
    # Create mesh from data
    mesh.from_pydata([list(v) for v in scaled_verts], [], list(faces))
    mesh.update()
    
    # Material
    mat = bpy.data.materials.new(name + '_mat')
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        bsdf.inputs['Base Color'].default_value = color
        bsdf.inputs['Alpha'].default_value = 0.85
    mat.blend_method = 'BLEND' if hasattr(mat, 'blend_method') else None
    obj.data.materials.append(mat)
    
    return obj

# ============================================================
# STELLATED FORMS (spike extrusion)
# ============================================================

def stellate_mesh(obj, stellation_factor=1.5):
    """Stellate a mesh by pushing each face center outward.
    Creates spike/star points from each face."""
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.faces.ensure_lookup_table()
    
    # For each face, poke it (create center vertex) then move center outward
    result = bmesh.ops.poke(bm, faces=bm.faces[:])
    
    # Move the new center vertices outward along face normal
    for v in result['verts']:
        direction = v.co.normalized()
        v.co = v.co + direction * stellation_factor * SCALE
    
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    
    obj.select_set(False)
    return obj

# ============================================================
# MAIN: BUILD THE COMPOUND
# ============================================================

def build_compound():
    # Clear existing objects
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    
    print('Building stellated icosahedron-dodecahedron compound...')
    print(f'Golden ratio phi = {PHI:.15f}')
    print(f'Scale = {SCALE}')
    
    # --- Icosahedron ---
    ico_verts = icosahedron_vertices()
    ico_faces = icosahedron_faces(ico_verts)
    print(f'Icosahedron: {len(ico_verts)} vertices, {len(ico_faces)} faces')
    
    ico_obj = create_mesh(
        'Stellated_Icosahedron',
        ico_verts,
        ico_faces,
        (0.2, 0.6, 1.0, 1.0)  # Blue
    )
    
    # Stellate it — push spikes outward
    stellate_mesh(ico_obj, stellation_factor=PHI * 0.5)
    
    # --- Dodecahedron ---
    dodec_verts = dodecahedron_vertices()
    dodec_faces = dodecahedron_faces(dodec_verts)
    print(f'Dodecahedron: {len(dodec_verts)} vertices, {len(dodec_faces)} faces')
    
    dodec_obj = create_mesh(
        'Stellated_Dodecahedron',
        dodec_verts,
        dodec_faces,
        (1.0, 0.3, 0.1, 1.0)  # Orange-red
    )
    
    # Stellate it
    stellate_mesh(dodec_obj, stellation_factor=PHI * 0.618)
    
    # --- Camera and lighting ---
    bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
    
    # Frame all objects
    bpy.ops.object.select_all(action='SELECT')
    
    print('\n=== COMPOUND COMPLETE ===')
    print(f'Stellated Icosahedron (blue): {len(ico_faces)} spiked faces')
    print(f'Stellated Dodecahedron (orange): {len(dodec_faces)} spiked faces')
    print(f'All vertex coordinates derived from phi = {PHI:.6f}')
    print('Rotate view: middle mouse button')
    print('Zoom: scroll wheel')

build_compound()
