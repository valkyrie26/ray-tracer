"""
Example code to render a scene inspired from the classic Whitted paper from the 80's
"""

import matplotlib.pyplot as plt
from scene.camera import Camera
from scene.world import World
from core.color import Color
from objects.sphere import Sphere
from core.point import Point
from core.vector import Vector
from objects.cuboid import Cuboid
from objects.torus import Torus
from objects.cylinder import Cylinder
import numpy as np
import os
from scene.toneReproduction import tone_reproduce


def main():
    # Initialize world
    world = World()

    # light source details in world (hardcoded for now)
    world.light_source = {
        'position': Point(7, 5, -40),  # Light position
        'color': Color(1.0, 1.0, 1.0)  # Light color (white)
    }

    # Create a sphere that is reflective
    sphere = Sphere(center=Point(-0.5, 0.5, -0.9), radius=1.1, color=Color(1, 1, 0),
                    kr=0.35, kt=0.0,
                    material={'ambient_color': Color(0, 0, 0), 'specular_color': Color(1, 1, 1)},
                    illumination_model='phong')

    # Add sphere to world
    world.add(sphere)

    # Create a sphere that is transparent
    sphere2 = Sphere(center=Point(1.2, 0.7, -1.7), radius=1.2, color=Color(0, 0, 1),
                     kr=0, kt=0.8,
                     material={'ambient_color': Color(0, 0, 0), 'specular_color': Color(1, 1, 1),
                               'refractive_index': 1.1},
                     illumination_model='phong')

    # Add sphere to world
    world.add(sphere2)

    # Create a cuboid with a checkerboard texture for the floor
    cuboid = Cuboid(center=Point(0, 1, 0.3), width=5.5, height=4, depth=0.7, color=Color(0, 1, 0),
                    kr=0.0, kt=0.0,
                    material={'ambient_color': Color(0, 0, 0), 'specular_color': Color(1, 1, 1)},
                    illumination_model='mosaic')

    # Add cuboid to world
    world.add(cuboid)

    # Examples for other available objects - uncomment to use in scene

    # cylinder = Cylinder(
    #     center=Point(3.5, -3, -1.4),
    #     radius=0.6,
    #     height=2.8,
    #     color=Color(0, 0, 1),
    #     kr=0,
    #     kt=0.0,
    #     material={
    #         'ambient_color': Color(0.1, 0.1, 0.1),
    #         'specular_color': Color(1.0, 1.0, 1.0),
    #     },
    #     illumination_model='phong'
    # )
    # world.add(cylinder)

    # torus = Torus(
    #     center=Point(3.5, -3, -0.8),
    #     major_radius=1.5,
    #     minor_radius=0.5,
    #     color=Color(0.8, 0.2, 0.2),
    #     kr=0.1,
    #     kt=0.0,
    #     material={'ambient_color': Color(0.1, 0.1, 0.1),
    #               'specular_color': Color(1, 1, 1)},
    #     illumination_model='phong'
    # )
    # world.add(torus)

    # Create a camera
    camera = Camera(
        position=Point(1, 3, -3),  # Camera position
        lookat=Point(1, 0, 0),  # Looking at -Z direction
        up=Vector(0.0, 0.6, 0.0),  # Up vector
        fov=90,  # Field of view
        width=500, height=500  # Image size
    )

    hdr_image = camera.render(world)  # Pass KD-tree to the render function

    # To render without tone reproduction, uncomment the following lines:
    # # Display the image using matplotlib
    # plt.imshow(hdr_image)
    # plt.axis('off')
    # plt.show()

    # Tone-reproduction for display:
    ldr = tone_reproduce(
        hdr_image,
        manual_exposure=0.15,  # if auto_key=False
        auto_key=False,  # computes a safe exposure so average luminance → 0.18
        white_pct=90.0,  # clamp top 5%
        contrast=1.1,
        saturation=1.2,
        gamma=2.2
    )
    plt.imshow(ldr)
    plt.axis('off')
    plt.show()


if __name__ == "__main__":
    main()
