"""
Example code to render the stanford bunny.

Download bunny: http://graphics.stanford.edu/data/3Dscanrep/
save bunny to a folder called "bunny"

Notes:
bun_zipper_res3 should take less than 2 minutes to render (has about 900 polygons)
bun_zipper_res3 should take less than 25 minutes to render (has about 5000 polygons)
"""

import trimesh
from scene.camera import Camera
from scene.world import World
from core.color import Color
from core.point import Point
from core.vector import Vector
from objects.polygon import Polygon
import matplotlib.pyplot as plt
import numpy as np


def load_ply_as_polygons(path):
    """Loads a .ply file using trimesh and returns a list of Polygon objects."""
    try:
        # Load mesh with error handling
        mesh = trimesh.load(path, force='mesh')

        # Ensure we have a proper mesh object
        if not isinstance(mesh, trimesh.Trimesh):
            if isinstance(mesh, trimesh.Scene):
                # Get the first mesh from the scene
                mesh = next(iter(mesh.geometry.values()))
            else:
                raise ValueError("Loaded file is not a mesh or scene")

        # Process the mesh (this will triangulate if needed)
        mesh = mesh.process()

        # Verify we have triangular faces
        if mesh.faces.shape[1] != 3:
            # Convert quads or n-gons to triangles
            triangles = []
            for face in mesh.faces:
                if len(face) == 3:
                    triangles.append(face)
                else:
                    # Manually triangulate polygons with more than 3 vertices
                    for i in range(1, len(face) - 1):
                        triangles.append([face[0], face[i], face[i + 1]])
            mesh.faces = np.array(triangles)

        print(f"Mesh loaded: {len(mesh.vertices)} vertices, {len(mesh.faces)} faces")

        polygons = []
        t_count = 0
        for face in mesh.faces:
            # Get vertices for this face
            verts = [Point(*mesh.vertices[int(i)]) for i in face]

            # Calculate normal
            edge1 = verts[1] - verts[0]
            edge2 = verts[2] - verts[0]
            normal = edge1.cross(edge2).normalize()

            # Create polygon
            poly = Polygon(
                vertices=verts,
                normal=normal,
                material={
                    'ambient_color': Color(0.1, 0.1, 0.1),
                    'specular_color': Color(1, 1, 1)
                },
                color=Color(0.7, 0.7, 0.7),
                kr=0.0,
                kt=0.0
            )
            polygons.append(poly)
            t_count += 1
            print("Triangle created count: ", t_count)

        return polygons

    except Exception as e:
        print(f"Error loading mesh: {str(e)}")
        raise


def main():
    world = World()

    # Load mesh polygons
    mesh_path = "bunny/reconstruction/bun_zipper_res4.ply"  # Path to the .ply file
    mesh_polygons = load_ply_as_polygons(mesh_path)

    add_count = 0
    # Add mesh polygons to the world
    for poly in mesh_polygons:
        world.add(poly)
        add_count += 1
        # Stanford bunny files can take a while to render, use this print statement to keep track (optional)
        print("Added polygon to world: ", add_count)

    # Light source
    world.light_source = {
        'position': Point(0, 0.5, -1),  # Adjusted light position
        'color': Color(1, 1, 1)
    }

    # Camera
    camera = Camera(
        position=Point(0, 0.3, -0.5),  # Adjusted camera position
        lookat=Point(0, 0.1, 0),
        up=Vector(0, 1, 0),
        fov=60,
        width=600,
        height=600
    )

    # Render
    print("Rendering has started...")
    image = camera.render(world)
    plt.imshow(image)
    plt.axis('off')
    plt.show()


if __name__ == "__main__":
    main()
