# Isotropic Vector Matrix (IVM) — Voice to OmniCAD v0.4.0
# Buckminster Fuller / Nassim Haramein: the infinite tiling of
# Vector Equilibria (cuboctahedra) — Haramein's fabric of spacetime.
# Each node is a Vector Equilibrium; edges connect nearest neighbours
# at distance = 1 (the IVM lattice = FCC / A2 crystal packing).
# First-mover: no Blender addon exposes this as a named sacred geometry.

import bpy
import bmesh
import math
from mathutils import Vector
import itertools


# IVM basis vectors: 12 directions from origin to cuboctahedron vertices
_IVM_BASIS = [
    Vector(( 1,  1,  0)), Vector(( 1, -1,  0)),
    Vector((-1,  1,  0)), Vector((-1, -1,  0)),
    Vector(( 1,  0,  1)), Vector(( 1,  0, -1)),
    Vector((-1,  0,  1)), Vector((-1,  0, -1)),
    Vector(( 0,  1,  1)), Vector(( 0,  1, -1)),
    Vector(( 0, -1,  1)), Vector(( 0, -1, -1)),
]


def _ivm_lattice_nodes(layers=2):
    """
    Return all IVM node positions within *layers* shells from origin.
    Uses FCC (face-centred cubic) lattice: integer combos of two
    orthogonal FCC primitive vectors that stay within radius layers*sqrt(2).
    """
    nodes = set()
    r = layers + 1
    for i, j, k in itertools.product(range(-r, r+1), repeat=3):
        # FCC condition: i+j+k must be even
        if (i + j + k) % 2 == 0:
            pos = Vector((i, j, k)) * (1.0 / math.sqrt(2))
            if pos.length <= layers * 1.05:
                nodes.add((round(pos.x, 6), round(pos.y, 6), round(pos.z, 6)))
    return [Vector(n) for n in nodes]


def create_isotropic_vector_matrix(
    name="Isotropic Vector Matrix",
    layers=2,
    node_radius=0.05,
    draw_edges=True,
    collection_name="Haramein Suite",
):
    """
    Isotropic Vector Matrix (IVM) — Haramein's spacetime fabric.

    layers      : number of shells to generate (2 = compact demo,
                  3+ = larger lattice — gets heavy above 4)
    node_radius : radius of the sphere placed at each node (0 = skip)
    draw_edges  : draw edges between nearest neighbours (dist ≈ 1/√2)
    """
    nodes = _ivm_lattice_nodes(layers)
    edge_len = 1.0 / math.sqrt(2)
    tol = edge_len * 0.15  # neighbour tolerance

    col = bpy.data.collections.get(collection_name)
    if col is None:
        col = bpy.data.collections.new(collection_name)
        bpy.context.scene.collection.children.link(col)

    # ── Edge mesh ────────────────────────────────────────────────
    last_obj = None
    if draw_edges:
        mesh = bpy.data.meshes.new(name + "_Edges")
        bm = bmesh.new()
        bm_node_map = {}
        for n in nodes:
            key = (round(n.x,5), round(n.y,5), round(n.z,5))
            bm_node_map[key] = bm.verts.new(n)
        bm.verts.ensure_lookup_table()
        node_list = list(bm_node_map.values())
        # Connect pairs within edge_len + tol
        for a, b in itertools.combinations(node_list, 2):
            if abs((a.co - b.co).length - edge_len) < tol:
                try:
                    bm.edges.new((a, b))
                except ValueError:
                    pass
        bm.to_mesh(mesh)
        bm.free()
        mesh.update()
        edge_obj = bpy.data.objects.new(name + "_Edges", mesh)
        col.objects.link(edge_obj)
        last_obj = edge_obj

    # ── Node spheres ─────────────────────────────────────────────
    if node_radius > 0:
        for i, n in enumerate(nodes):
            bpy.ops.mesh.primitive_uv_sphere_add(
                radius=node_radius,
                location=n,
                segments=6,
                ring_count=4,
            )
            sphere = bpy.context.active_object
            sphere.name = f"{name}_Node_{i:03d}"
            # Move from default collection to our collection
            for other_col in list(sphere.users_collection):
                other_col.objects.unlink(sphere)
            col.objects.link(sphere)
            last_obj = sphere

    if last_obj:
        bpy.context.view_layer.objects.active = last_obj
        last_obj.select_set(True)
    return last_obj
