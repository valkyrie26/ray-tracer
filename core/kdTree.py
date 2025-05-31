"""
KD-Tree implementation for efficient ray-object intersection in 3D space
"""

import numpy as np
from core.vector import Vector
from core.point import Point


class KDNode:
    __slots__ = ('axis', 'left', 'right', 'bounds', 'objects', 'objects_with_bounds')

    def __init__(self, objects, depth=0, max_objects=4, max_depth=20, use_sah=False):
        self.axis = depth % 3
        self.left = None
        self.right = None

        # Cache object bounds upfront
        self.objects_with_bounds = [(obj, obj.get_bounds()) for obj in objects]
        valid_objects = [obj for obj, bounds in self.objects_with_bounds if bounds]

        self.bounds = self._compute_bounds_fast(valid_objects)

        # Stop recursion if max_depth reached or few objects remain
        if len(valid_objects) <= max_objects or depth >= max_depth:
            self.objects = valid_objects
            return

        # Choose split strategy
        if use_sah:
            split_pos = self._find_best_split_sah(valid_objects, self.axis)
        else:
            split_pos = self._fast_median(valid_objects, self.axis)

        # Divide objects into left and right children
        left_objs = []
        right_objs = []

        for obj, bounds in self.objects_with_bounds:
            if bounds:
                center = self._get_center(bounds, self.axis)
                if center < split_pos:
                    left_objs.append(obj)
                else:
                    right_objs.append(obj)

        # Only create child nodes if the division is effective
        if left_objs and right_objs:
            self.left = KDNode(left_objs, depth + 1, max_objects, max_depth, use_sah)
            self.right = KDNode(right_objs, depth + 1, max_objects, max_depth, use_sah)
            self.objects = []  # Clear objects list to save memory
        else:
            # Division failed or skewed, make this a leaf node
            self.objects = valid_objects

    @staticmethod
    def _compute_surface_area(bounds):
        """Compute surface area of a bounding box"""
        min_p, max_p = bounds
        dx = max_p.x - min_p.x
        dy = max_p.y - min_p.y
        dz = max_p.z - min_p.z
        return 2 * (dx * dy + dx * dz + dy * dz)

    def _fast_median(self, axis):
        """Calculate median without numpy for small arrays"""
        centers = []
        for obj, bounds in [(o, b) for o, b in self.objects_with_bounds if b]:
            centers.append(self._get_center(bounds, axis))

        if len(centers) <= 10:
            sorted_centers = sorted(centers)
            return sorted_centers[len(sorted_centers) // 2]
        else:
            return float(np.median(centers))

    def _find_best_split_sah(self, objects, axis):
        """Find split position using Surface Area Heuristic"""
        # Sort objects by their center along the axis
        sorted_objs = sorted(
            [(obj, bounds) for obj, bounds in self.objects_with_bounds if bounds],
            key=lambda x: self._get_center(x[1], axis)
        )

        best_cost = float('inf')
        best_split = None

        # Evaluate multiple split positions
        for i in range(1, len(sorted_objs)):
            left = [x[0] for x in sorted_objs[:i]]
            right = [x[0] for x in sorted_objs[i:]]

            left_bounds = self._compute_bounds_fast(left)
            right_bounds = self._compute_bounds_fast(right)

            # Calculate SAH cost
            left_area = self._compute_surface_area(left_bounds)
            right_area = self._compute_surface_area(right_bounds)

            cost = left_area * len(left) + right_area * len(right)

            if cost < best_cost:
                best_cost = cost
                left_center = self._get_center(sorted_objs[i - 1][1], axis)
                right_center = self._get_center(sorted_objs[i][1], axis)
                best_split = (left_center + right_center) / 2

        return best_split if best_split is not None else self._fast_median(objects, axis)

    @staticmethod
    def _get_center(bounds, axis):
        """
        Get the center coordinate of the bounding box along the specified axis.
        :param bounds: Bounding box defined by two points (min_bound, max_bound).
        :param axis: Axis along which to compute the center (0 for x, 1 for y, 2 for z).
        :return: Center coordinate along the specified axis.
        """
        min_bound, max_bound = bounds
        if axis == 0:
            return (min_bound.x + max_bound.x) / 2
        elif axis == 1:
            return (min_bound.y + max_bound.y) / 2
        else:  # axis == 2
            return (min_bound.z + max_bound.z) / 2

    @staticmethod
    def _compute_bounds_fast(objects):
        """
        Compute the bounding box that contains all objects.
        :param objects: List of objects to compute bounds for.
        :return: Tuple of two Points representing the minimum and maximum bounds.
        """
        if not objects:
            return Point(0, 0, 0), Point(0, 0, 0)

        # Initialize with extreme values
        min_x = min_y = min_z = float('inf')
        max_x = max_y = max_z = float('-inf')

        # Find min and max bounds for all objects
        for obj in objects:
            bounds = obj.get_bounds()
            if bounds:
                min_bound, max_bound = bounds
                min_x = min(min_x, min_bound.x)
                min_y = min(min_y, min_bound.y)
                min_z = min(min_z, min_bound.z)
                max_x = max(max_x, max_bound.x)
                max_y = max(max_y, max_bound.y)
                max_z = max(max_z, max_bound.z)

        # Handle case with no valid bounds
        if min_x == float('inf'):
            return Point(0, 0, 0), Point(0, 0, 0)

        return Point(min_x, min_y, min_z), Point(max_x, max_y, max_z)

    def intersect_ray(self, ray):
        """
        Check if a ray intersects the bounding box of this node.
        :param ray: Ray object with origin and direction attributes.
        :return: True if the ray intersects the bounding box, False otherwise.
        """
        bounds_min, bounds_max = self.bounds
        origin = ray.origin
        direction = ray.direction

        # Calculate inverse direction components (handle zeros)
        inv_dir_x = 1.0 / direction.x if direction.x != 0 else float('inf')
        inv_dir_y = 1.0 / direction.y if direction.y != 0 else float('inf')
        inv_dir_z = 1.0 / direction.z if direction.z != 0 else float('inf')

        # Calculate t values for each slab
        t1_x = (bounds_min.x - origin.x) * inv_dir_x
        t2_x = (bounds_max.x - origin.x) * inv_dir_x
        t1_y = (bounds_min.y - origin.y) * inv_dir_y
        t2_y = (bounds_max.y - origin.y) * inv_dir_y
        t1_z = (bounds_min.z - origin.z) * inv_dir_z
        t2_z = (bounds_max.z - origin.z) * inv_dir_z

        # Swap if necessary
        if inv_dir_x < 0:
            t1_x, t2_x = t2_x, t1_x
        if inv_dir_y < 0:
            t1_y, t2_y = t2_y, t1_y
        if inv_dir_z < 0:
            t1_z, t2_z = t2_z, t1_z

        # Find entry and exit points
        tmin = max(max(t1_x, t1_y), t1_z)
        tmax = min(min(t2_x, t2_y), t2_z)

        return tmax > max(tmin, 0.0)


class KDTree:
    __slots__ = ('root',)  # Memory optimization

    def __init__(self, objects, max_objects=4, max_depth=20, use_sah=False):
        self.root = KDNode(objects, max_objects=max_objects, max_depth=max_depth, use_sah=use_sah) if objects else None

    def intersect(self, ray):
        """
        Find the closest intersection of a ray with objects in the KD-Tree.
        Skips intersecting the object stored in ray.space (useful for transmission and shadow rays).
        """
        if not self.root:
            return None

        closest_hit = None
        min_dist = float('inf')

        # Stack-based KD-tree traversal: (node, estimated_distance)
        nodes_to_visit = [(self.root, 0.0)]

        while nodes_to_visit:
            # Optional optimization: sort stack by estimated distance occasionally
            if len(nodes_to_visit) > 8:
                nodes_to_visit.sort(key=lambda x: x[1])

            current_node, est_dist = nodes_to_visit.pop(0)

            # Skip node if all hits here would be farther than one we've already found
            if est_dist > min_dist:
                continue

            # Bounding box check
            if not current_node.intersect_ray(ray):
                continue

            # Leaf node: check each object
            for obj in current_node.objects:
                hit = obj.intersect(ray)
                if not hit:
                    continue

                # Skip every hit on the object that spawned this ray
                if ray.space is obj:
                    continue

                # Otherwise, accept it if it’s the nearest so far
                if 1e-4 < hit['t'] < min_dist:
                    closest_hit = hit
                    min_dist = hit['t']

            else:
                # Internal node: enqueue children
                if current_node.left:
                    left_dist = self._estimate_distance(ray, current_node.left.bounds)
                    nodes_to_visit.append((current_node.left, left_dist))

                if current_node.right:
                    right_dist = self._estimate_distance(ray, current_node.right.bounds)
                    nodes_to_visit.append((current_node.right, right_dist))

        return closest_hit

    @staticmethod
    def _estimate_distance(ray, bounds):
        """
        Estimate the distance from the ray origin to the closest point on the bounding box.
        :param ray: Ray object with origin and direction attributes.
        :param bounds: Tuple of two Points representing the bounding box (min_bound, max_bound).
        :return: Estimated distance to the closest point on the bounding box.
        """
        bounds_min, bounds_max = bounds

        # For rays starting inside the box
        if (bounds_min.x <= ray.origin.x <= bounds_max.x and
                bounds_min.y <= ray.origin.y <= bounds_max.y and
                bounds_min.z <= ray.origin.z <= bounds_max.z):
            return 0.0

        # Find the closest point on the box to the ray origin
        closest_x = max(bounds_min.x, min(ray.origin.x, bounds_max.x))
        closest_y = max(bounds_min.y, min(ray.origin.y, bounds_max.y))
        closest_z = max(bounds_min.z, min(ray.origin.z, bounds_max.z))

        # Calculate squared distance to this point
        dx = ray.origin.x - closest_x
        dy = ray.origin.y - closest_y
        dz = ray.origin.z - closest_z

        # Only consider distance in the ray direction
        sqr_dist = dx * dx + dy * dy + dz * dz
        if sqr_dist == 0:
            return 0.0

        # Project the distance vector onto the ray direction
        to_closest = Vector(closest_x - ray.origin.x,
                            closest_y - ray.origin.y,
                            closest_z - ray.origin.z)
        proj = to_closest.dot(ray.direction)

        # If projection is negative, the box is behind the ray
        return max(0.0, proj)
