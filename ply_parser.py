def load_ply(filename, color, kr=0.0, kt=0.0, material=None):
    from objects.polygon import Polygon
    from core.point import Point

    vertices = []
    faces = []
    polygons = []

    with open(filename, 'r') as f:
        line = f.readline()
        assert line.startswith("ply"), "Not a PLY file"
        is_ascii = False
        vertex_count = 0
        face_count = 0

        while line.strip() != "end_header":
            if line.startswith("format ascii"):
                is_ascii = True
            elif line.startswith("element vertex"):
                vertex_count = int(line.split()[-1])
            elif line.startswith("element face"):
                face_count = int(line.split()[-1])
            line = f.readline()

        # Read vertices
        for _ in range(vertex_count):
            parts = f.readline().strip().split()
            x, y, z = map(float, parts[:3])
            vertices.append(Point(x, y, z))

        # Read faces (assume triangle)
        for _ in range(face_count):
            parts = f.readline().strip().split()
            if int(parts[0]) != 3:
                continue  # Skip non-triangular faces
            i1, i2, i3 = map(int, parts[1:4])
            tri = Polygon(
                vertices=[vertices[i1], vertices[i2], vertices[i3]],
                color=color,
                kr=kr,
                kt=kt,
                material=material
            )
            polygons.append(tri)

    return polygons
