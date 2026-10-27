#!/usr/bin/env python3
"""
Builder for Radiant Sun Model in Gazebo:
  - Generates high-resolution RGBA solar textures (solar disc, corona halo, sunburst diffraction rays)
  - Builds 3D solar billboard mesh facing the poultry farm complex
  - Configures emissive PBR materials for brilliant self-illumination in Ogre2
"""

import os
import math
import numpy as np
from PIL import Image

PACKAGE_DIR = "/home/nammy/ros2_ws/src/poultry_farm_world"
MODEL_NAME = "sun_radiant"
MODEL_DIR = os.path.join(PACKAGE_DIR, "models", MODEL_NAME)
MESHES_DIR = os.path.join(MODEL_DIR, "meshes")
TEXTURES_DIR = os.path.join(MODEL_DIR, "materials", "textures")


def ensure_dir(d):
    os.makedirs(d, exist_ok=True)


def generate_sun_texture():
    ensure_dir(TEXTURES_DIR)
    tex_path = os.path.join(TEXTURES_DIR, "sun_radiant.png")
    print(f"--> Generating high-res radiant sun texture (1024x1024)...")

    size = 1024
    center = size / 2.0
    yy, xx = np.mgrid[:size, :size]
    dx = xx - center
    dy = yy - center
    dist = np.sqrt(dx**2 + dy**2)
    angle = np.arctan2(dy, dx)

    # 1. Blinding pure white core disc (radius 85 px)
    core = np.clip((95.0 - dist) / 14.0, 0.0, 1.0)

    # 2. Intense golden solar limb (radius 200 px)
    limb = np.clip(np.exp(-dist / 75.0) * 1.6, 0.0, 1.0)

    # 3. Radiant atmospheric corona (radius 420 px)
    corona = np.clip(np.exp(-dist / 160.0) * 1.0, 0.0, 1.0)

    # 4. Solar flare and halo (radius 620 px)
    halo = np.clip(np.exp(-dist / 280.0) * 0.7, 0.0, 1.0)

    # 5. Radiant diffraction spikes / rays (32 rays with harmonic modulation)
    rays = (0.5 + 0.35 * np.sin(24 * angle) + 0.15 * np.cos(48 * angle))
    rays = np.clip(rays * np.exp(-dist / 240.0) * 0.85, 0.0, 0.85)

    # Composite RGB: Brilliant golden sunlight
    r = 255.0 * np.ones_like(dist)
    g = corona * 242.0 + halo * 220.0 + rays * 238.0 + limb * 252.0
    b = corona * 170.0 + halo * 130.0 + rays * 165.0 + limb * 225.0

    # Core is pure blinding white
    r = r * (1.0 - core) + 255.0 * core
    g = g * (1.0 - core) + 255.0 * core
    b = b * (1.0 - core) + 255.0 * core

    # Alpha channel: smooth natural falloff to 0 at perimeter
    alpha = np.clip(core * 1.0 + limb * 0.98 + corona * 0.92 + rays * 0.88 + halo * 0.75, 0.0, 1.0)
    # Edge fadeout to zero
    edge_fade = np.clip((495.0 - dist) / 50.0, 0.0, 1.0)
    alpha *= edge_fade

    rgba = np.dstack([
        np.clip(r, 0, 255).astype(np.uint8),
        np.clip(g, 0, 255).astype(np.uint8),
        np.clip(b, 0, 255).astype(np.uint8),
        np.clip(alpha * 255.0, 0, 255).astype(np.uint8)
    ])

    img = Image.fromarray(rgba, mode="RGBA")
    img.save(tex_path, format="PNG")
    print(f"  -> Saved radiant sun texture: {tex_path}")
    return tex_path


def generate_sun_mesh():
    ensure_dir(MESHES_DIR)
    obj_path = os.path.join(MESHES_DIR, "sun_radiant.obj")
    mtl_path = os.path.join(MESHES_DIR, "sun_radiant.mtl")
    print("--> Generating 3D sun billboard mesh...")

    # Billboard size: 56 meters across (grand, majestic cinematic solar presence at 86m)
    radius = 28.0
    segments = 32

    # Vector from Sun (-32, 54, 64) to Farm Center (0, 6, 0) is (+32, -48, -64)
    # Unit normal vector pointing towards farm center:
    N = np.array([32.0, -48.0, -64.0], dtype=np.float32)
    N /= np.linalg.norm(N)

    # Construct orthogonal basis (U, V) perpendicular to N
    up = np.array([0.0, 0.0, 1.0], dtype=np.float32)
    U = np.cross(up, N)
    U /= np.linalg.norm(U)
    V = np.cross(N, U)

    verts = []
    uvs = []
    normals = []
    faces = []

    # Center vertex
    verts.append([0.0, 0.0, 0.0])
    uvs.append([0.5, 0.5])
    normals.append([N[0], N[1], N[2]])

    # Rim vertices
    for i in range(segments):
        th = 2.0 * math.pi * i / segments
        pos = (U * math.cos(th) + V * math.sin(th)) * radius
        u = 0.5 + 0.5 * math.cos(th)
        v = 0.5 + 0.5 * math.sin(th)
        verts.append([pos[0], pos[1], pos[2]])
        uvs.append([u, v])
        normals.append([N[0], N[1], N[2]])

    # Triangles: fan from center (vertex 1)
    # Front-facing counter-clockwise winding when viewed along -N (from the farm looking at the sun)
    for i in range(segments):
        v1 = 1
        v2 = 2 + i
        v3 = 2 + ((i + 1) % segments)
        faces.append((v1, v2, v3))

    with open(obj_path, "w") as f:
        f.write("# Radiant Sun Billboard Mesh\n")
        f.write("mtllib sun_radiant.mtl\n")
        f.write("usemtl sun_material\n")
        for vx, vy, vz in verts:
            f.write(f"v {vx:.4f} {vy:.4f} {vz:.4f}\n")
        for u, v in uvs:
            f.write(f"vt {u:.6f} {v:.6f}\n")
        for nx, ny, nz in normals:
            f.write(f"vn {nx:.4f} {ny:.4f} {nz:.4f}\n")
        for fa, fb, fc in faces:
            f.write(f"f {fa}/{fa}/{fa} {fb}/{fb}/{fa} {fc}/{fc}/{fa}\n")

    with open(mtl_path, "w") as f:
        f.write("""newmtl sun_material
Ka 1.0 1.0 1.0
Kd 1.0 1.0 1.0
Ks 0.0 0.0 0.0
d 1.0
illum 1
map_Kd ../materials/textures/sun_radiant.png
""")

    print(f"  -> Generated sun billboard mesh: {obj_path} ({len(verts)} verts, {len(faces)} faces)")


def generate_sun_sdf():
    sdf_path = os.path.join(MODEL_DIR, "model.sdf")
    config_path = os.path.join(MODEL_DIR, "model.config")

    with open(sdf_path, "w") as f:
        f.write(f"""<?xml version="1.0" ?>
<sdf version="1.8">
  <model name="{MODEL_NAME}">
    <static>true</static>
    <link name="link">
      <visual name="sun_visual">
        <cast_shadows>false</cast_shadows>
        <geometry>
          <mesh>
            <uri>model://{MODEL_NAME}/meshes/sun_radiant.obj</uri>
          </mesh>
        </geometry>
        <material>
          <ambient>1.0 1.0 1.0 1.0</ambient>
          <diffuse>1.0 1.0 1.0 1.0</diffuse>
          <specular>0.0 0.0 0.0 1.0</specular>
          <emissive>1.0 1.0 1.0 1.0</emissive>
          <double_sided>true</double_sided>
          <pbr>
            <metal>
              <albedo_map>model://{MODEL_NAME}/materials/textures/sun_radiant.png</albedo_map>
              <emissive_map>model://{MODEL_NAME}/materials/textures/sun_radiant.png</emissive_map>
              <roughness>1.0</roughness>
              <metalness>0.0</metalness>
            </metal>
          </pbr>
        </material>
      </visual>
    </link>
  </model>
</sdf>
""")

    with open(config_path, "w") as f:
        f.write(f"""<?xml version="1.0"?>
<model>
  <name>{MODEL_NAME}</name>
  <version>1.0</version>
  <sdf version="1.8">model.sdf</sdf>
  <author><name>Antigravity</name></author>
  <description>Radiant Glowing Sun with Golden Corona and Solar Rays</description>
</model>
""")
    print(f"  -> Generated model.sdf & model.config in {MODEL_DIR}")


def build_sun_model():
    print(f"--> Building Radiant Sun Model ({MODEL_NAME})...")
    generate_sun_texture()
    generate_sun_mesh()
    generate_sun_sdf()
    print(f"--> {MODEL_NAME} built successfully!")


if __name__ == "__main__":
    build_sun_model()
