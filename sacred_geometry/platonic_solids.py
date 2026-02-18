# Platonic Solids Generators

import bpy
import math

def create_tetrahedron(size=1.0, location=(0, 0, 0)):
    """4 faces, 4 vertices, 6 edges - Fire element"""
    # TODO: Implement proper tetrahedron
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, size=size, location=location)
    return bpy.context.active_object

def create_cube(size=1.0, location=(0, 0, 0)):
    """6 faces, 8 vertices, 12 edges - Earth element"""
    bpy.ops.mesh.primitive_cube_add(size=size, location=location)
    return bpy.context.active_object

def create_octahedron(size=1.0, location=(0, 0, 0)):
    """8 faces, 6 vertices, 12 edges - Air element"""
    # TODO: Implement proper octahedron
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, size=size, location=location)
    return bpy.context.active_object

def create_dodecahedron(size=1.0, location=(0, 0, 0)):
    """12 faces, 20 vertices, 30 edges - Ether/Universe element"""
    # TODO: Implement proper dodecahedron
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, size=size, location=location)
    return bpy.context.active_object

def create_icosahedron(size=1.0, location=(0, 0, 0)):
    """20 faces, 12 vertices, 30 edges - Water element"""
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, size=size, location=location)
    return bpy.context.active_object

def create_all_platonic_solids(size=1.0, spacing=3.0):
    """Create all 5 Platonic solids in a row"""
    solids = [
        ("Tetrahedron", create_tetrahedron),
        ("Cube", create_cube),
        ("Octahedron", create_octahedron),
        ("Dodecahedron", create_dodecahedron),
        ("Icosahedron", create_icosahedron),
    ]
    
    objects = []
    for i, (name, func) in enumerate(solids):
        x = i * spacing - (len(solids) - 1) * spacing / 2
        obj = func(size=size, location=(x, 0, 0))
        obj.name = name
        objects.append(obj)
    
    return objects
