#!/usr/bin/env python3
"""
Comprehensive Farm Decorations Builder:
  1. Front Entrance Gate with Grand Roman Named Signboard ("GOLDEN VALLEY POULTRY FARM").
  2. Complete Perimeter Farm Fencing enclosing the farm complex with gate opening.
  3. Poultry Farm Worker Models with authentic farm apparel.
  4. Local Standalone Tree Models (Pine & Oak).
"""

import os
import shutil
import numpy as np
from PIL import Image, ImageDraw, ImageFont

PACKAGE_DIR = "/home/nammy/ros2_ws/src/poultry_farm_world"
MODELS_DIR = os.path.join(PACKAGE_DIR, "models")
TEXTURES_DIR = os.path.join(PACKAGE_DIR, "materials", "textures")
FUEL_CACHE = "/home/nammy/.gz/fuel/fuel.gazebosim.org/openrobotics/models"


def ensure_dir(d):
    os.makedirs(d, exist_ok=True)


# ==============================================================================
# 1. GRAND ENTRANCE GATE WITH ROMAN NAMED SIGNBOARD
# ==============================================================================

def build_entrance_gate():
    print("--> Building Grand Entrance Gate with Roman Named Signboard...")
    model_name = "farm_entrance_gate"
    model_dir = os.path.join(MODELS_DIR, model_name)
    meshes_dir = os.path.join(model_dir, "meshes")
    mat_dir = os.path.join(model_dir, "materials", "textures")
    ensure_dir(meshes_dir)
    ensure_dir(mat_dir)

    # 1.1 Generate High-Resolution Roman Serif Signboard Texture (2048x512)
    tex_path = os.path.join(mat_dir, "poultry_farm_sign_roman.png")
    font_path = "/usr/share/fonts/truetype/liberation2/LiberationSerif-Bold.ttf"
    if not os.path.exists(font_path):
        font_path = "/usr/share/fonts/truetype/freefont/FreeSerifBold.ttf"

    W, H = 2048, 512
    img = Image.new("RGB", (W, H), color=(22, 34, 25))  # Deep heritage British racing green / dark oak
    draw = ImageDraw.Draw(img)

    # Ornamental gilded border
    draw.rectangle([(18, 18), (W - 18, H - 18)], outline=(218, 175, 55), width=10)
    draw.rectangle([(36, 36), (W - 36, H - 36)], outline=(175, 135, 38), width=4)
    # Corner ornamental flourishes
    for cx, cy in [(46, 46), (W - 46, 46), (46, H - 46), (W - 46, H - 46)]:
        draw.ellipse([cx - 16, cy - 16, cx + 16, cy + 16], fill=(218, 175, 55))

    font_title = ImageFont.truetype(font_path, 160)
    title_text = "POULTRY FARM"

    # Embossed 3D gold effect for Roman title text (centered vertically and horizontally)
    tx, ty = W // 2, H // 2
    # Cast shadow
    draw.text((tx + 6, ty + 6), title_text, font=font_title, fill=(8, 12, 8), anchor="mm")
    # Base dark gold
    draw.text((tx + 3, ty + 3), title_text, font=font_title, fill=(160, 110, 20), anchor="mm")
    # Brilliant radiant gold lettering
    draw.text((tx, ty), title_text, font=font_title, fill=(255, 226, 95), anchor="mm")

    img.save(tex_path)
    # Also copy to shared textures
    shutil.copyfile(tex_path, os.path.join(TEXTURES_DIR, "poultry_farm_sign_roman.png"))
    print(f"  -> Saved Roman signboard texture: {tex_path}")

    # 1.2 Build 3D Mesh for Grand Entrance Gate (OBJ + MTL)
    # Features:
    #   - 2 Masonry stone pillars (Y = ±3.2m, height 3.8m, width 0.70m x 0.70m)
    #   - Heavy overhead timber lintel beam (span 6.4m, Z = 3.2m to 3.5m)
    #   - Grand Roman Signboard (span 5.2m, height 0.9m, Z = 3.5m to 4.4m, double-sided with UV mapping)
    #   - Double-leaf steel tubular gates (Y = -3.0 to 0 and 0 to +3.0, Z = 0 to 1.6m)
    obj_path = os.path.join(meshes_dir, "farm_entrance_gate.obj")
    mtl_path = os.path.join(meshes_dir, "farm_entrance_gate.mtl")

    verts = []
    uvs = []
    normals = []
    faces = []

    def add_v(x, y, z):
        verts.append([float(x), float(y), float(z)])
        return len(verts)

    def add_vt(u, v):
        uvs.append([float(u), float(v)])
        return len(uvs)

    def add_box(cx, cy, cz, dx, dy, dz, mtl="stone"):
        hx, hy, hz = dx / 2, dy / 2, dz / 2
        p = [
            add_v(cx - hx, cy - hy, cz - hz), add_v(cx + hx, cy - hy, cz - hz),
            add_v(cx + hx, cy + hy, cz - hz), add_v(cx - hx, cy + hy, cz - hz),
            add_v(cx - hx, cy - hy, cz + hz), add_v(cx + hx, cy - hy, cz + hz),
            add_v(cx + hx, cy + hy, cz + hz), add_v(cx - hx, cy + hy, cz + hz),
        ]
        t = add_vt(0, 0)
        box_quads = [
            (p[0], p[1], p[2], p[3]),  # Bottom
            (p[4], p[7], p[6], p[5]),  # Top
            (p[0], p[4], p[5], p[1]),  # Front (-Y)
            (p[2], p[6], p[7], p[3]),  # Back (+Y)
            (p[0], p[3], p[7], p[4]),  # Left (-X)
            (p[1], p[5], p[6], p[2]),  # Right (+X)
        ]
        for q in box_quads:
            faces.append((q[0], q[1], q[2], t, t, t, mtl))
            faces.append((q[0], q[2], q[3], t, t, t, mtl))

    def add_cyl(p1, p2, r, n=10, mtl="gate_steel"):
        p1 = np.array(p1, dtype=np.float64)
        p2 = np.array(p2, dtype=np.float64)
        axis = p2 - p1
        length = np.linalg.norm(axis)
        if length < 1e-6:
            return
        z_ax = axis / length
        ref = np.array([0, 1, 0]) if abs(z_ax[1]) < 0.9 else np.array([1, 0, 0])
        x_ax = np.cross(ref, z_ax)
        x_ax /= np.linalg.norm(x_ax)
        y_ax = np.cross(z_ax, x_ax)

        r1, r2 = [], []
        t = add_vt(0, 0)
        for j in range(n):
            phi = 2.0 * np.pi * j / n
            r1.append(add_v(*(p1 + r * (np.cos(phi) * x_ax + np.sin(phi) * y_ax))))
            r2.append(add_v(*(p2 + r * (np.cos(phi) * x_ax + np.sin(phi) * y_ax))))
        for j in range(n):
            nj = (j + 1) % n
            faces.append((r1[j], r1[nj], r2[nj], t, t, t, mtl))
            faces.append((r1[j], r2[nj], r2[j], t, t, t, mtl))

    # Masonry stone pillars
    add_box(0, -3.2, 1.9, 0.70, 0.70, 3.8, mtl="stone_pillar")
    add_box(0,  3.2, 1.9, 0.70, 0.70, 3.8, mtl="stone_pillar")
    # Pillar caps
    add_box(0, -3.2, 3.85, 0.85, 0.85, 0.15, mtl="stone_cap")
    add_box(0,  3.2, 3.85, 0.85, 0.85, 0.15, mtl="stone_cap")

    # Overhead timber archway beam (spanning between pillars)
    add_box(0, 0, 3.35, 0.35, 6.40, 0.30, mtl="timber_beam")
    # Top crown beam
    add_box(0, 0, 4.45, 0.30, 5.60, 0.18, mtl="timber_beam")
    # Vertical side support posts for the board
    add_box(0, -2.6, 3.90, 0.25, 0.20, 0.90, mtl="timber_beam")
    add_box(0,  2.6, 3.90, 0.25, 0.20, 0.90, mtl="timber_beam")

    # The Grand Signboard (Double-Sided with UV Coordinates for Roman Text)
    # Span: Y in [-2.5, +2.5] (5.0m wide), Z in [3.55, 4.35] (0.80m tall), thickness: X in [-0.06, +0.06]
    # Texture UV coordinates:
    #   (0.0, 1.0) = Top-Left ("P" in POULTRY, top edge in Gazebo Sim)
    #   (1.0, 1.0) = Top-Right ("M" in FARM, top edge in Gazebo Sim)
    #   (1.0, 0.0) = Bottom-Right ("M" in FARM, bottom edge in Gazebo Sim)
    #   (0.0, 0.0) = Bottom-Left ("P" in POULTRY, bottom edge in Gazebo Sim)
    vt_lt = add_vt(0.0, 1.0)
    vt_rt = add_vt(1.0, 1.0)
    vt_rb = add_vt(1.0, 0.0)
    vt_lb = add_vt(0.0, 0.0)

    # West face (-X normal, viewed approaching farm from outside at West looking +X):
    # From observer's perspective (+X view):
    #   Observer Left is +Y (Y = +2.5), Observer Right is -Y (Y = -2.5)
    #   Observer Top is +Z (Z = 4.35), Observer Bottom is -Z (Z = 3.55)
    w_tl = add_v(-0.06,  2.5, 4.35)  # Top-Left
    w_tr = add_v(-0.06, -2.5, 4.35)  # Top-Right
    w_br = add_v(-0.06, -2.5, 3.55)  # Bottom-Right
    w_bl = add_v(-0.06,  2.5, 3.55)  # Bottom-Left

    # West Face Triangles (Normal: -X)
    faces.append((w_tl, w_bl, w_br, vt_lt, vt_lb, vt_rb, "roman_signboard"))
    faces.append((w_tl, w_br, w_tr, vt_lt, vt_rb, vt_rt, "roman_signboard"))

    # East face (+X normal, viewed leaving farm from inside at East looking -X):
    # From observer's perspective (-X view):
    #   Observer Left is -Y (Y = -2.5), Observer Right is +Y (Y = +2.5)
    #   Observer Top is +Z (Z = 4.35), Observer Bottom is -Z (Z = 3.55)
    e_tl = add_v(0.06, -2.5, 4.35)  # Top-Left
    e_tr = add_v(0.06,  2.5, 4.35)  # Top-Right
    e_br = add_v(0.06,  2.5, 3.55)  # Bottom-Right
    e_bl = add_v(0.06, -2.5, 3.55)  # Bottom-Left

    # East Face Triangles (Normal: +X)
    faces.append((e_tl, e_bl, e_br, vt_lt, vt_lb, vt_rb, "roman_signboard"))
    faces.append((e_tl, e_br, e_tr, vt_lt, vt_rb, vt_rt, "roman_signboard"))

    # Signboard perimeter border rim
    t_rim = add_vt(0, 0)
    # Top rim (+Z normal)
    faces.append((w_tl, w_tr, e_tl, t_rim, t_rim, t_rim, "timber_beam"))
    faces.append((w_tl, e_tl, e_tr, t_rim, t_rim, t_rim, "timber_beam"))
    # Bottom rim (-Z normal)
    faces.append((w_bl, e_br, e_bl, t_rim, t_rim, t_rim, "timber_beam"))
    faces.append((w_bl, e_bl, w_br, t_rim, t_rim, t_rim, "timber_beam"))
    # North rim (Y = +2.5, +Y normal)
    faces.append((w_tl, e_tr, e_br, t_rim, t_rim, t_rim, "timber_beam"))
    faces.append((w_tl, e_br, w_bl, t_rim, t_rim, t_rim, "timber_beam"))
    # South rim (Y = -2.5, -Y normal)
    faces.append((w_tr, w_br, e_bl, t_rim, t_rim, t_rim, "timber_beam"))
    faces.append((w_tr, e_bl, e_tl, t_rim, t_rim, t_rim, "timber_beam"))

    # Double-Leaf Steel Tubular Vehicle Gates (Z = 0.15 to 1.65m)
    # South Leaf (Y = -2.85 to -0.05)
    for zh in [0.20, 0.55, 0.90, 1.25, 1.60]:
        add_cyl([0, -2.85, zh], [0, -0.05, zh], 0.028, n=8, mtl="gate_steel")
    add_cyl([0, -2.85, 0.15], [0, -2.85, 1.65], 0.035, n=8, mtl="gate_steel")
    add_cyl([0, -0.05, 0.15], [0, -0.05, 1.65], 0.035, n=8, mtl="gate_steel")
    add_cyl([0, -2.85, 0.20], [0, -0.05, 1.60], 0.024, n=8, mtl="gate_steel")

    # North Leaf (Y = +0.05 to +2.85)
    for zh in [0.20, 0.55, 0.90, 1.25, 1.60]:
        add_cyl([0, 0.05, zh], [0, 2.85, zh], 0.028, n=8, mtl="gate_steel")
    add_cyl([0, 0.05, 0.15], [0, 0.05, 1.65], 0.035, n=8, mtl="gate_steel")
    add_cyl([0, 2.85, 0.15], [0, 2.85, 1.65], 0.035, n=8, mtl="gate_steel")
    add_cyl([0, 2.85, 0.20], [0, 0.05, 1.60], 0.024, n=8, mtl="gate_steel")

    # Compute Normals
    norm_dict = [np.zeros(3, dtype=np.float64) for _ in range(len(verts))]
    v_arr = np.array(verts, dtype=np.float64)
    for p1, p2, p3, _, _, _, _ in faces:
        fn = np.cross(v_arr[p2 - 1] - v_arr[p1 - 1], v_arr[p3 - 1] - v_arr[p1 - 1])
        norm_dict[p1 - 1] += fn
        norm_dict[p2 - 1] += fn
        norm_dict[p3 - 1] += fn

    norm_clean = []
    for n in norm_dict:
        l = np.linalg.norm(n)
        norm_clean.append(n / l if l > 1e-6 else np.array([0, 0, 1], dtype=np.float64))

    # Write OBJ
    with open(obj_path, "w") as f:
        f.write("mtllib farm_entrance_gate.mtl\n")
        for v in verts:
            f.write(f"v {v[0]:.4f} {v[1]:.4f} {v[2]:.4f}\n")
        for vt in uvs:
            f.write(f"vt {vt[0]:.4f} {vt[1]:.4f}\n")
        for vn in norm_clean:
            f.write(f"vn {vn[0]:.4f} {vn[1]:.4f} {vn[2]:.4f}\n")

        cur_mtl = None
        for p1, p2, p3, t1, t2, t3, mtl in faces:
            if mtl != cur_mtl:
                f.write(f"usemtl {mtl}\n")
                cur_mtl = mtl
            f.write(f"f {p1}/{t1}/{p1} {p2}/{t2}/{p2} {p3}/{t3}/{p3}\n")

    # Write MTL
    with open(mtl_path, "w") as f:
        f.write(f"""newmtl stone_pillar
Ka 0.60 0.58 0.55
Kd 0.68 0.65 0.62
Ks 0.10 0.10 0.10
Ns 10.0

newmtl stone_cap
Ka 0.70 0.68 0.64
Kd 0.78 0.76 0.72
Ks 0.15 0.15 0.15
Ns 15.0

newmtl timber_beam
Ka 0.35 0.22 0.12
Kd 0.45 0.30 0.18
Ks 0.08 0.08 0.08
Ns 8.0

newmtl gate_steel
Ka 0.75 0.20 0.15
Kd 0.85 0.25 0.20
Ks 0.40 0.40 0.40
Ns 30.0

newmtl roman_signboard
Ka 1.0 1.0 1.0
Kd 1.0 1.0 1.0
Ks 0.35 0.35 0.35
Ns 35.0
map_Kd ../materials/textures/poultry_farm_sign_roman.png
""")

    # Write Model SDF with PBR
    with open(os.path.join(model_dir, "model.sdf"), "w") as f:
        f.write(f"""<?xml version="1.0" ?>
<sdf version="1.8">
  <model name="{model_name}">
    <static>true</static>
    <link name="link">
      <visual name="visual">
        <geometry>
          <mesh>
            <uri>model://{model_name}/meshes/{model_name}.obj</uri>
          </mesh>
        </geometry>
      </visual>
      <collision name="collision_left_pillar">
        <pose>0 -3.2 1.9 0 0 0</pose>
        <geometry><box><size>0.80 0.80 3.8</size></box></geometry>
      </collision>
      <collision name="collision_right_pillar">
        <pose>0 3.2 1.9 0 0 0</pose>
        <geometry><box><size>0.80 0.80 3.8</size></box></geometry>
      </collision>
      <collision name="collision_beam">
        <pose>0 0 3.8 0 0 0</pose>
        <geometry><box><size>0.40 6.4 1.4</size></box></geometry>
      </collision>
    </link>
  </model>
</sdf>""")

    with open(os.path.join(model_dir, "model.config"), "w") as f:
        f.write(f"""<?xml version="1.0"?>
<model><name>{model_name}</name><version>1.0</version><sdf version="1.8">model.sdf</sdf></model>""")

    print(f"  -> Grand Entrance Gate ({model_name}) built successfully!")


# ==============================================================================
# 2. CONTINUOUS PERIMETER FARM FENCE
# ==============================================================================

def build_perimeter_fence():
    print("--> Building Continuous Perimeter Farm Fence with Gate Opening...")
    model_name = "farm_perimeter_fence"
    model_dir = os.path.join(MODELS_DIR, model_name)
    meshes_dir = os.path.join(model_dir, "meshes")
    ensure_dir(meshes_dir)

    # Perimeter definition:
    # Bounding Box: X in [-21.0, +21.0], Y in [-15.0, +27.0]
    # Gate opening on West line (X = -21.0): Y in [4.8, 11.2] (width 6.4m centered at Y = 8.0)
    obj_path = os.path.join(meshes_dir, f"{model_name}.obj")
    mtl_path = os.path.join(meshes_dir, f"{model_name}.mtl")

    verts = []
    normals = []
    faces = []

    def add_v(x, y, z):
        verts.append([float(x), float(y), float(z)])
        return len(verts)

    def add_cyl(p1, p2, r, n=8, mtl="fence_wood"):
        p1 = np.array(p1, dtype=np.float64)
        p2 = np.array(p2, dtype=np.float64)
        axis = p2 - p1
        length = np.linalg.norm(axis)
        if length < 1e-6:
            return
        z_ax = axis / length
        ref = np.array([0, 1, 0]) if abs(z_ax[1]) < 0.9 else np.array([1, 0, 0])
        x_ax = np.cross(ref, z_ax)
        x_ax /= np.linalg.norm(x_ax)
        y_ax = np.cross(z_ax, x_ax)

        r1, r2 = [], []
        for j in range(n):
            phi = 2.0 * np.pi * j / n
            r1.append(add_v(*(p1 + r * (np.cos(phi) * x_ax + np.sin(phi) * y_ax))))
            r2.append(add_v(*(p2 + r * (np.cos(phi) * x_ax + np.sin(phi) * y_ax))))
        for j in range(n):
            nj = (j + 1) % n
            faces.append((r1[j], r1[nj], r2[nj], mtl))
            faces.append((r1[j], r2[nj], r2[j], mtl))

    def add_fence_run(start_pt, end_pt, post_spacing=3.0):
        """Builds a run of farm fence from start_pt to end_pt."""
        p_start = np.array(start_pt, dtype=np.float64)
        p_end = np.array(end_pt, dtype=np.float64)
        vec = p_end - p_start
        total_len = np.linalg.norm(vec)
        dir_vec = vec / total_len
        n_bays = max(1, int(round(total_len / post_spacing)))
        step = total_len / n_bays

        # Normal perpendicular to fence line
        perp_vec = np.array([-dir_vec[1], dir_vec[0], 0])

        for b in range(n_bays):
            p1 = p_start + dir_vec * (b * step)
            p2 = p_start + dir_vec * ((b + 1) * step)

            # Post at p1
            add_cyl([p1[0], p1[1], 0.0], [p1[0], p1[1], 1.80], 0.065, n=8, mtl="fence_post")

            # Rails
            for zh, r_rad in [(1.60, 0.045), (0.85, 0.045), (0.15, 0.045)]:
                add_cyl([p1[0], p1[1], zh], [p2[0], p2[1], zh], r_rad, n=6, mtl="fence_rail")

            # Wire mesh panel (2-sided)
            w1 = add_v(p1[0], p1[1], 0.12)
            w2 = add_v(p2[0], p2[1], 0.12)
            w3 = add_v(p2[0], p2[1], 1.62)
            w4 = add_v(p1[0], p1[1], 1.62)
            faces.append((w1, w2, w3, "fence_mesh"))
            faces.append((w1, w3, w4, "fence_mesh"))
            faces.append((w2, w1, w4, "fence_mesh"))
            faces.append((w2, w4, w3, "fence_mesh"))

        # End post
        add_cyl([p_end[0], p_end[1], 0.0], [p_end[0], p_end[1], 1.80], 0.065, n=8, mtl="fence_post")

    # Perimeter runs:
    # 1. South line (-21, -15) to (+21, -15)
    add_fence_run([-21.0, -15.0], [21.0, -15.0])
    # 2. East line (+21, -15) to (+21, +27)
    add_fence_run([21.0, -15.0], [21.0, 27.0])
    # 3. North line (+21, +27) to (-21, +27)
    add_fence_run([21.0, 27.0], [-21.0, 27.0])
    # 4. West line North (-21, +27) to (-21, +11.2)
    add_fence_run([-21.0, 27.0], [-21.0, 11.2])
    # 5. West line South (-21, +4.8) to (-21, -15.0)
    add_fence_run([-21.0, 4.8], [-21.0, -15.0])

    # Compute Normals
    norm_dict = [np.zeros(3, dtype=np.float64) for _ in range(len(verts))]
    v_arr = np.array(verts, dtype=np.float64)
    for p1, p2, p3, _ in faces:
        fn = np.cross(v_arr[p2 - 1] - v_arr[p1 - 1], v_arr[p3 - 1] - v_arr[p1 - 1])
        norm_dict[p1 - 1] += fn
        norm_dict[p2 - 1] += fn
        norm_dict[p3 - 1] += fn

    norm_clean = []
    for n in norm_dict:
        l = np.linalg.norm(n)
        norm_clean.append(n / l if l > 1e-6 else np.array([0, 0, 1], dtype=np.float64))

    # Write OBJ
    with open(obj_path, "w") as f:
        f.write(f"mtllib {model_name}.mtl\n")
        for v in verts:
            f.write(f"v {v[0]:.4f} {v[1]:.4f} {v[2]:.4f}\n")
        for vn in norm_clean:
            f.write(f"vn {vn[0]:.4f} {vn[1]:.4f} {vn[2]:.4f}\n")

        cur_mtl = None
        for p1, p2, p3, mtl in faces:
            if mtl != cur_mtl:
                f.write(f"usemtl {mtl}\n")
                cur_mtl = mtl
            f.write(f"f {p1}//{p1} {p2}//{p2} {p3}//{p3}\n")

    # Write MTL
    with open(mtl_path, "w") as f:
        f.write("""newmtl fence_post
Ka 0.45 0.32 0.20
Kd 0.55 0.40 0.26
Ks 0.08 0.08 0.08
Ns 10.0

newmtl fence_rail
Ka 0.52 0.38 0.24
Kd 0.62 0.46 0.30
Ks 0.10 0.10 0.10
Ns 12.0

newmtl fence_mesh
Ka 0.68 0.70 0.74
Kd 0.74 0.76 0.80
Ks 0.30 0.30 0.30
Ns 30.0
""")

    # Write Model SDF
    with open(os.path.join(model_dir, "model.sdf"), "w") as f:
        f.write(f"""<?xml version="1.0" ?>
<sdf version="1.8">
  <model name="{model_name}">
    <static>true</static>
    <link name="link">
      <visual name="visual">
        <geometry>
          <mesh>
            <uri>model://{model_name}/meshes/{model_name}.obj</uri>
          </mesh>
        </geometry>
      </visual>
      <collision name="collision_south">
        <pose>0 -15.0 0.90 0 0 0</pose>
        <geometry><box><size>42.0 0.15 1.80</size></box></geometry>
      </collision>
      <collision name="collision_north">
        <pose>0 27.0 0.90 0 0 0</pose>
        <geometry><box><size>42.0 0.15 1.80</size></box></geometry>
      </collision>
      <collision name="collision_east">
        <pose>21.0 6.0 0.90 0 0 0</pose>
        <geometry><box><size>0.15 42.0 1.80</size></box></geometry>
      </collision>
      <collision name="collision_west_s">
        <pose>-21.0 -5.1 0.90 0 0 0</pose>
        <geometry><box><size>0.15 19.8 1.80</size></box></geometry>
      </collision>
      <collision name="collision_west_n">
        <pose>-21.0 19.1 0.90 0 0 0</pose>
        <geometry><box><size>0.15 15.8 1.80</size></box></geometry>
      </collision>
    </link>
  </model>
</sdf>""")

    with open(os.path.join(model_dir, "model.config"), "w") as f:
        f.write(f"""<?xml version="1.0"?>
<model><name>{model_name}</name><version>1.0</version><sdf version="1.8">model.sdf</sdf></model>""")

    print(f"  -> Continuous Perimeter Fence ({model_name}) built successfully!")


if __name__ == "__main__":
    build_entrance_gate()
    build_perimeter_fence()
    from build_sun_radiant import build_sun_model
    build_sun_model()


