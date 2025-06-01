"""
Camera has a position, lookAt, up, and render(world) method
Responsible for ray tracing
"""

import numpy as np
from core.ray import Ray


class Camera:
    def __init__(self, position, lookat, up, fov, width, height):
        self.position = position  # Camera position (Point)
        self.lookat = lookat  # Point the camera is looking at (Point)
        self.up = up  # Up vector (Vector)
        self.fov = fov  # Field of view (in degrees)
        self.width = width  # Image width in pixels
        self.height = height  # Image height in pixels

        # Compute camera basis vectors
        self.forward = (self.lookat - self.position).normalize()
        self.right = self.forward.cross(self.up).normalize()
        self.up = self.right.cross(self.forward).normalize()

        # Film plane dimensions in world units
        aspect_ratio = self.width / self.height
        self.film_height = 2.0 * np.tan(np.radians(self.fov / 2.0))
        self.film_width = self.film_height * aspect_ratio

    def render(self, world):
        """
        Render the scene from the camera's perspective.
        :param world: World object containing the scene
        :return: Rendered image as a numpy array
        """
        image = np.zeros((self.height, self.width, 3))  # RGB image

        for y in range(self.height):
            for x in range(self.width):
                color = np.zeros(3)  # Initialize color for the pixel

                # Toggle available - normal or super sampling

                # Normal sampling
                image[y, x] = self.normal_sampling(x, y, color, world)

                # # Super-sampling (will take longer to render)
                # image[y, x] = self.super_sampling(x, y, color, world)

        return image

    def normal_sampling(self, x, y, color, world):
        """
        Normal sampling for ray tracing
        :param x: x coordinate of the pixel
        :param y: y coordinate of the pixel
        :param color: Color accumulator
        :param world: World object containing the scene
        :return: Color value for the pixel
        """
        ray = self.generate_ray(x, y)
        color += world.spawn_ray(ray).rgb
        return color

    def super_sampling(self, x, y, color, world):
        """
        Super-sampling for antialiasing
        :param x: x coordinate of the pixel
        :param y: y coordinate of the pixel
        :param color: Color accumulator
        :param world: World object containing the scene
        :return: Color value for the pixel
        """
        for i in range(2):
            for j in range(2):
                ray = self.generate_ray(x + i / 2, y + j / 2)
                color += world.spawn_ray(ray).rgb
        return color / 4

    def view_matrix(self):
        """
        Compute the view transform matrix for the camera.
        :return: 4x4 view matrix
        """
        z_axis = (self.position - self.lookat).normalize()
        x_axis = self.up.cross(z_axis).normalize()
        yaxis = z_axis.cross(x_axis)

        # Translate the camera to the world
        translation = np.array([
            [-x_axis.dot(self.position), -yaxis.dot(self.position), -z_axis.dot(self.position), 1]
        ])

        # Construct the 4x4 view matrix
        return np.array([
            [x_axis.x, yaxis.x, z_axis.x, 0],
            [x_axis.y, yaxis.y, z_axis.y, 0],
            [x_axis.z, yaxis.z, z_axis.z, 0],
            [translation[0][0], translation[0][1], translation[0][2], 1]
        ])

    def generate_ray(self, x, y):
        """
        Generate a ray from the camera through the pixel (x, y) on the image plane.
        :param x: x-coordinate of the pixel
        :param y: y-coordinate of the pixel
        :return: Ray object
        """
        u = (x + 0.5) / self.width * self.film_width - self.film_width / 2.0
        v = (y + 0.5) / self.height * self.film_height - self.film_height / 2.0

        # Ray direction
        direction = self.forward + self.right * u + self.up * v
        ray_origin = self.position  # Camera position (eye)

        # Normalize the direction vector
        ray_direction = direction.normalize()

        # Return the ray
        return Ray(ray_origin, ray_direction)



