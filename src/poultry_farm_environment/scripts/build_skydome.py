#!/usr/bin/env python3
"""
Photorealistic 3D Skydome Generator for Gazebo:
  - Generates 2048x1024 seamless panoramic sky texture with:
      * Realistic atmospheric Rayleigh scattering gradient
      * Radiant glowing Sun positioned to match Gazebo directional light
      * Fluffy cumulus cloud formations with multi-octave fractal noise
      * Seamless 360-degree horizontal wrapping
  - Generates 3D Inward-Facing Hemisphere Mesh (R = 220m, 32 rings x 48 sectors)
  - Generates Model SDF & Config with Emissive PBR Material
"""

import os
import math
import numpy as np
from PIL import Image, ImageFilter

PACKAGE_DIR = "/home/nammy/ros2_ws/src/poultry_farm_world"
MODELS_DIR = os.path.join(PACKAGE_DIR, "models")
MODEL_NAME = "sky_dome_clouds_sun"
MODEL_DIR = os.path.join(MODELS_DIR, MODEL_NAME)
MESHES_DIR = os.path.join(MODEL_DIR, "meshes")
TEXTURES_DIR = os.path.join(MODEL_DIR, "materials", "textures")


def ensure_dir(d):
    os.makedirs(d, exist_ok=True)


def generate_sky_texture(output_path, width=2048, height=1024):
    print(f"--> Generating high-resolution sky texture ({width}x{height})...")
    np.random.seed(42)

    # 1. Base Rayleigh Atmospheric Sky Gradient
    # Vertical coordinates: y=0 (zenith, 90 deg elevation), y=height-1 (horizon, 0 deg elevation)
    # y beyond horizon (below 0 deg) transitions smoothly to ground haze
    y_norm = np.linspace(0.0, 1.0, height, dtype=np.float32)[:, None]
    x_norm = np.linspace(0.0, 1.0, width, dtype=np.float32)[None, :]

    # RGB gradient keypoints along y_norm:
    # 0.00 (Zenith): Deep celestial azure (18, 85, 185)
    # 0.35 (Mid-High): Vibrant sky blue (45, 125, 215)
    # 0.70 (Mid-Low): Azure blue (85, 165, 235)
    # 0.90 (Near horizon): Warm atmospheric haze (165, 205, 245)
    # 1.00 (Horizon): Warm golden-white haze (215, 228, 242)

    sky_r = np.zeros((height, width), dtype=np.float32)
    sky_g = np.zeros((height, width), dtype=np.float32)
    sky_b = np.zeros((height, width), dtype=np.float32)

    # Interpolate gradient
    for y in range(height):
        t = y / (height - 1)
        if t < 0.35:
            f = t / 0.35
            r = 18 * (1 - f) + 45 * f
            g = 85 * (1 - f) + 125 * f
            b = 185 * (1 - f) + 215 * f
        elif t < 0.70:
            f = (t - 0.35) / 0.35
            r = 45 * (1 - f) + 85 * f
            g = 125 * (1 - f) + 165 * f
            b = 215 * (1 - f) + 235 * f
        elif t < 0.90:
            f = (t - 0.70) / 0.20
            r = 85 * (1 - f) + 165 * f
            g = 165 * (1 - f) + 205 * f
            b = 235 * (1 - f) + 245 * f
        else:
            f = (t - 0.90) / 0.10
            r = 165 * (1 - f) + 215 * f
            g = 205 * (1 - f) + 228 * f
            b = 245 * (1 - f) + 242 * f
        sky_r[y, :] = r
        sky_g[y, :] = g
        sky_b[y, :] = b

    # 2. Multi-Octave Seamless Fractal Clouds
    # We generate octaves with horizontal periodic boundary conditions for seamless 360 wrap
    cloud_map = np.zeros((height, width), dtype=np.float32)
    octaves = [
        (4, 2, 0.45),
        (8, 4, 0.30),
        (16, 8, 0.18),
        (32, 16, 0.10),
        (64, 32, 0.05),
    ]

    for ow, oh, weight in octaves:
        # Create random noise with periodic horizontal boundary (tileable in X)
        noise_grid = np.random.uniform(0.0, 1.0, (oh, ow)).astype(np.float32)
        # Pad horizontally by 1 column for seamless wrap
        noise_padded = np.hstack([noise_grid, noise_grid[:, :1]])
        noise_img = Image.fromarray((noise_padded * 255).astype(np.uint8))
        # Upscale to width + (width/ow) then crop to exact width
        upscaled_w = int(width * (ow + 1) / ow)
        noise_upscaled = noise_img.resize((upscaled_w, height), resample=Image.BICUBIC)
        noise_arr = np.array(noise_upscaled, dtype=np.float32)[:, :width] / 255.0
        cloud_map += noise_arr * weight

    # Cloud distribution mask: cumulus clouds gather mostly in mid and lower sky
    # Flat base at t=0.82, peak density around t=0.45 - 0.70, thinner near zenith
    cloud_height_envelope = np.zeros(height, dtype=np.float32)
    for y in range(height):
        t = y / (height - 1)
        if t < 0.20:
            env = (t / 0.20) ** 1.5 * 0.6  # Thin wisps near zenith
        elif t <= 0.78:
            env = 0.6 + 0.4 * math.sin((t - 0.20) / 0.58 * math.pi)  # Puffy cumulus bodies
        elif t <= 0.88:
            env = 1.0 - (t - 0.78) / 0.10  # Crisp flat cloud bottoms
        else:
            env = 0.0
        cloud_height_envelope[y] = env

    cloud_density = (cloud_map - 0.48) / 0.35
    cloud_density = np.clip(cloud_density, 0.0, 1.0)
    cloud_density = (3 * cloud_density**2 - 2 * cloud_density**3)  # Smoothstep
    cloud_density *= cloud_height_envelope[:, None]

    # Cloud shading (bright white tops, soft silver-grey shaded underside)
    # Calculate vertical derivative of cloud density for top-lighting highlight
    grad_y = np.gradient(cloud_density, axis=0)
    sunlit_factor = np.clip(-grad_y * 12.0 + 0.6, 0.2, 1.0)

    # Cloud colors
    cloud_r = 255.0 * sunlit_factor
    cloud_g = 253.0 * sunlit_factor
    cloud_b = (248.0 * sunlit_factor) + (1.0 - sunlit_factor) * 210.0

    # Composite clouds onto sky
    cloud_alpha = np.clip(cloud_density * 1.25, 0.0, 0.95)
    sky_r = sky_r * (1.0 - cloud_alpha) + cloud_r * cloud_alpha
    sky_g = sky_g * (1.0 - cloud_alpha) + cloud_g * cloud_alpha
    sky_b = sky_b * (1.0 - cloud_alpha) + cloud_b * cloud_alpha

    # 3. Radiant Glowing Sun & Atmospheric Corona
    # Direction in Gazebo: direction = 0.4 -0.6 -0.8
    # Sun light source vector = [-0.4, 0.6, 0.8]
    # Azimuth: atan2(0.6, -0.4) = 123.7 deg -> U = 123.7 / 360 = 0.3436 -> X = 704
    # Elevation: atan2(0.8, sqrt(0.4^2 + 0.6^2)) = 48.0 deg -> V = 48.0 / 90.0 = 0.533
    # Y on texture = (1.0 - 48.0 / 90.0) * height = 0.467 * 1024 = 478
    sun_x = int(0.3436 * width)
    sun_y = int(0.4667 * height)

    yy, xx = np.mgrid[:height, :width]
    # Handle wrap-around distance for X
    dx = np.abs(xx - sun_x)
    dx = np.minimum(dx, width - dx)
    dy = yy - sun_y
    dist = np.sqrt(dx**2 + dy**2)

    # Sun components:
    # A. Blinding white disc (radius 32 px)
    disc_mask = np.clip((35.0 - dist) / 5.0, 0.0, 1.0)

    # B. Inner intense solar core glow (radius 110 px)
    inner_glow = np.clip(np.exp(-dist / 45.0) * 1.5, 0.0, 1.0)

    # C. Outer atmospheric corona / halo (radius 450 px)
    outer_halo = np.clip(np.exp(-dist / 140.0) * 0.85, 0.0, 1.0)

    # D. Subtle radiant sun rays
    angle = np.arctan2(dy, dx)
    rays = (0.5 + 0.3 * np.sin(16 * angle) + 0.2 * np.cos(32 * angle))
    rays = np.clip(rays * np.exp(-dist / 220.0) * 0.4, 0.0, 0.6)

    # Apply Sun onto sky
    # Corona color: Warm radiant gold (255, 235, 175)
    sky_r += outer_halo * 160.0 + rays * 120.0
    sky_g += outer_halo * 140.0 + rays * 100.0
    sky_b += outer_halo * 70.0 + rays * 40.0

    # Inner glow: Brilliant pale yellow (255, 250, 210)
    sky_r += inner_glow * 220.0
    sky_g += inner_glow * 210.0
    sky_b += inner_glow * 150.0

    # Disc: Pure brilliant white (255, 255, 255)
    sky_r = sky_r * (1.0 - disc_mask) + 255.0 * disc_mask
    sky_g = sky_g * (1.0 - disc_mask) + 255.0 * disc_mask
    sky_b = sky_b * (1.0 - disc_mask) + 255.0 * disc_mask

    # Final clipping to uint8
    sky_r = np.clip(sky_r, 0, 255).astype(np.uint8)
    sky_g = np.clip(sky_g, 0, 255).astype(np.uint8)
    sky_b = np.clip(sky_b, 0, 255).astype(np.uint8)

    sky_img = Image.fromarray(np.dstack([sky_r, sky_g, sky_b]), mode="RGB")

    # Slight soft Gaussian blur on edges to eliminate high-frequency noise
    # Keep the sun crisp by blending
    sky_img.save(output_path, quality=95)
    print(f"  -> Sky texture saved to: {output_path} (Sun at X={sun_x}, Y={sun_y})")


def generate_skydome_mesh(obj_path, mtl_path, radius=220.0, rings=32, sectors=48):
    print(f"--> Generating 3D Inward-Facing Skydome Mesh (R={radius}m, {rings}x{sectors})...")
    verts = []
    uvs = []
    faces = []

    # Dome covers elevation from theta = -6 degrees (-0.10 rad) up to 90 degrees (+pi/2)
    # The negative theta ensures the sky extends slightly below the ground horizon plane,
    # eliminating any gaps or clipping seams at ground level.
    theta_min = -math.radians(6.0)
    theta_max = math.radians(90.0)

    # Grid of vertices: (rings + 1) rows, (sectors + 1) columns (columns wrap seamlessly)
    for r in range(rings + 1):
        # r = 0 is zenith, r = rings is horizon
        frac_r = r / rings
        theta = theta_max - frac_r * (theta_max - theta_min)
        v_coord = frac_r  # V=0 at zenith (top of texture), V=1 at horizon (bottom)

        cos_t = math.cos(theta)
        sin_t = math.sin(theta)

        for s in range(sectors + 1):
            frac_s = s / sectors
            # Azimuth angle phi from 0 to 2*pi
            phi = frac_s * 2.0 * math.pi
            u_coord = frac_s

            x = radius * cos_t * math.cos(phi)
            y = radius * cos_t * math.sin(phi)
            z = radius * sin_t

            verts.append((x, y, z))
            uvs.append((u_coord, 1.0 - v_coord))

    def vert_idx(r, s):
        return r * (sectors + 1) + s + 1

    # Inward-facing triangles (clockwise winding when viewed from inside)
    # Normal points towards (0, 0, 0)
    for r in range(rings):
        for s in range(sectors):
            v00 = vert_idx(r, s)
            v01 = vert_idx(r, s + 1)
            v10 = vert_idx(r + 1, s)
            v11 = vert_idx(r + 1, s + 1)

            # Inside view: face normals must point INWARD.
            # Triangle 1: (v00, v10, v01)
            faces.append((v00, v10, v01))
            # Triangle 2: (v01, v10, v11)
            faces.append((v01, v10, v11))

    # Write OBJ
    with open(obj_path, "w") as f:
        f.write("# Inward-Facing Skydome Mesh with Clouds & Sun\n")
        f.write("mtllib sky_dome.mtl\n")
        f.write("usemtl sky_material\n")
        for x, y, z in verts:
            f.write(f"v {x:.4f} {y:.4f} {z:.4f}\n")
        for u, v in uvs:
            f.write(f"vt {u:.6f} {v:.6f}\n")
        # Inward normals
        for x, y, z in verts:
            # normalized inward vector
            d = math.sqrt(x*x + y*y + z*z)
            if d > 0:
                nx, ny, nz = -x/d, -y/d, -z/d
            else:
                nx, ny, nz = 0, 0, -1
            f.write(f"vn {nx:.4f} {ny:.4f} {nz:.4f}\n")
        for v1, v2, v3 in faces:
            f.write(f"f {v1}/{v1}/{v1} {v2}/{v2}/{v2} {v3}/{v3}/{v3}\n")

    # Write MTL
    with open(mtl_path, "w") as f:
        f.write("""newmtl sky_material
Ka 1.0 1.0 1.0
Kd 1.0 1.0 1.0
Ks 0.0 0.0 0.0
d 1.0
illum 1
map_Kd ../materials/textures/sky_clouds_sun.png
""")
    print(f"  -> Generated {len(verts)} vertices, {len(faces)} inward faces in {obj_path}")


def build_skydome_model():
    ensure_dir(MESHES_DIR)
    ensure_dir(TEXTURES_DIR)

    tex_path = os.path.join(TEXTURES_DIR, "sky_clouds_sun.png")
    generate_sky_texture(tex_path, width=2048, height=1024)

    obj_path = os.path.join(MESHES_DIR, "sky_dome.obj")
    mtl_path = os.path.join(MESHES_DIR, "sky_dome.mtl")
    generate_skydome_mesh(obj_path, mtl_path, radius=220.0, rings=32, sectors=48)

    # Model SDF
    sdf_path = os.path.join(MODEL_DIR, "model.sdf")
    with open(sdf_path, "w") as f:
        f.write(f"""<?xml version="1.0" ?>
<sdf version="1.8">
  <model name="{MODEL_NAME}">
    <static>true</static>
    <link name="link">
      <visual name="sky_dome_visual">
        <cast_shadows>false</cast_shadows>
        <geometry>
          <mesh>
            <uri>model://{MODEL_NAME}/meshes/sky_dome.obj</uri>
          </mesh>
        </geometry>
        <material>
          <ambient>1.0 1.0 1.0 1.0</ambient>
          <diffuse>1.0 1.0 1.0 1.0</diffuse>
          <specular>0.0 0.0 0.0 1.0</specular>
          <emissive>0.88 0.90 0.95 1.0</emissive>
          <pbr>
            <metal>
              <albedo_map>materials/textures/sky_clouds_sun.png</albedo_map>
              <emissive_map>materials/textures/sky_clouds_sun.png</emissive_map>
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

    # Model Config
    config_path = os.path.join(MODEL_DIR, "model.config")
    with open(config_path, "w") as f:
        f.write(f"""<?xml version="1.0"?>
<model>
  <name>{MODEL_NAME}</name>
  <version>1.0</version>
  <sdf version="1.8">model.sdf</sdf>
  <author><name>Antigravity</name></author>
  <description>Photorealistic 3D Skydome with Natural Clouds and Radiant Sun</description>
</model>
""")

    print(f"--> Successfully created Skydome Model in {MODEL_DIR}")


if __name__ == "__main__":
    build_skydome_model()
