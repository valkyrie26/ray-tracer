from __future__ import annotations

from core.color import Color
import numpy as np
import random
import math

from objects.polygon import Polygon

from core.ray import Ray
from core.point import Point
from core.vector import Vector
from core.kdTree import KDTree


MAX_DEPTH = 5  # Min 2 needed to see reflection


class World:
    def __init__(self):
        self.objects = []  # List to store all objects in the scene
        self.scene_matrix = np.eye(4)  # Scene transformation matrix
        self.background_color = Color(0.5, 0.7, 1.0)  # Light blue background color
        self.light_source = {
            'position': Point(10, 10, 10),  # Light position
            'color': Color(1.0, 1.0, 1.0)  # Light color (white)
        }
        self.kd_tree = None  # KD-tree for efficient ray-object intersection

    def add(self, *obj):
        """
        Add an object to the world and rebuild the KD-tree.
        :param obj: Objects to be added to the world
        :return: None
        """
        self.objects.extend(obj)
        self.rebuild_tree()  # Only rebuild once after adding objects

    def rebuild_tree(self):
        """Rebuild KD-tree only when needed"""
        self.kd_tree = KDTree(self.objects) if self.objects else None

    def get_objects(self):
        """
        Get all objects in the world.
        :return: List of objects in the world
        """
        return self.objects

    @staticmethod
    def transform(obj, matrix):
        """
        Apply a transformation matrix to an object.
        :param obj: Object to be transformed
        :param matrix: Transformation matrix
        :return: None
        """
        obj.transform(matrix)

    def transform_all_objects(self, matrix):
        """
        Transform all objects in the world using a transformation matrix.
        :param matrix: Transformation matrix
        :return: None
        """
        for obj in self.objects:
            self.transform(obj, matrix)

    def spawn_ray(self, ray, depth=1):
        """
        Ray‐trace with hard black shadows, arbitrary illumination models,
        mirror‐reflection, and refraction—while keeping the first‐bounce
        specular highlight at full strength.
        """
        # 0) recursion guard
        if depth > MAX_DEPTH:
            return self.background_color

        # 1) intersection
        if not hasattr(self, 'kd_tree') or self.kd_tree is None:
            return self.background_color
        hit = self.kd_tree.intersect(ray)
        if not hit:
            return self.background_color

        obj = hit['object']
        P = ray.origin + ray.direction * hit['t']
        N = self.calculate_normal(obj, P)
        view_dir = (ray.origin - P).normalize()
        light_dir = (self.light_source['position'] - P).normalize()

        # 2) shadow factor (opaque → 0, transparent attenuate)
        shadow_ray = Ray(P + N * 1e-4, light_dir, space=obj)
        blocker = self.kd_tree.intersect(shadow_ray)
        if blocker and blocker['object'] is not obj:
            blk = blocker['object']
            shadow = 0.0 if blk.kt == 0 else (1.0 - blk.kt)
        else:
            shadow = 1.0

        # generic “Phong-like” material colors for .illuminate calls
        mat = {
            'ambient_color': Color(0.1, 0.1, 0.1),
            'specular_color': Color(1.0, 1.0, 1.0)
        }

        # 3) split the local illumination into two pieces:
        #    – ambient+diffuse, which we _do_ attenuate by transparency (except on first hit)
        #    – specular, which we leave at full strength on the first bounce
        atten = 1.0 if depth == 1 else (1 - obj.kt)

        # 3a) ambient+diffuse only, shadowed & transparency‐attenuated

        ad_local = obj.illumination_model.illuminate(
            obj.color,
            self.light_source['color'],
            N, light_dir, view_dir,
            {
                'ambient_color': mat['ambient_color'],
                'specular_color': Color(0, 0, 0)
            },
            P
        )
        ad_local = ad_local * shadow * atten

        # 3b) specular only, shadowed but NOT transparency‐attenuated
        spec_local = obj.illumination_model.illuminate(
            Color(0, 0, 0),
            self.light_source['color'],
            N, light_dir, view_dir,
            {
                'ambient_color': Color(0, 0, 0),
                'specular_color': mat['specular_color']
            },
            P
        )
        spec_local = spec_local * shadow

        # 3c) combine direct lighting
        if obj.kt > 0:
            # transparent surface: no diffuse, only specular
            local = ad_local * (1 - obj.kt) + spec_local * obj.kt
        else:
            # opaque surface: full Phong (diffuse + specular)
            local = ad_local + spec_local

        # 4) mirror‐style reflection
        refl = Color(0, 0, 0)
        if obj.kr > 0:
            refl = self.basic_reflection(obj, P, N, ray, depth, Color(0, 0, 0))

        # 5) refraction + Fresnel‐mix
        refr = Color(0, 0, 0)
        if obj.kt > 0:
            def refract(I, Nn, n1, n2):
                cos_i = -Nn.dot(I)
                η = n1 / n2
                sin2t = η * η * (1 - cos_i * cos_i)
                if sin2t > 1.0:
                    return None
                cos_t = math.sqrt(1 - sin2t)
                return (I * η + Nn * (η * cos_i - cos_t)).normalize()

            # set up indices & normal flip if inside object
            n1, n2 = 1.0, obj.material['refractive_index']
            Nn = N
            if N.dot(ray.direction) > 0:
                Nn, n1, n2 = -N, n2, n1
            cos_i = -Nn.dot(ray.direction)

            # always trace a physical reflection for the Fresnel term
            refl_o = P + Nn * 1e-4
            refl_d = (ray.direction - 2 * ray.direction.dot(Nn) * Nn).normalize()
            refl = self.spawn_ray(Ray(refl_o, refl_d, space=obj), depth + 1)

            # then attempt actual refraction
            rdir = refract(ray.direction, Nn, n1, n2)
            if rdir is not None:
                F0 = ((n1 - n2) / (n1 + n2)) ** 2
                F = F0 + (1 - F0) * (1 - cos_i) ** 5

                refr_o = P + rdir * 1e-4
                refr = self.spawn_ray(Ray(refr_o, rdir, space=obj), depth + 1)

                # Fresnel‐weight reflection vs. refraction
                refl *= F
                refr *= (1 - F)

        # 6) final composition
        #    – direct = ad_local + spec_local
        #    – reflection scaled by kr
        #    – refraction scaled by kt
        color = local + refl * obj.kr + refr * obj.kt
        return self.clamp_color(color)

    def basic_reflection(self, obj, intersection_point, normal, ray, depth, illumination):
        """
        Basic reflection model. If the object has a kr (reflection coefficient), spawn a reflection ray.
        :param obj: Object that was hit
        :param intersection_point: Point of intersection of the ray with the object
        :param normal: Normal at the intersection point
        :param ray: Ray that hit the object
        :param depth: Recursion depth
        :param illumination: Current illumination color
        :return: Illuminated color at the intersection point
        """
        if hasattr(obj, 'kr') and obj.kr > 0:
            reflect_dir = (ray.direction - normal * (2 * ray.direction.dot(normal))).normalize()
            reflect_ray = Ray(intersection_point + normal * 0.001, reflect_dir)
            reflected_color = self.spawn_ray(reflect_ray, depth + 1)
            illumination = illumination * (1 - obj.kr) + reflected_color * obj.kr

        return illumination

    def phong_brdf_reflection(self, obj, intersection_point, normal, ray, depth, illumination):
        """
        Phong BRDF reflection model. If the object has a kr (reflection coefficient), spawn multiple reflection rays.
        It makes the reflection look rougher
        :param obj: Object that was hit
        :param intersection_point: Point of intersection of the ray with the object
        :param normal: Normal at the intersection point
        :param ray: Ray that hit the object
        :param depth: Recursion depth
        :param illumination: Current illumination color
        :return: Illuminated color at the intersection point
        """
        if hasattr(obj, 'kr') and isinstance(obj.kr, (int, float)) and obj.kr > 0:
            ideal_reflect_dir = ray.direction - normal * (2 * ray.direction.dot(normal))
            ideal_reflect_dir = ideal_reflect_dir.normalize()  # Normalize ideal reflection direction

            # Parameters for glossy reflection
            num_rays = 5
            phong_exponent = getattr(obj, 'shininess', 50)  # Control glossiness
            reflection_color = Color(0, 0, 0)
            total_weight = 0

            for _ in range(num_rays):
                # Sample direction around the reflection vector using Phong lobe
                perturbed_dir = self.sample_phong_lobe(ideal_reflect_dir, phong_exponent)
                perturbed_dir = perturbed_dir.normalize()  # Ensure perturbed direction is normalized

                reflection_ray = Ray(intersection_point + normal * 1e-4, perturbed_dir)
                sample_color = self.spawn_ray(reflection_ray, depth + 1)

                # Weight using Phong BRDF (cos^n term)
                cos_theta = max(perturbed_dir.dot(ideal_reflect_dir), 0)
                weight = (phong_exponent + 2) / (2 * np.pi) * (cos_theta ** phong_exponent)

                reflection_color += sample_color * weight  # Accumulate weighted color
                total_weight += weight  # Accumulate total weight

            # Normalize the final reflection color by the total weight
            if total_weight > 0:
                reflection_color = reflection_color * (1 / total_weight)  # Normalize by total weight

            reflection_color = reflection_color * obj.kr  # Apply the reflection coefficient
            illumination = illumination * (1 - obj.kr) + reflection_color

        return illumination

    @staticmethod
    def sample_phong_lobe(ideal_dir, exponent):
        """
        Sample a direction around the ideal reflection direction using a Phong lobe distribution.
        :param ideal_dir: Ideal reflection direction
        :param exponent: Phong exponent controlling the glossiness
        :return: Sampled direction in world space
        """
        # Sample spherical coordinates
        u = random.random()
        v = random.random()
        theta = math.acos(u ** (1 / (exponent + 1)))
        phi = 2 * math.pi * v

        # Convert to cartesian coordinates in local space
        x = math.sin(theta) * math.cos(phi)
        y = math.sin(theta) * math.sin(phi)
        z = math.cos(theta)

        # Build orthonormal basis (w = ideal_dir, u,v = perpendiculars)
        w = ideal_dir.normalize()
        up = Vector(0, 1, 0) if abs(w.y) < 0.9 else Vector(1, 0, 0)
        u = w.cross(up).normalize()
        v = w.cross(u)

        # Rotate sampled direction into world space
        direction = u * x + v * y + w * z
        return direction.normalize()

    @staticmethod
    def clamp_color(color):
        """
        Clamp the color values to be within the range [0, 1].
        :param color: Color object to clamp
        :return: Clamped Color object
        """
        return Color(
            min(1, max(0, color.rgb[0])),
            min(1, max(0, color.rgb[1])),
            min(1, max(0, color.rgb[2]))
        )

    @staticmethod
    def calculate_normal(obj, intersection_point):
        """
        Calculate the normal at the intersection point based on the object type.
        :param obj: Object that was hit
        :param intersection_point: Point of intersection of the ray with the object
        :return: Normal vector at the intersection point
        """
        if isinstance(obj, Polygon):
            # Polygon normal calculation
            v0, v1, v2 = obj.vertices
            normal = (v1 - v0).cross(v2 - v0).normalize()
        else:
            # Sphere normal calculation (must be unit-length!)
            normal = (intersection_point - obj.center).normalize()

        return normal

    def is_in_shadow(self, shadow_ray, obj):
        """
        Return True if an *opaque* object (kt == 0) blocks the light.
        Transparent objects (kt > 0) do not cast hard shadows.
        """
        hit = self.kd_tree.intersect(shadow_ray)
        if not hit:
            return False
        blocker = hit['object']
        # skip the object we’re shading, and skip any transparent object
        return blocker is not obj and getattr(blocker, 'kt', 0) == 0

    def compute_shadow_transmittance(self, shadow_ray, max_dist):
        """
        Cast a ray toward the light, multiplying through any kt’s you hit.
        Returns a float in [0,1]: 0=fully blocked, 1=fully clear.
        """
        tr = 1.0
        eps = 1e-4

        # keep marching the ray until it reaches the light or is fully blocked
        while True:
            hit = self.kd_tree.intersect(shadow_ray)
            if not hit or hit['t'] > max_dist:
                break

            o = hit['object']
            # skip self‐hit
            if o is shadow_ray.space:
                # advance origin past this surface
                shadow_ray.origin = shadow_ray.origin + shadow_ray.direction * (hit['t'] + eps)
                continue

            # attenuate by this object’s transparency
            # (kt=1 means fully clear, kt=0 means opaque)
            tr *= o.kt
            if tr <= 0:
                return 0.0

            # march onward from just past this surface
            shadow_ray.origin = shadow_ray.origin + shadow_ray.direction * (hit['t'] + eps)
            # keep the same shadow_ray.direction, keep shadow_ray.space=None

        return tr

    def set_scene_transformation(self, translation, scale):
        """
        Set the transformation matrix for the scene.
        :param translation: Translation vector (x, y, z)
        :param scale: Scale vector (sx, sy, sz)
        :return: None
        """
        translation_matrix = np.array([
            [1, 0, 0, translation[0]],
            [0, 1, 0, translation[1]],
            [0, 0, 1, translation[2]],
            [0, 0, 0, 1]
        ])

        scale_matrix = np.array([
            [scale[0], 0, 0, 0],
            [0, scale[1], 0, 0],
            [0, 0, scale[2], 0],
            [0, 0, 0, 1]
        ])

        self.scene_matrix = np.dot(translation_matrix, scale_matrix)

