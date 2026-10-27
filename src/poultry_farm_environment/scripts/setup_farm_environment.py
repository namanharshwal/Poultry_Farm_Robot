#!/usr/bin/env python3
"""
Setup script to create:
  1. Local standalone 'pine_tree' and 'oak_tree' models.
  2. Realistic 'farm_worker' models with distinct work apparel and safety gear.
  3. High-fidelity 'farm_fence_section' and 'farm_gate' models.
"""

import os
import shutil
import numpy as np
from PIL import Image, ImageDraw

PACKAGE_DIR = "/home/nammy/ros2_ws/src/poultry_farm_world"
MODELS_DIR = os.path.join(PACKAGE_DIR, "models")
FUEL_CACHE = "/home/nammy/.gz/fuel/fuel.gazebosim.org/openrobotics/models"


def ensure_dir(d):
    os.makedirs(d, exist_ok=True)


# ==============================================================================
# 1. SETUP STANDALONE TREE MODELS (PINE & OAK)
# ==============================================================================

def setup_tree_models():
    print("--> Setting up local standalone Tree models...")
    
    # 1.1 Pine Tree
    src_pine = os.path.join(FUEL_CACHE, "pine tree", "6")
    dst_pine = os.path.join(MODELS_DIR, "pine_tree")
    if os.path.exists(src_pine):
        ensure_dir(dst_pine)
        # Copy meshes, textures, scripts
        for item in ["meshes", "materials"]:
            s = os.path.join(src_pine, item)
            d = os.path.join(dst_pine, item)
            if os.path.exists(s):
                if os.path.exists(d):
                    shutil.rmtree(d)
                shutil.copytree(s, d)
        
        # Write clean local model.sdf
        with open(os.path.join(dst_pine, "model.sdf"), "w") as f:
            f.write("""<?xml version="1.0" ?>
<sdf version="1.7">
  <model name="pine_tree">
    <static>true</static>
    <link name="link">
      <collision name="collision">
        <geometry>
          <mesh>
            <uri>model://pine_tree/meshes/pine_tree.dae</uri>
          </mesh>
        </geometry>
      </collision>
      <visual name="branch">
        <geometry>
          <mesh>
            <uri>model://pine_tree/meshes/pine_tree.dae</uri>
            <submesh><name>Branch</name></submesh>
          </mesh>
        </geometry>
        <material>
          <diffuse>1.0 1.0 1.0 1.0</diffuse>
          <pbr>
            <metal>
              <albedo_map>model://pine_tree/materials/textures/branch_2_diffuse.png</albedo_map>
              <roughness>0.8</roughness>
              <metalness>0.0</metalness>
            </metal>
          </pbr>
        </material>
      </visual>
      <visual name="bark">
        <geometry>
          <mesh>
            <uri>model://pine_tree/meshes/pine_tree.dae</uri>
            <submesh><name>Bark</name></submesh>
          </mesh>
        </geometry>
        <material>
          <diffuse>1.0 1.0 1.0 1.0</diffuse>
          <pbr>
            <metal>
              <albedo_map>model://pine_tree/materials/textures/bark_diffuse.png</albedo_map>
              <roughness>0.85</roughness>
              <metalness>0.0</metalness>
            </metal>
          </pbr>
        </material>
      </visual>
    </link>
  </model>
</sdf>""")
        with open(os.path.join(dst_pine, "model.config"), "w") as f:
            f.write("""<?xml version="1.0"?>
<model><name>pine_tree</name><version>1.0</version><sdf version="1.7">model.sdf</sdf></model>""")
        print("  -> Pine tree model ready.")

    # 1.2 Oak Tree
    src_oak = os.path.join(FUEL_CACHE, "oak tree", "7")
    dst_oak = os.path.join(MODELS_DIR, "oak_tree")
    if os.path.exists(src_oak):
        ensure_dir(dst_oak)
        for item in ["meshes", "materials"]:
            s = os.path.join(src_oak, item)
            d = os.path.join(dst_oak, item)
            if os.path.exists(s):
                if os.path.exists(d):
                    shutil.rmtree(d)
                shutil.copytree(s, d)
        
        with open(os.path.join(dst_oak, "model.sdf"), "w") as f:
            f.write("""<?xml version="1.0" ?>
<sdf version="1.7">
  <model name="oak_tree">
    <static>true</static>
    <link name="link">
      <collision name="collision">
        <geometry>
          <mesh>
            <uri>model://oak_tree/meshes/oak_tree.dae</uri>
          </mesh>
        </geometry>
      </collision>
      <visual name="branch">
        <geometry>
          <mesh>
            <uri>model://oak_tree/meshes/oak_tree.dae</uri>
            <submesh><name>Branch</name></submesh>
          </mesh>
        </geometry>
        <material>
          <diffuse>1.0 1.0 1.0 1.0</diffuse>
          <pbr>
            <metal>
              <albedo_map>model://oak_tree/materials/textures/branch_diffuse.png</albedo_map>
              <roughness>0.75</roughness>
              <metalness>0.0</metalness>
            </metal>
          </pbr>
        </material>
      </visual>
      <visual name="bark">
        <geometry>
          <mesh>
            <uri>model://oak_tree/meshes/oak_tree.dae</uri>
            <submesh><name>Bark</name></submesh>
          </mesh>
        </geometry>
        <material>
          <diffuse>1.0 1.0 1.0 1.0</diffuse>
          <pbr>
            <metal>
              <albedo_map>model://oak_tree/materials/textures/bark_diffuse.png</albedo_map>
              <roughness>0.85</roughness>
              <metalness>0.0</metalness>
            </metal>
          </pbr>
        </material>
      </visual>
    </link>
  </model>
</sdf>""")
        with open(os.path.join(dst_oak, "model.config"), "w") as f:
            f.write("""<?xml version="1.0"?>
<model><name>oak_tree</name><version>1.0</version><sdf version="1.7">model.sdf</sdf></model>""")
        print("  -> Oak tree model ready.")


# ==============================================================================
# 2. SETUP POULTRY FARM WORKER MODELS
# ==============================================================================

def setup_worker_models():
    print("--> Setting up Poultry Farm Worker models...")
    src_person = os.path.join(FUEL_CACHE, "standing person", "3")
    if not os.path.exists(src_person):
        print("  [ERROR] Standing person cache not found!")
        return

    workers = [
        ("farm_worker_supervisor", "High-Visibility Safety Vest & Farm Cap", (255, 120, 0), (30, 80, 160)),
        ("farm_worker_caretaker", "Green Farm Overalls & Field Boots", (40, 110, 50), (60, 90, 60)),
        ("farm_worker_logistics", "Industrial Work Wear & Safety Gear", (220, 180, 20), (50, 50, 60)),
    ]

    for model_name, desc, shirt_color, pants_color in workers:
        model_dir = os.path.join(MODELS_DIR, model_name)
        ensure_dir(model_dir)
        meshes_dst = os.path.join(model_dir, "meshes")
        materials_dst = os.path.join(model_dir, "materials", "textures")
        ensure_dir(meshes_dst)
        ensure_dir(materials_dst)

        # Copy original textures and mesh
        src_tex = os.path.join(src_person, "materials", "textures")
        for f in os.listdir(src_tex):
            shutil.copyfile(os.path.join(src_tex, f), os.path.join(materials_dst, f))

        # Copy DAE mesh
        shutil.copyfile(os.path.join(src_person, "meshes", "standing.dae"), os.path.join(meshes_dst, f"{model_name}.dae"))

        # Modify shirt texture to create distinctive farm work apparel!
        shirt_tex_path = os.path.join(materials_dst, "tshirt02_texture.png")
        if os.path.exists(shirt_tex_path):
            img = Image.open(shirt_tex_path).convert("RGBA")
            arr = np.array(img, dtype=np.float32)
            # Apply color tint while preserving fabric folds/shadows
            r_scale, g_scale, b_scale = shirt_color[0] / 255.0, shirt_color[1] / 255.0, shirt_color[2] / 255.0
            luminance = 0.299 * arr[:, :, 0] + 0.587 * arr[:, :, 1] + 0.114 * arr[:, :, 2]
            arr[:, :, 0] = np.clip(luminance * r_scale * 1.5, 0, 255)
            arr[:, :, 1] = np.clip(luminance * g_scale * 1.5, 0, 255)
            arr[:, :, 2] = np.clip(luminance * b_scale * 1.5, 0, 255)
            
            # Draw reflective safety stripes for supervisor and logistics
            if "supervisor" in model_name or "logistics" in model_name:
                tinted = Image.fromarray(arr.astype(np.uint8))
                d = ImageDraw.Draw(tinted)
                # Horizontal reflective silver band across torso
                h, w = tinted.size[1], tinted.size[0]
                d.rectangle([(int(w * 0.1), int(h * 0.45)), (int(w * 0.9), int(h * 0.52))], fill=(240, 240, 240, 255))
                d.rectangle([(int(w * 0.1), int(h * 0.58)), (int(w * 0.9), int(h * 0.65))], fill=(240, 240, 240, 255))
                tinted.save(shirt_tex_path)
            else:
                Image.fromarray(arr.astype(np.uint8)).save(shirt_tex_path)

        # Write clean local model.sdf
        with open(os.path.join(model_dir, "model.sdf"), "w") as f:
            f.write(f"""<?xml version="1.0" ?>
<sdf version="1.7">
  <model name="{model_name}">
    <static>true</static>
    <link name="link">
      <collision name="collision">
        <pose>0 0 0.90 0 0 0</pose>
        <geometry>
          <cylinder>
            <radius>0.28</radius>
            <length>1.80</length>
          </cylinder>
        </geometry>
      </collision>
      <visual name="visual">
        <pose>0 0 0.02 0.04 0 0</pose>
        <geometry>
          <mesh>
            <uri>model://{model_name}/meshes/{model_name}.dae</uri>
          </mesh>
        </geometry>
      </visual>
    </link>
  </model>
</sdf>""")

        with open(os.path.join(model_dir, "model.config"), "w") as f:
            f.write(f"""<?xml version="1.0"?>
<model><name>{model_name}</name><version>1.0</version><sdf version="1.7">model.sdf</sdf></model>""")

        print(f"  -> {model_name} ready ({desc}).")


# ==============================================================================
# 3. SETUP MODULAR FARM FENCE & SECURITY GATE
# ==============================================================================

def setup_fence_models():
    print("--> Setting up Modular Farm Fencing & Security Gate models...")

    # 3.1 Modular Farm Fence Section (3.0m length)
    fence_dir = os.path.join(MODELS_DIR, "farm_fence_section")
    ensure_dir(fence_dir)
    meshes_dir = os.path.join(fence_dir, "meshes")
    ensure_dir(meshes_dir)

    # 3D OBJ mesh for 3.0m fence panel:
    # 2 round treated timber posts (dia 0.12m, height 1.8m) + top rail + mid rail + wire mesh panel
    obj_path = os.path.join(meshes_dir, "farm_fence_section.obj")
    mtl_path = os.path.join(meshes_dir, "farm_fence_section.mtl")

    verts = []
    faces = []

    def add_v(x, y, z):
        verts.append([x, y, z])
        return len(verts)

    def add_cyl(p1, p2, r, n=10, mtl="wood"):
        p1 = np.array(p1)
        p2 = np.array(p2)
        axis = p2 - p1
        length = np.linalg.norm(axis)
        z_ax = axis / length
        ref = np.array([0, 1, 0]) if abs(z_ax[1]) < 0.9 else np.array([1, 0, 0])
        x_ax = np.cross(ref, z_ax)
        x_ax /= np.linalg.norm(x_ax)
        y_ax = np.cross(z_ax, x_ax)

        r1 = []
        r2 = []
        for j in range(n):
            phi = 2.0 * np.pi * j / n
            cp = np.cos(phi)
            sp = np.sin(phi)
            r1.append(add_v(*(p1 + r * (cp * x_ax + sp * y_ax))))
            r2.append(add_v(*(p2 + r * (cp * x_ax + sp * y_ax))))

        for j in range(n):
            nj = (j + 1) % n
            faces.append((r1[j], r1[nj], r2[nj], mtl))
            faces.append((r1[j], r2[nj], r2[j], mtl))

    # Left post at X = -1.5, Right post at X = +1.5
    add_cyl([-1.5, 0, 0.0], [-1.5, 0, 1.80], 0.065, n=12, mtl="post_wood")
    add_cyl([ 1.5, 0, 0.0], [ 1.5, 0, 1.80], 0.065, n=12, mtl="post_wood")

    # Top horizontal rail (Z = 1.60m)
    add_cyl([-1.5, 0, 1.60], [1.5, 0, 1.60], 0.045, n=10, mtl="rail_wood")
    # Middle horizontal rail (Z = 0.85m)
    add_cyl([-1.5, 0, 0.85], [1.5, 0, 0.85], 0.045, n=10, mtl="rail_wood")
    # Bottom kick rail (Z = 0.15m)
    add_cyl([-1.5, 0, 0.15], [1.5, 0, 0.15], 0.045, n=10, mtl="rail_wood")

    # Wire mesh panel (2-sided box between -1.45 and +1.45, Z = 0.10 to 1.65)
    # 4 vertices per side
    w1 = add_v(-1.45, -0.005, 0.12)
    w2 = add_v( 1.45, -0.005, 0.12)
    w3 = add_v( 1.45, -0.005, 1.62)
    w4 = add_v(-1.45, -0.005, 1.62)
    faces.append((w1, w2, w3, "wire_mesh"))
    faces.append((w1, w3, w4, "wire_mesh"))

    w5 = add_v(-1.45, 0.005, 0.12)
    w6 = add_v( 1.45, 0.005, 0.12)
    w7 = add_v( 1.45, 0.005, 1.62)
    w8 = add_v(-1.45, 0.005, 1.62)
    faces.append((w6, w5, w8, "wire_mesh"))
    faces.append((w6, w8, w7, "wire_mesh"))

    # Write OBJ
    with open(obj_path, "w") as f:
        f.write("mtllib farm_fence_section.mtl\n")
        for v in verts:
            f.write(f"v {v[0]:.4f} {v[1]:.4f} {v[2]:.4f}\n")
        
        cur = None
        for p1, p2, p3, m in faces:
            if m != cur:
                f.write(f"usemtl {m}\n")
                cur = m
            f.write(f"f {p1} {p2} {p3}\n")

    # Write MTL
    with open(mtl_path, "w") as f:
        f.write("""newmtl post_wood
Ka 0.45 0.32 0.20
Kd 0.55 0.40 0.26
Ks 0.08 0.08 0.08
Ns 10.0

newmtl rail_wood
Ka 0.52 0.38 0.24
Kd 0.62 0.46 0.30
Ks 0.10 0.10 0.10
Ns 12.0

newmtl wire_mesh
Ka 0.70 0.72 0.75
Kd 0.75 0.78 0.82
Ks 0.30 0.30 0.30
Ns 35.0
""")

    with open(os.path.join(fence_dir, "model.sdf"), "w") as f:
        f.write("""<?xml version="1.0" ?>
<sdf version="1.8">
  <model name="farm_fence_section">
    <static>true</static>
    <link name="link">
      <visual name="visual">
        <geometry>
          <mesh>
            <uri>model://farm_fence_section/meshes/farm_fence_section.obj</uri>
          </mesh>
        </geometry>
      </visual>
      <collision name="collision">
        <pose>0 0 0.90 0 0 0</pose>
        <geometry>
          <box><size>3.0 0.14 1.80</size></box>
        </geometry>
      </collision>
    </link>
  </model>
</sdf>""")

    with open(os.path.join(fence_dir, "model.config"), "w") as f:
        f.write("""<?xml version="1.0"?>
<model><name>farm_fence_section</name><version>1.0</version><sdf version="1.8">model.sdf</sdf></model>""")
    print("  -> Farm fence section ready.")

    # 3.2 Security Farm Gate Model
    gate_dir = os.path.join(MODELS_DIR, "farm_gate")
    ensure_dir(gate_dir)
    gate_mesh_dir = os.path.join(gate_dir, "meshes")
    ensure_dir(gate_mesh_dir)

    # Double leaf steel tubular farm gate (span 6.0m, height 1.6m)
    g_obj = os.path.join(gate_mesh_dir, "farm_gate.obj")
    g_mtl = os.path.join(gate_mesh_dir, "farm_gate.mtl")
    g_verts = []
    g_faces = []

    def add_gv(x, y, z):
        g_verts.append([x, y, z])
        return len(g_verts)

    def add_gcyl(p1, p2, r, n=8, mtl="gate_steel"):
        p1 = np.array(p1)
        p2 = np.array(p2)
        axis = p2 - p1
        length = np.linalg.norm(axis)
        z_ax = axis / length
        ref = np.array([0, 1, 0]) if abs(z_ax[1]) < 0.9 else np.array([1, 0, 0])
        x_ax = np.cross(ref, z_ax)
        x_ax /= np.linalg.norm(x_ax)
        y_ax = np.cross(z_ax, x_ax)
        r1, r2 = [], []
        for j in range(n):
            phi = 2.0 * np.pi * j / n
            r1.append(add_gv(*(p1 + r * (np.cos(phi) * x_ax + np.sin(phi) * y_ax))))
            r2.append(add_gv(*(p2 + r * (np.cos(phi) * x_ax + np.sin(phi) * y_ax))))
        for j in range(n):
            nj = (j + 1) % n
            g_faces.append((r1[j], r1[nj], r2[nj], mtl))
            g_faces.append((r1[j], r2[nj], r2[j], mtl))

    # Massive Gate Posts (dia 0.20m, height 2.2m) at X = -3.0 and X = +3.0
    add_gcyl([-3.0, 0, 0], [-3.0, 0, 2.2], 0.10, n=12, mtl="gate_post")
    add_gcyl([ 3.0, 0, 0], [ 3.0, 0, 2.2], 0.10, n=12, mtl="gate_post")

    # Left Leaf (-3.0 to -0.05)
    for zh in [0.20, 0.55, 0.90, 1.25, 1.60]:
        add_gcyl([-2.9, 0, zh], [-0.05, 0, zh], 0.030, n=8, mtl="gate_steel")
    add_gcyl([-2.9, 0, 0.15], [-2.9, 0, 1.65], 0.035, n=8, mtl="gate_steel")
    add_gcyl([-0.05, 0, 0.15], [-0.05, 0, 1.65], 0.035, n=8, mtl="gate_steel")
    # Diagonal brace
    add_gcyl([-2.9, 0, 0.20], [-0.05, 0, 1.60], 0.025, n=8, mtl="gate_steel")

    # Right Leaf (+0.05 to +2.9)
    for zh in [0.20, 0.55, 0.90, 1.25, 1.60]:
        add_gcyl([0.05, 0, zh], [2.9, 0, zh], 0.030, n=8, mtl="gate_steel")
    add_gcyl([0.05, 0, 0.15], [0.05, 0, 1.65], 0.035, n=8, mtl="gate_steel")
    add_gcyl([2.9, 0, 0.15], [2.9, 0, 1.65], 0.035, n=8, mtl="gate_steel")
    # Diagonal brace
    add_gcyl([2.9, 0, 0.20], [0.05, 0, 1.60], 0.025, n=8, mtl="gate_steel")

    # Biosecurity warning sign on right leaf (0.60m x 0.40m at X = 1.4, Z = 1.1)
    s1 = add_gv(1.10, -0.04, 0.90)
    s2 = add_gv(1.70, -0.04, 0.90)
    s3 = add_gv(1.70, -0.04, 1.30)
    s4 = add_gv(1.10, -0.04, 1.30)
    g_faces.append((s1, s2, s3, "bio_sign"))
    g_faces.append((s1, s3, s4, "bio_sign"))

    with open(g_obj, "w") as f:
        f.write("mtllib farm_gate.mtl\n")
        for v in g_verts:
            f.write(f"v {v[0]:.4f} {v[1]:.4f} {v[2]:.4f}\n")
        cur = None
        for p1, p2, p3, m in g_faces:
            if m != cur:
                f.write(f"usemtl {m}\n")
                cur = m
            f.write(f"f {p1} {p2} {p3}\n")

    with open(g_mtl, "w") as f:
        f.write("""newmtl gate_post
Ka 0.40 0.42 0.45
Kd 0.50 0.52 0.55
Ks 0.20 0.20 0.20
Ns 20.0

newmtl gate_steel
Ka 0.75 0.20 0.15
Kd 0.85 0.25 0.20
Ks 0.40 0.40 0.40
Ns 30.0

newmtl bio_sign
Ka 0.90 0.85 0.10
Kd 0.95 0.90 0.15
Ks 0.20 0.20 0.20
Ns 15.0
""")

    with open(os.path.join(gate_dir, "model.sdf"), "w") as f:
        f.write("""<?xml version="1.0" ?>
<sdf version="1.8">
  <model name="farm_gate">
    <static>true</static>
    <link name="link">
      <visual name="visual">
        <geometry><mesh><uri>model://farm_gate/meshes/farm_gate.obj</uri></mesh></geometry>
      </visual>
      <collision name="collision">
        <pose>0 0 1.0 0 0 0</pose>
        <geometry><box><size>6.2 0.25 2.0</size></box></geometry>
      </collision>
    </link>
  </model>
</sdf>""")

    with open(os.path.join(gate_dir, "model.config"), "w") as f:
        f.write("""<?xml version="1.0"?>
<model><name>farm_gate</name><version>1.0</version><sdf version="1.8">model.sdf</sdf></model>""")
    print("  -> Farm gate ready.")


if __name__ == "__main__":
    setup_tree_models()
    setup_worker_models()
    setup_fence_models()
    print("\n--> All farm environment models initialized successfully!")
