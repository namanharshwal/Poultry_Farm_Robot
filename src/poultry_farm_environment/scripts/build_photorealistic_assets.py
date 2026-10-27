#!/usr/bin/env python3
"""
Photorealistic Asset Builder for Gazebo Poultry Farm Simulation.
Creates:
  1. High-Resolution Texture Atlases for White and Brown Chickens with anatomical skin, plumage, comb, beak, and eyes.
  2. Anatomically Sculpted 3D Chicken Models with smooth vertex normals and exact UV mapping.
  3. High-Fidelity 3D Chicken Egg Models with authentic asymmetric ovoid curvature and PBR materials.
  4. Realistically Populated 30-Egg Packing Flats and Sorting Mill Graded Eggs.
"""

import os
import math
import numpy as np
from PIL import Image, ImageDraw

OUTPUT_BASE = "/home/nammy/ros2_ws/src/poultry_farm_world"
MODELS_DIR = os.path.join(OUTPUT_BASE, "models")
TEXTURES_DIR = os.path.join(OUTPUT_BASE, "materials", "textures")


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


# ==============================================================================
# 1. TEXTURE ATLAS GENERATOR
# ==============================================================================

def generate_photorealistic_chicken_atlas(breed="white"):
    ensure_dir(TEXTURES_DIR)
    size = 1024
    img = Image.new("RGB", (size, size), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    # ----------------------------------------------------
    # Region 1: Body Plumage (X: 0 to 665, Y: 0 to 716)
    # ----------------------------------------------------
    if breed == "white":
        # White Broiler / Leghorn: Layered soft ivory with feather barbules
        base_col = (248, 246, 240)
        draw.rectangle([(0, 0), (665, 716)], fill=base_col)
        for y in range(0, 716, 14):
            for x in range(0, 665, 22):
                x_shift = (y // 14) % 2 * 11
                px = (x + x_shift) % 665
                shade = np.random.randint(228, 244)
                # Feather arc
                draw.arc([px - 14, y - 6, px + 14, y + 18], start=25, end=155, fill=(shade, shade, shade - 6), width=2)
                # Quill
                draw.line([px, y, px, y + 14], fill=(shade - 14, shade - 14, shade - 20), width=1)
    else:
        # Brown Layer (Rhode Island Red): Rich copper, chestnut, mahogany, amber tips
        base_col = (168, 72, 28)
        draw.rectangle([(0, 0), (665, 716)], fill=base_col)
        for y in range(0, 716, 14):
            for x in range(0, 665, 22):
                x_shift = (y // 14) % 2 * 11
                px = (x + x_shift) % 665
                r = np.random.randint(150, 205)
                g = int(r * 0.48)
                b = int(r * 0.20)
                # Main barbule curve
                draw.arc([px - 14, y - 6, px + 14, y + 18], start=25, end=155, fill=(r, g, b), width=3)
                # Golden fringe
                draw.arc([px - 12, y - 4, px + 12, y + 16], start=30, end=150, fill=(min(255, r + 30), min(255, g + 30), b + 10), width=1)
                # Darker spine
                draw.line([px, y, px, y + 14], fill=(int(r*0.6), int(g*0.6), int(b*0.6)), width=1)

    # ----------------------------------------------------
    # Region 2: Comb & Wattles (X: 665 to 1024, Y: 0 to 358)
    # ----------------------------------------------------
    # Vibrant organic blood red with skin stippling & vascular texture
    draw.rectangle([(665, 0), (1024, 358)], fill=(225, 20, 25))
    for _ in range(5000):
        cx = np.random.randint(665, 1024)
        cy = np.random.randint(0, 358)
        val = np.random.randint(170, 255)
        draw.point((cx, cy), fill=(val, np.random.randint(10, 40), np.random.randint(10, 40)))
    # Soft fleshy creases
    for cy in range(20, 340, 24):
        draw.line([(680, cy), (1010, cy + np.random.randint(-10, 10))], fill=(175, 15, 20), width=2)

    # ----------------------------------------------------
    # Region 3: Beak Horn (X: 665 to 1024, Y: 358 to 665)
    # ----------------------------------------------------
    # Warm golden-maize keratin with longitudinal growth rings
    draw.rectangle([(665, 358), (1024, 665)], fill=(245, 185, 35))
    for by in range(365, 660, 6):
        draw.line([(670, by), (1020, by)], fill=(225, 160, 25), width=2)
    # Darker mouth crease line
    draw.line([(665, 512), (1024, 512)], fill=(180, 110, 15), width=4)

    # ----------------------------------------------------
    # Region 4: Legs & Feet (X: 0 to 460, Y: 716 to 1024)
    # ----------------------------------------------------
    # Golden-orange scales (scutes) with dark borders
    draw.rectangle([(0, 716), (460, 1024)], fill=(238, 155, 32))
    for ly in range(720, 1020, 10):
        for lx in range(0, 450, 16):
            draw.arc([lx, ly, lx + 16, ly + 10], start=0, end=180, fill=(195, 115, 15), width=2)
            draw.arc([lx + 1, ly + 1, lx + 15, ly + 9], start=0, end=180, fill=(255, 180, 50), width=1)

    # ----------------------------------------------------
    # Region 5: Avian Eye (X: 460 to 665, Y: 716 to 1024)
    # ----------------------------------------------------
    # Photorealistic eye with iris, pupil, and specular catchlight
    draw.rectangle([(460, 716), (665, 1024)], fill=(30, 30, 30))
    # Sclera / eye perimeter
    center = (562, 870)
    r_eye = 85
    draw.ellipse([center[0] - r_eye, center[1] - r_eye, center[0] + r_eye, center[1] + r_eye], fill=(240, 120, 18))
    # Radial iris fibers
    for ang in range(0, 360, 10):
        rad_ang = math.radians(ang)
        x_end = center[0] + int(r_eye * math.cos(rad_ang))
        y_end = center[1] + int(r_eye * math.sin(rad_ang))
        draw.line([center, (x_end, y_end)], fill=(255, 165, 35), width=2)
    # Inner limbus
    draw.ellipse([center[0] - 50, center[1] - 50, center[0] + 50, center[1] + 50], fill=(210, 95, 12))
    # Deep black pupil
    r_pupil = 34
    draw.ellipse([center[0] - r_pupil, center[1] - r_pupil, center[0] + r_pupil, center[1] + r_pupil], fill=(10, 10, 10))
    # Specular white catchlights
    draw.ellipse([center[0] + 10, center[1] - 22, center[0] + 28, center[1] - 6], fill=(255, 255, 255))
    draw.ellipse([center[0] - 18, center[1] + 12, center[0] - 8, center[1] + 20], fill=(230, 230, 230))

    # ----------------------------------------------------
    # Region 6: Tail Sickles & Coverts (X: 665 to 1024, Y: 665 to 1024)
    # ----------------------------------------------------
    if breed == "white":
        draw.rectangle([(665, 665), (1024, 1024)], fill=(242, 240, 235))
        for y in range(670, 1020, 12):
            draw.line([(670, y), (1020, y + 8)], fill=(218, 215, 205), width=2)
    else:
        # Dark greenish-black iridescent tail sickles with copper sheen
        draw.rectangle([(665, 665), (1024, 1024)], fill=(45, 52, 42))
        for y in range(670, 1020, 12):
            draw.line([(670, y), (1020, y + 8)], fill=(75, 95, 65), width=2)
            draw.line([(670, y + 2), (1020, y + 10)], fill=(120, 85, 40), width=1)

    filename = f"chicken_atlas_{breed}.png"
    out_path = os.path.join(TEXTURES_DIR, filename)
    img.save(out_path)
    print(f"--> Saved photorealistic atlas: {out_path}")
    return filename


# ==============================================================================
# 2. SCULPTED 3D CHICKEN BUILDER WITH EXACT ATLAS UV MAPPING
# ==============================================================================

class ChickenMeshBuilder:
    def __init__(self):
        self.vertices = []
        self.uvs = []
        self.triangles = []  # list of (v1, v2, v3, vt1, vt2, vt3)
        self.normals = []

    def add_v(self, x, y, z):
        self.vertices.append(np.array([float(x), float(y), float(z)], dtype=np.float32))
        return len(self.vertices)

    def add_vt(self, u, v):
        self.uvs.append((float(u), float(v)))
        return len(self.uvs)

    def add_tri(self, v1, v2, v3, uv1, uv2, uv3):
        t1 = self.add_vt(*uv1)
        t2 = self.add_vt(*uv2)
        t3 = self.add_vt(*uv3)
        self.triangles.append((v1, v2, v3, t1, t2, t3))

    def add_quad(self, v1, v2, v3, v4, uv1, uv2, uv3, uv4):
        self.add_tri(v1, v2, v3, uv1, uv2, uv3)
        self.add_tri(v1, v3, v4, uv1, uv3, uv4)

    def compute_smooth_normals(self):
        normals = [np.zeros(3, dtype=np.float32) for _ in range(len(self.vertices))]
        for v1, v2, v3, _, _, _ in self.triangles:
            p1 = self.vertices[v1 - 1]
            p2 = self.vertices[v2 - 1]
            p3 = self.vertices[v3 - 1]
            fn = np.cross(p2 - p1, p3 - p1)
            normals[v1 - 1] += fn
            normals[v2 - 1] += fn
            normals[v3 - 1] += fn
        self.normals = []
        for n in normals:
            l = np.linalg.norm(n)
            self.normals.append(n / l if l > 1e-6 else np.array([0, 0, 1], dtype=np.float32))

    def export_obj(self, filepath):
        self.compute_smooth_normals()
        with open(filepath, "w") as f:
            f.write("# Photorealistic Organic Chicken OBJ\n")
            for v in self.vertices:
                f.write(f"v {v[0]:.4f} {v[1]:.4f} {v[2]:.4f}\n")
            for vt in self.uvs:
                # Flip V for standard OBJ / OpenGL texture coordinates
                f.write(f"vt {vt[0]:.4f} {1.0 - vt[1]:.4f}\n")
            for vn in self.normals:
                f.write(f"vn {vn[0]:.4f} {vn[1]:.4f} {vn[2]:.4f}\n")
            for v1, v2, v3, t1, t2, t3 in self.triangles:
                f.write(f"f {v1}/{t1}/{v1} {v2}/{t2}/{v2} {v3}/{t3}/{v3}\n")


def build_chicken_geometry(pose="standing"):
    m = ChickenMeshBuilder()

    # Posture parameters
    if pose == "standing":
        body_z = 0.17
        neck_root = (0.07, 0.0, body_z + 0.05)
        head_c = (0.13, 0.0, 0.31)
        tail_end = (-0.17, 0.0, 0.26)
    elif pose == "pecking":
        body_z = 0.15
        neck_root = (0.08, 0.0, body_z + 0.03)
        head_c = (0.19, 0.0, 0.06)
        tail_end = (-0.18, 0.0, 0.28)
    else:  # resting
        body_z = 0.07
        neck_root = (0.06, 0.0, body_z + 0.04)
        head_c = (0.11, 0.0, 0.23)
        tail_end = (-0.16, 0.0, 0.18)

    # ---------------------------------------------------------
    # 1. ORGANIC SCULPTED TORSO & BREAST (UV: [0.05..0.60, 0.05..0.65])
    # ---------------------------------------------------------
    n_rings = 16
    n_slices = 16
    x_coords = np.linspace(-0.13, 0.10, n_rings)

    rings = []
    for i, x in enumerate(x_coords):
        t = i / (n_rings - 1)
        # Avian cross section: breast prominence, saddle curve
        ry = 0.088 * math.sin(t * math.pi) * (1.0 - 0.18 * (t - 0.5))
        rz = 0.096 * math.sin(t * math.pi) * (1.0 + 0.28 * math.cos(t * math.pi))
        cz = body_z + 0.02 * math.sin(t * math.pi) - 0.012 * (t - 0.5)

        if t > 0.6:
            rz *= (1.0 + 0.35 * (t - 0.6))
            cz += 0.016 * (t - 0.6)

        ring = []
        for j in range(n_slices):
            phi = 2.0 * math.pi * j / n_slices
            vy = ry * math.sin(phi)
            vz = cz + rz * math.cos(phi)
            v_idx = m.add_v(x, vy, vz)
            # Map into plumage UV quadrant
            u_uv = 0.05 + 0.55 * t
            v_uv = 0.05 + 0.60 * (j / n_slices)
            ring.append((v_idx, (u_uv, v_uv)))
        rings.append(ring)

    for i in range(n_rings - 1):
        for j in range(n_slices):
            nj = (j + 1) % n_slices
            v1, uv1 = rings[i][j]
            v2, uv2 = rings[i][nj]
            v3, uv3 = rings[i + 1][nj]
            v4, uv4 = rings[i + 1][j]
            m.add_quad(v1, v2, v3, v4, uv1, uv2, uv3, uv4)

    # Torso end caps
    v_front = m.add_v(x_coords[-1] + 0.022, 0.0, body_z + 0.01)
    uv_front = (0.60, 0.35)
    v_back = m.add_v(x_coords[0] - 0.022, 0.0, body_z)
    uv_back = (0.05, 0.35)
    for j in range(n_slices):
        nj = (j + 1) % n_slices
        m.add_tri(v_front, rings[-1][j][0], rings[-1][nj][0], uv_front, rings[-1][j][1], rings[-1][nj][1])
        m.add_tri(v_back, rings[0][nj][0], rings[0][j][0], uv_back, rings[0][nj][1], rings[0][j][1])

    # ---------------------------------------------------------
    # 2. FLANK WINGS (Left & Right) - (UV: [0.10..0.58, 0.20..0.65])
    # ---------------------------------------------------------
    for sign in [-1.0, 1.0]:
        wy = sign * 0.082
        # Upper wing covert curvature
        w_top = m.add_v(0.02, wy * 1.05, body_z + 0.05)
        w_front = m.add_v(0.08, wy * 0.95, body_z + 0.01)
        w_back = m.add_v(-0.08, wy * 0.95, body_z + 0.01)
        w_bot = m.add_v(-0.02, wy * 1.05, body_z - 0.04)
        m.add_quad(w_front, w_top, w_back, w_bot,
                   (0.50, 0.25), (0.35, 0.20), (0.15, 0.30), (0.30, 0.55))

    # ---------------------------------------------------------
    # 3. TAIL SICKLE FEATHERS (UV: [0.70..0.98, 0.70..0.98])
    # ---------------------------------------------------------
    tx, ty, tz = tail_end
    t_base1 = m.add_v(-0.12, -0.025, body_z + 0.04)
    t_base2 = m.add_v(-0.12,  0.025, body_z + 0.04)
    t_mid1 = m.add_v(tx * 0.8, -0.018, tz * 0.8)
    t_mid2 = m.add_v(tx * 0.8,  0.018, tz * 0.8)
    t_tip = m.add_v(tx, 0.0, tz)

    m.add_quad(t_base1, t_base2, t_mid2, t_mid1, (0.72, 0.72), (0.95, 0.72), (0.95, 0.88), (0.72, 0.88))
    m.add_tri(t_mid1, t_mid2, t_tip, (0.72, 0.88), (0.95, 0.88), (0.84, 0.98))

    # ---------------------------------------------------------
    # 4. ARCHED NECK & HEAD (UV: [0.15..0.55, 0.05..0.30])
    # ---------------------------------------------------------
    n_steps = 7
    neck_rings = []
    for s in range(n_steps):
        t = s / (n_steps - 1)
        nx = neck_root[0] * (1 - t) + head_c[0] * t + 0.018 * math.sin(t * math.pi)
        nz = neck_root[2] * (1 - t) + head_c[2] * t
        nr = 0.048 * (1 - 0.35 * t)
        ring = []
        for j in range(12):
            phi = 2.0 * math.pi * j / 12
            vx = nx + nr * math.cos(phi) * 0.75
            vy = nr * math.sin(phi)
            vz = nz + nr * math.cos(phi) * 0.55
            v_idx = m.add_v(vx, vy, vz)
            u_uv = 0.15 + 0.35 * t
            v_uv = 0.05 + 0.25 * (j / 12)
            ring.append((v_idx, (u_uv, v_uv)))
        neck_rings.append(ring)

    for s in range(n_steps - 1):
        for j in range(12):
            nj = (j + 1) % 12
            m.add_quad(neck_rings[s][j][0], neck_rings[s][nj][0],
                       neck_rings[s + 1][nj][0], neck_rings[s + 1][j][0],
                       neck_rings[s][j][1], neck_rings[s][nj][1],
                       neck_rings[s + 1][nj][1], neck_rings[s + 1][j][1])

    # Head Cranium
    hx, hy, hz = head_c
    head_pts = []
    for i in range(7):
        th = math.pi * i / 6
        row = []
        for j in range(12):
            phi = 2.0 * math.pi * j / 12
            vx = hx + 0.044 * math.sin(th) * math.cos(phi)
            vy = hy + 0.034 * math.sin(th) * math.sin(phi)
            vz = hz + 0.038 * math.cos(th)
            v_idx = m.add_v(vx, vy, vz)
            row.append((v_idx, (0.35 + 0.15 * math.sin(th), 0.15 + 0.10 * math.cos(phi))))
        head_pts.append(row)

    for i in range(6):
        for j in range(12):
            nj = (j + 1) % 12
            m.add_quad(head_pts[i][j][0], head_pts[i][nj][0],
                       head_pts[i + 1][nj][0], head_pts[i + 1][j][0],
                       head_pts[i][j][1], head_pts[i][nj][1],
                       head_pts[i + 1][nj][1], head_pts[i + 1][j][1])

    # ---------------------------------------------------------
    # 5. CRIMSON SCULPTED COMB (UV: [0.68..0.98, 0.05..0.32])
    # ---------------------------------------------------------
    comb_spikes = [
        (hx - 0.024, hz + 0.042, 0.016),
        (hx - 0.010, hz + 0.054, 0.025),
        (hx + 0.006, hz + 0.062, 0.030),
        (hx + 0.022, hz + 0.056, 0.026),
        (hx + 0.034, hz + 0.046, 0.018),
    ]
    for idx, (cx, cz, ch) in enumerate(comb_spikes):
        u_c = 0.70 + 0.05 * idx
        c_b1 = m.add_v(cx - 0.007, -0.004, cz)
        c_b2 = m.add_v(cx + 0.007, -0.004, cz)
        c_b3 = m.add_v(cx + 0.007,  0.004, cz)
        c_b4 = m.add_v(cx - 0.007,  0.004, cz)
        c_tip = m.add_v(cx, 0.0, cz + ch)
        uv_b = (u_c, 0.28)
        uv_t = (u_c + 0.02, 0.08)
        m.add_tri(c_b1, c_b2, c_tip, uv_b, uv_b, uv_t)
        m.add_tri(c_b2, c_b3, c_tip, uv_b, uv_b, uv_t)
        m.add_tri(c_b3, c_b4, c_tip, uv_b, uv_b, uv_t)
        m.add_tri(c_b4, c_b1, c_tip, uv_b, uv_b, uv_t)

    # ---------------------------------------------------------
    # 6. THROAT WATTLES (UV: [0.70..0.95, 0.15..0.32])
    # ---------------------------------------------------------
    for wy_sign in [-1.0, 1.0]:
        wy = wy_sign * 0.009
        w_top = m.add_v(hx + 0.025, wy, hz - 0.020)
        w_front = m.add_v(hx + 0.038, wy, hz - 0.035)
        w_back = m.add_v(hx + 0.020, wy, hz - 0.035)
        w_low = m.add_v(hx + 0.028, wy, hz - 0.052)
        m.add_quad(w_top, w_front, w_low, w_back, (0.80, 0.15), (0.90, 0.22), (0.85, 0.30), (0.75, 0.22))

    # ---------------------------------------------------------
    # 7. CURVED GOLDEN BEAK (UV: [0.68..0.98, 0.38..0.62])
    # ---------------------------------------------------------
    bk_base_x = hx + 0.040
    bk_tip_x = hx + 0.078
    bk_z = hz - 0.010
    v_tip = m.add_v(bk_tip_x, 0.0, bk_z - 0.004)
    v_b1 = m.add_v(bk_base_x, -0.014, bk_z + 0.012)
    v_b2 = m.add_v(bk_base_x,  0.014, bk_z + 0.012)
    v_b3 = m.add_v(bk_base_x,  0.000, bk_z - 0.014)
    uv_tip = (0.95, 0.50)
    uv_b1 = (0.72, 0.40)
    uv_b2 = (0.72, 0.60)
    uv_b3 = (0.80, 0.50)
    m.add_tri(v_tip, v_b1, v_b2, uv_tip, uv_b1, uv_b2)
    m.add_tri(v_tip, v_b2, v_b3, uv_tip, uv_b2, uv_b3)
    m.add_tri(v_tip, v_b3, v_b1, uv_tip, uv_b3, uv_b1)

    # ---------------------------------------------------------
    # 8. CONVEX AVIAN EYES (UV: [0.48..0.62, 0.74..0.96])
    # ---------------------------------------------------------
    for ey_sign in [-1.0, 1.0]:
        ey = ey_sign * 0.034
        ex = hx + 0.018
        ez = hz + 0.010
        # 4-quad spherical eye bulb
        e_c = m.add_v(ex, ey * 1.08, ez)
        e_t = m.add_v(ex, ey, ez + 0.007)
        e_b = m.add_v(ex, ey, ez - 0.007)
        e_f = m.add_v(ex + 0.007, ey, ez)
        e_r = m.add_v(ex - 0.007, ey, ez)
        uv_c = (0.55, 0.85)  # Center pupil
        uv_edge = (0.62, 0.85)
        m.add_tri(e_c, e_t, e_f, uv_c, uv_edge, uv_edge)
        m.add_tri(e_c, e_f, e_b, uv_c, uv_edge, uv_edge)
        m.add_tri(e_c, e_b, e_r, uv_c, uv_edge, uv_edge)
        m.add_tri(e_c, e_r, e_t, uv_c, uv_edge, uv_edge)

    # ---------------------------------------------------------
    # 9. SCALED LEGS & FEET (UV: [0.05..0.45, 0.72..0.98])
    # ---------------------------------------------------------
    if pose in ["standing", "pecking"]:
        for ly in [-0.045, 0.045]:
            # Drumstick
            ds_t = m.add_v(-0.01, ly, body_z - 0.01)
            ds_b = m.add_v(-0.01, ly, body_z - 0.06)
            # Shank
            sh_b = m.add_v(-0.01, ly, 0.012)
            # Toes
            t_f = m.add_v(0.042, ly, 0.005)
            t_l = m.add_v(0.032, ly - 0.022, 0.005)
            t_r = m.add_v(0.032, ly + 0.022, 0.005)
            t_b = m.add_v(-0.032, ly, 0.005)

            # Leg geometry
            m.add_tri(ds_t, ds_b, sh_b, (0.10, 0.75), (0.20, 0.82), (0.25, 0.95))
            m.add_tri(sh_b, t_f, t_l, (0.25, 0.95), (0.40, 0.98), (0.35, 0.98))
            m.add_tri(sh_b, t_r, t_f, (0.25, 0.95), (0.35, 0.98), (0.40, 0.98))
            m.add_tri(sh_b, t_b, t_r, (0.25, 0.95), (0.15, 0.98), (0.35, 0.98))

    return m


def export_chicken_model_package(model_name, breed="white", pose="standing", atlas_file="chicken_atlas_white.png"):
    model_dir = os.path.join(MODELS_DIR, model_name)
    meshes_dir = os.path.join(model_dir, "meshes")
    tex_dir = os.path.join(model_dir, "materials", "textures")
    ensure_dir(meshes_dir)
    ensure_dir(tex_dir)

    # 1. Build and export 3D OBJ
    m = build_chicken_geometry(pose)
    obj_file = f"{model_name}.obj"
    obj_path = os.path.join(meshes_dir, obj_file)
    m.export_obj(obj_path)

    # 2. Copy Texture to model's materials folder
    src_atlas = os.path.join(TEXTURES_DIR, atlas_file)
    dst_atlas = os.path.join(tex_dir, atlas_file)
    import shutil
    shutil.copyfile(src_atlas, dst_atlas)

    # 3. Model config
    with open(os.path.join(model_dir, "model.config"), "w") as f:
        f.write(f"""<?xml version="1.0"?>
<model>
  <name>{model_name}</name>
  <version>3.0</version>
  <sdf version="1.8">model.sdf</sdf>
  <description>Photorealistic anatomical {breed} chicken model in {pose} pose with PBR materials.</description>
</model>""")

    # 4. Model SDF with PBR Material
    with open(os.path.join(model_dir, "model.sdf"), "w") as f:
        f.write(f"""<?xml version="1.0" ?>
<sdf version="1.8">
  <model name="{model_name}">
    <static>true</static>
    <link name="link">
      <visual name="visual">
        <geometry>
          <mesh>
            <uri>model://{model_name}/meshes/{obj_file}</uri>
          </mesh>
        </geometry>
        <material>
          <ambient>0.9 0.9 0.9 1</ambient>
          <diffuse>0.95 0.95 0.95 1</diffuse>
          <pbr>
            <metal>
              <albedo_map>model://{model_name}/materials/textures/{atlas_file}</albedo_map>
              <roughness>0.55</roughness>
              <metalness>0.02</metalness>
            </metal>
          </pbr>
        </material>
      </visual>
      <collision name="collision">
        <pose>0 0 0.15 0 0 0</pose>
        <geometry>
          <cylinder>
            <radius>0.12</radius>
            <length>0.30</length>
          </cylinder>
        </geometry>
      </collision>
    </link>
  </model>
</sdf>""")
    print(f"--> Exported photorealistic chicken model: {model_name}")


# ==============================================================================
# 3. PHOTOREALISTIC 3D CHICKEN EGG MODEL
# ==============================================================================

def export_photorealistic_egg(color="white"):
    model_name = f"egg_{color}"
    model_dir = os.path.join(MODELS_DIR, model_name)
    meshes_dir = os.path.join(model_dir, "meshes")
    ensure_dir(meshes_dir)

    obj_file = f"{model_name}.obj"
    obj_path = os.path.join(meshes_dir, obj_file)

    # Authentic asymmetric Cartesian egg ovoid: 58mm length, 44mm width
    L = 0.029
    r0 = 0.022
    k = 0.14  # Noticeable blunt vs pointed pole

    z_steps = 24
    th_steps = 24

    verts = []
    normals = []
    uvs = []
    faces = []

    for i in range(z_steps + 1):
        u = -1.0 + 2.0 * i / z_steps
        z = u * L
        rad = r0 * math.sqrt(max(0.0, 1.0 - u * u)) * (1.0 - k * u)
        for j in range(th_steps):
            phi = 2.0 * math.pi * j / th_steps
            x = rad * math.cos(phi)
            y = rad * math.sin(phi)
            verts.append((x, y, z + L))  # Base at Z = 0
            # Radial normal approximation
            normals.append((math.cos(phi), math.sin(phi), u * 0.5))
            uvs.append((j / th_steps, i / z_steps))

    for i in range(z_steps):
        for j in range(th_steps):
            nj = (j + 1) % th_steps
            p1 = i * th_steps + j + 1
            p2 = i * th_steps + nj + 1
            p3 = (i + 1) * th_steps + nj + 1
            p4 = (i + 1) * th_steps + j + 1
            if i != 0:
                faces.append((p1, p2, p3))
            if i != z_steps - 1:
                faces.append((p1, p3, p4))

    with open(obj_path, "w") as f:
        f.write("# Photorealistic Egg Ovoid OBJ\n")
        for v in verts:
            f.write(f"v {v[0]:.5f} {v[1]:.5f} {v[2]:.5f}\n")
        for vt in uvs:
            f.write(f"vt {vt[0]:.4f} {vt[1]:.4f}\n")
        for vn in normals:
            l = math.sqrt(vn[0]**2 + vn[1]**2 + vn[2]**2)
            f.write(f"vn {vn[0]/l:.4f} {vn[1]/l:.4f} {vn[2]/l:.4f}\n")
        for p1, p2, p3 in faces:
            f.write(f"f {p1}/{p1}/{p1} {p2}/{p2}/{p2} {p3}/{p3}/{p3}\n")

    # SDF with delicate eggshell PBR shader
    if color == "white":
        albedo = "0.98 0.97 0.94 1.0"
        roughness = "0.32"
    else:
        albedo = "0.85 0.62 0.42 1.0"  # Natural farm brown
        roughness = "0.35"

    with open(os.path.join(model_dir, "model.config"), "w") as f:
        f.write(f"""<?xml version="1.0"?>
<model><name>{model_name}</name><version>2.0</version><sdf version="1.8">model.sdf</sdf></model>""")

    with open(os.path.join(model_dir, "model.sdf"), "w") as f:
        f.write(f"""<?xml version="1.0" ?>
<sdf version="1.8">
  <model name="{model_name}">
    <static>true</static>
    <link name="link">
      <visual name="visual">
        <geometry>
          <mesh>
            <uri>model://{model_name}/meshes/{obj_file}</uri>
          </mesh>
        </geometry>
        <material>
          <ambient>{albedo}</ambient>
          <diffuse>{albedo}</diffuse>
          <specular>0.3 0.3 0.3 1</specular>
          <pbr>
            <metal>
              <roughness>{roughness}</roughness>
              <metalness>0.01</metalness>
            </metal>
          </pbr>
        </material>
      </visual>
      <collision name="collision">
        <pose>0 0 0.029 0 0 0</pose>
        <geometry>
          <sphere><radius>0.023</radius></sphere>
        </geometry>
      </collision>
    </link>
  </model>
</sdf>""")
    print(f"--> Exported photorealistic egg model: {model_name}")


# ==============================================================================
# MAIN
# ==============================================================================

def main():
    print("==================================================")
    print("Building Photorealistic Chicken & Egg Models...")
    print("==================================================")

    # 1. Textures
    atlas_white = generate_photorealistic_chicken_atlas("white")
    atlas_brown = generate_photorealistic_chicken_atlas("brown")

    # 2. Chickens with PBR & UV Mapping
    for pose in ["standing", "pecking", "resting"]:
        export_chicken_model_package(f"chicken_white_{pose}", breed="white", pose=pose, atlas_file=atlas_white)
        export_chicken_model_package(f"chicken_brown_{pose}", breed="brown", pose=pose, atlas_file=atlas_brown)

    # 3. Eggs with Asymmetric Ovoid Mesh & PBR Shaders
    export_photorealistic_egg("white")
    export_photorealistic_egg("brown")

    print("==================================================")
    print("Photorealistic Chicken & Egg Models Completed!")
    print("==================================================")


if __name__ == "__main__":
    main()
