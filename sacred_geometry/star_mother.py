# =============================================================================
# STAR MOTHER — Dan Winter's Sacred Geometry Model
# All 5 Platonic solids nested with golden ratio scaling + stellation
# Paste into Blender Python Console: exec(open("<path>/star_mother.py").read())
# =============================================================================

import bpy
import bmesh
import math
from mathutils import Vector

# Golden ratio
PHI = (1 + math.sqrt(5)) / 2       # 1.618033988749895
PHI_INV = 1 / PHI                   # 0.618033988749895
SCALE = 2.0                          # Master scale

# =============================================================================
# COLORS (RGBA) — each solid gets a distinct color
# =============================================================================
COLORS = {
    'octahedron':      (1.0, 1.0, 0.2, 1.0),   # Yellow (core)
    'tetrahedron_a':   (1.0, 0.0, 0.0, 1.0),   # Red
    'tetrahedron_b':   (0.0, 0.4, 1.0, 1.0),   # Blue
    'cube':            (0.0, 1.0, 0.4, 1.0),   # Green
    'dodecahedron':    (1.0, 0.5, 0.0, 1.0),   # Orange
    'icosahedron':     (0.8, 0.0, 1.0, 1.0),   # Purple
}

# =============================================================================
# VERTEX GENERATORS — exact coordinates from golden ratio
# =============================================================================

def octahedron_verts(r=1.0):
    """6 vertices of octahedron at distance r from origin."""
    return [
        Vector((r, 0, 0)), Vector((-r, 0, 0)),
        Vector((0, r, 0)), Vector((0, -r, 0)),
        Vector((0, 0, r)), Vector((0, 0, -r)),
    ]

def octahedron_faces():
    return [
        (0, 2, 4), (0, 4, 3), (0, 3, 5), (0, 5, 2),
        (1, 4, 2), (1, 3, 4), (1, 5, 3), (1, 2, 5),
    ]

def tetrahedron_verts_a(r=1.0):
    """4 vertices of tetrahedron A inscribed in cube of half-edge r."""
    return [
        Vector((r, r, r)), Vector((r, -r, -r)),
        Vector((-r, r, -r)), Vector((-r, -r, r)),
    ]

def tetrahedron_verts_b(r=1.0):
    """4 vertices of tetrahedron B (dual/inverse of A)."""
    return [
        Vector((-r, -r, -r)), Vector((-r, r, r)),
        Vector((r, -r, r)), Vector((r, r, -r)),
    ]

def tetrahedron_faces():
    return [
        (0, 1, 2), (0, 2, 3), (0, 3, 1), (1, 3, 2),
    ]

def cube_verts(r=1.0):
    """8 vertices of cube with half-edge r."""
    verts = []
    for x in [r, -r]:
        for y in [r, -r]:
            for z in [r, -r]:
                verts.append(Vector((x, y, z)))
    return verts

def cube_faces():
    return [
        (0, 2, 3, 1), (4, 5, 7, 6),
        (0, 1, 5, 4), (2, 6, 7, 3),
        (0, 4, 6, 2), (1, 3, 7, 5),
    ]

def dodecahedron_verts(r=1.0):
    """20 vertices of dodecahedron. Cube vertices + golden rectangle vertices.
    All at scale r."""
    verts = []
    # 8 cube vertices
    for x in [1, -1]:
        for y in [1, -1]:
            for z in [1, -1]:
                verts.append(Vector((x, y, z)))
    # 4 on YZ plane: (0, +/-phi, +/-phi_inv)
    for s1 in [1, -1]:
        for s2 in [1, -1]:
            verts.append(Vector((0, s1 * PHI, s2 * PHI_INV)))
    # 4 on XZ plane: (+/-phi_inv, 0, +/-phi)
    for s1 in [1, -1]:
        for s2 in [1, -1]:
            verts.append(Vector((s1 * PHI_INV, 0, s2 * PHI)))
    # 4 on XY plane: (+/-phi, +/-phi_inv, 0)
    for s1 in [1, -1]:
        for s2 in [1, -1]:
            verts.append(Vector((s1 * PHI, s2 * PHI_INV, 0)))
    # Scale all
    return [v * r for v in verts]

def dodecahedron_faces_from_verts(verts):
    """Find 12 pentagonal faces by edge adjacency."""
    edge_len = (verts[0] - verts[8]).length  # known edge pair
    tol = edge_len * 0.05
    n = len(verts)
    adj = {i: set() for i in range(n)}
    for i in range(n):
        for j in range(i+1, n):
            if abs((verts[i] - verts[j]).length - edge_len) < tol:
                adj[i].add(j)
                adj[j].add(i)
    # Find pentagons via 5-cycles
    faces = []
    found = set()
    for a in range(n):
        for b in adj[a]:
            for c in adj[b]:
                if c == a: continue
                for d in adj[c]:
                    if d == a or d == b: continue
                    for e in adj[d]:
                        if e == b or e == c: continue
                        if a in adj[e]:
                            key = tuple(sorted([a,b,c,d,e]))
                            if key not in found:
                                # Verify coplanar
                                pts = [verts[i] for i in [a,b,c,d,e]]
                                n_vec = (pts[1]-pts[0]).cross(pts[2]-pts[0])
                                if n_vec.length > 1e-8:
                                    n_vec = n_vec.normalized()
                                    if all(abs(n_vec.dot(pts[i]-pts[0])) < tol for i in range(2,5)):
                                        found.add(key)
                                        faces.append((a,b,c,d,e))
    return faces

def icosahedron_verts(r=1.0):
    """12 vertices of icosahedron. Even permutations of (0, +/-1, +/-phi)."""
    raw = []
    for s1 in [1, -1]:
        for s2 in [1, -1]:
            raw.append(Vector((0, s1, s2 * PHI)))
            raw.append(Vector((s1 * PHI, 0, s2)))
            raw.append(Vector((s1, s2 * PHI, 0)))
    # Normalize to circumradius r
    cr = raw[0].length
    return [v * (r / cr) for v in raw]

def icosahedron_faces_from_verts(verts):
    """Find 20 triangular faces by edge length."""
    # Compute expected edge length
    dists = sorted(set(round((verts[0]-verts[j]).length, 6) for j in range(1, len(verts))))
    edge_len = dists[0]  # shortest distance = edge
    tol = edge_len * 0.05
    n = len(verts)
    faces = []
    for i in range(n):
        for j in range(i+1, n):
            if abs((verts[i]-verts[j]).length - edge_len) > tol: continue
            for k in range(j+1, n):
                if (abs((verts[i]-verts[k]).length - edge_len) < tol and
                    abs((verts[j]-verts[k]).length - edge_len) < tol):
                    faces.append((i, j, k))
    return faces

# =============================================================================
# MESH + MATERIAL HELPERS
# =============================================================================

def make_material(name, color, alpha=0.7):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        bsdf.inputs['Base Color'].default_value = color
        bsdf.inputs['Alpha'].default_value = alpha
        bsdf.inputs['Roughness'].default_value = 0.3
    mat.use_backface_culling = False
    # Transparency for EEVEE
    if hasattr(mat, 'blend_method'):
        mat.blend_method = 'BLEND'
    return mat

def create_solid(name, verts, faces, color, alpha=0.6, wireframe=False):
    """Create a mesh object from vertex/face data."""
    mesh = bpy.data.meshes.new(name + '_mesh')
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    scaled = [v * SCALE for v in verts]
    mesh.from_pydata([list(v) for v in scaled], [], list(faces))
    mesh.update()
    mat = make_material(name + '_mat', color, alpha)
    obj.data.materials.append(mat)
    if wireframe:
        mod = obj.modifiers.new('Wire', 'WIREFRAME')
        mod.thickness = 0.02 * SCALE
        mod.use_replace = False
    return obj

def stellate(obj, factor):
    """Stellate by poking faces and pushing centers outward."""
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.faces.ensure_lookup_table()
    result = bmesh.ops.poke(bm, faces=bm.faces[:])
    for v in result['verts']:
        direction = v.co.normalized()
        v.co = v.co + direction * factor * SCALE
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    obj.select_set(False)
    return obj

# =============================================================================
# NESTING SCALE FACTORS
# =============================================================================
# Star Mother nesting from Dan Winter:
# Octahedron (core) → Star Tetrahedron → Cube → Dodecahedron → Icosahedron
#
# Key relationships (circumradius-based):
# - Tetrahedron inscribed in cube: tet vertices on cube vertices
#   → same circumradius
# - Octahedron inside star tetrahedron: oct vertices at edge midpoints
#   → oct circumradius = tet edge / 2 = cube_edge * sqrt(2) / 2
# - Cube inscribed in dodecahedron: cube vertices on dodec vertices
#   → dodec circumradius = cube circumradius * phi
# - Icosahedron as dual of dodecahedron: ico vertices at dodec face centers
#   → same circumscribing sphere
#
# Using cube half-edge = 1 as the reference unit:

R_OCTA = 1.0                    # Octahedron circumradius
R_TETRA = 1.0                   # Star tetrahedron half-edge = same as cube
R_CUBE = 1.0                    # Cube half-edge
R_DODEC = 1.0                   # Dodecahedron at natural scale (cube fits inside)
R_ICO = 1.0 * PHI               # Icosahedron slightly larger (phi relationship)

# =============================================================================
# BUILD THE STAR MOTHER
# =============================================================================

def build_star_mother():
    # Clear scene
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for mesh in bpy.data.meshes:
        bpy.data.meshes.remove(mesh)
    for mat in bpy.data.materials:
        bpy.data.materials.remove(mat)

    print('='*60)
    print('  STAR MOTHER — Dan Winter Sacred Geometry')
    print(f'  Golden Ratio phi = {PHI:.15f}')
    print(f'  Scale = {SCALE}')
    print('='*60)

    # --- Layer 1: Octahedron (core) ---
    print('\n[1/5] Octahedron (core)...')
    ov = octahedron_verts(R_OCTA)
    of = octahedron_faces()
    octa = create_solid('01_Octahedron', ov, of,
                        COLORS['octahedron'], alpha=0.9)
    print(f'  {len(ov)} vertices, {len(of)} faces')

    # --- Layer 2: Star Tetrahedron (two interpenetrating tetrahedra) ---
    print('\n[2/5] Star Tetrahedron...')
    ta = tetrahedron_verts_a(R_TETRA)
    tb = tetrahedron_verts_b(R_TETRA)
    tf = tetrahedron_faces()
    tet_a = create_solid('02_Tetrahedron_A', ta, tf,
                         COLORS['tetrahedron_a'], alpha=0.5)
    tet_b = create_solid('02_Tetrahedron_B', tb, tf,
                         COLORS['tetrahedron_b'], alpha=0.5)
    print(f'  2 x 4 vertices, 2 x 4 faces')

    # --- Layer 3: Cube ---
    print('\n[3/5] Cube...')
    cv = cube_verts(R_CUBE)
    cf = cube_faces()
    cube = create_solid('03_Cube', cv, cf,
                        COLORS['cube'], alpha=0.3, wireframe=True)
    print(f'  {len(cv)} vertices, {len(cf)} faces')

    # --- Layer 4: Dodecahedron ---
    print('\n[4/5] Dodecahedron...')
    dv = dodecahedron_verts(R_DODEC)
    df = dodecahedron_faces_from_verts(dv)
    if len(df) < 12:
        # Fallback: use bmesh primitive
        print(f'  (face detection found {len(df)}, using bmesh fallback)')
        bm = bmesh.new()
        bmesh.ops.create_icosphere(bm, subdivisions=1, radius=R_DODEC * SCALE * math.sqrt(3))
        mesh = bpy.data.meshes.new('04_Dodecahedron_mesh')
        bm.to_mesh(mesh)
        bm.free()
        dodec = bpy.data.objects.new('04_Dodecahedron', mesh)
        bpy.context.collection.objects.link(dodec)
        mat = make_material('dodec_mat', COLORS['dodecahedron'], 0.4)
        dodec.data.materials.append(mat)
    else:
        dodec = create_solid('04_Dodecahedron', dv, df,
                            COLORS['dodecahedron'], alpha=0.4)
    print(f'  {len(dv)} vertices, {len(df)} faces')

    # Stellate dodecahedron
    stellate(dodec, PHI * 0.4)
    print('  + stellated')

    # --- Layer 5: Icosahedron ---
    print('\n[5/5] Icosahedron...')
    iv = icosahedron_verts(R_ICO)
    icof = icosahedron_faces_from_verts(iv)
    ico = create_solid('05_Icosahedron', iv, icof,
                       COLORS['icosahedron'], alpha=0.35)
    print(f'  {len(iv)} vertices, {len(icof)} faces')

    # Stellate icosahedron
    stellate(ico, PHI * 0.55)
    print('  + stellated')

    # --- Lighting ---
    bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
    sun = bpy.context.active_object
    sun.data.energy = 3.0

    # Add point light inside for inner glow
    bpy.ops.object.light_add(type='POINT', location=(0, 0, 0))
    point = bpy.context.active_object
    point.data.energy = 50.0
    point.data.color = (1.0, 0.95, 0.8)

    # Frame all
    bpy.ops.object.select_all(action='SELECT')

    print('\n' + '='*60)
    print('  STAR MOTHER COMPLETE')
    print('  5 nested Platonic solids, phi-scaled:')
    print('  [Yellow] Octahedron → [Red+Blue] Star Tetrahedron →')
    print('  [Green] Cube → [Orange] Stellated Dodecahedron →')
    print('  [Purple] Stellated Icosahedron')
    print(f'  phi = {PHI:.6f}')
    print('  Rotate: middle mouse | Zoom: scroll')
    print('='*60)

build_star_mother()
