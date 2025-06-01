
# Ray Tracer

A simple, object-oriented ray tracer inspired by Whitted (1980s). Rays are spawned from each pixel into the scene, colors and light intensities are stored as floats instead of 0-255 rgb for accurate irradiance calculations, and tone mapping prevents overly bright areas from washing out. A KD-Tree speeds up intersection tests, making it possible to render complex models like the Stanford Bunny in a reasonable time. Overall, this project builds upon traditional rasterization by implementing global illumination techniques.

---

## Features

- **Float‐based Colors**: All RGB and light values use floats, not 0–255, so irradiance is more accurate and physically based.  
- **Whitted‐Style Ray Tracing**: Recursive reflection and refraction with configurable recursion depth.  
- **Anti‐Aliasing**: Optional supersampling per pixel to reduce jagged edges.  
- **Materials & Shading**: Phong and Blinn‐Phong shading models, plus shadow attenuation through transparent objects.  
- **Textures**:  
  - **Procedural**: Checkerboard, Brick, Mandelbrot, Mosaic (in `procedural_textures/`).  
  - **Image‐Based**: Load JPEG/PNG maps (e.g. `image-textures/bumps.jpg`).  
- **Geometry Primitives**: Sphere, Cuboid, Cylinder, Torus, Polygon—all inherit from an abstract `object.py`.  
- **KD‐Tree Acceleration**: Speeds up ray‐object intersection tests (`core/kdTree.py`).  
- **Tone Mapping & HDR Output**: Operators to compress high dynamic range.  

---

## Directory Structure

```

ray-tracer/
├── core/
│   ├── color.py
│   ├── kdTree.py
│   ├── material.py
│   ├── point.py
│   ├── ray.py
│   └── vector.py
│
├── image-textures/
│   └── bumps.jpg
│
├── objects/
│   ├── cuboid.py
│   ├── cylinder.py
│   ├── object.py         # abstract base class
│   ├── polygon.py
│   ├── sphere.py
│   └── torus.py
│
├── procedural\_textures/
│   ├── brickTexture.py
│   ├── checkerboardTexture.py
│   ├── mandelbrotTexture.py
│   └── mosaicTexture.py
│
├── scene/
│   ├── blinnPhongIllumination.py
│   ├── camera.py
│   ├── illuminationModel.py  # abstract base class
│   ├── imageTexture.py
│   ├── phongIllumination.py
│   ├── toneReproduction.py
│   └── world.py
│
├── bunny\_example.py
├── notes.txt
├── ply\_parser.py
├── README.md
└── whitted\_replica\_example.py

````

---

## Getting Started

1. **Clone the repo**  
   ```bash
   git clone https://github.com/valkyrie26/ray-tracer.git
   cd ray-tracer
    ```

2. **Install dependencies**

   ```bash
   pip install numpy pillow
   # (Optional) pip install tqdm
   ```

3. **Run an example**

   ```bash
   python whitted_replica_example.py   # Simple Whitted scene
   python bunny_example.py             # Renders the Stanford Bunny
   ```

4. **Build your own scene**

   * Inherit from `object.py` to add new geometry.
   * Inherit from `illuminationModel.py` to add new shading models and procedural textures.
   * Write a script that sets up `Camera`, `World`, adds objects, lights, and calls `camera.render(world)`. Note that this does not inherently include tone reproduction and will return raw values

---

## Usage Overview

* **Camera** (`scene/camera.py`): Defines the camera, its position and orientation, handles super sampling, spawns rays to render
* **World** (`scene/world.py`): Holds objects, lights, kdtree creation and updation calls, ray tracing core, reflection, transmission, shadow attenuation, Phong BRDF to add roughness
* **Materials** (`core/material.py`): ambient, diffused, specular light and specular exponent used by illumination models.
* **Illumination Models**:

  * **`phongIllumination.py`**: Classic Phong shading.
  * **`blinnPhongIllumination.py`**: Blinn‐Phong variant.
* **Textures**:

  * **Procedural**: Located in `procedural_textures/`, each has `illuminate()` like the shaders do.
  * **Image**: `scene/imageTexture.py` loads images from `image-textures/`.
* **KD‐Tree**: `core/kdTree.py` organizes primitives for fast intersection. Dynamically built as we add objects to scene.

---

## Customization

* **Add a new primitive**:

  1. Subclass `objects/object.py`.
  2. Implement `intersect(ray) → IntersectionInfo or None` and `get_bounds()` for the bounding box.
  3. Create and add the object to `world` with specific traits like reflection or material.
* **Add a new illumination model**:

  1. Subclass `scene/illuminationModel.py`.
  2. Implement `illuminate() → Color`.
  3. Assign it to `illumination_model` when constructing objects.
* **Add a new texture**:

  1. For procedural: put your Python file in `procedural_textures/`, and use it by assigning to `illumination_model` when constructing objects.
  2. For image: place the image in `image-textures/` and insert its path in `scene/imageTexture.py`, and use it by assigning `illumination_model=image` when constructing objects.

---

## Future Improvements

* Photon mapping, path tracing.
* Bump mapping (normal perturbations).
* Disney‐style BRDF.
* Depth of field / motion blur.
* Image‐based lighting (HDR environment maps).
* Parallel rendering (multiprocessing or GPU).
* Simple GUI for real‐time previews.

---

## License

This project is licensed under the **MIT License**

