#!/usr/bin/env python3
"""
Enhanced High-Fidelity Asset Generator for Poultry Farm Simulation.
Generates:
  1. Realistic Organic Chickens with smoothed normals, curved plumage, natural combs, wattles, beaks, and wings.
  2. High-resolution plumage and anatomy textures.
  3. Realistic 3D Eggs (asymmetric ovoid geometry) in white and brown.
  4. 30-Egg Honeycomb Packing Trays and Stacking Crates.
  5. Industrial Egg Separation & Grading Mill with 5-tier elevator infeed, candling hood, washing chamber,
     4-grade sizing chutes, and packing tables.
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
# 1. ENHANCED HIGH-RESOLUTION TEXTURES
# ==============================================================================

def generate_enhanced_textures():
    print("--> Generating high-detail realistic textures...")
    ensure_dir(TEXTURES_DIR)
    size = 1024

    # 1.1 Detailed White Broiler Feather Texture (Layered barbules & soft ambient depth)
    white_img = Image.new("RGB", (size, size), color=(248, 246, 240))
    d_w = ImageDraw.Draw(white_img)
    # Add subtle feather contours
    for y in range(0, size, 16):
        for x in range(0, size, 24):
            x_off = (y // 16) % 2 * 12
            fx = (x + x_off) % size
            # Feather curve
            shade = np.random.randint(228, 242)
            d_w.arc([fx - 14, y - 8, fx + 14, y + 20], start=30, end=150, fill=(shade, shade, shade - 5), width=2)
            # Shaft / quill
            d_w.line([fx, y, fx, y + 16], fill=(shade - 10, shade - 10, shade - 15), width=1)
    white_arr = np.array(white_img, dtype=np.float32)
    noise = np.random.normal(0, 4, white_arr.shape)
    white_arr = np.clip(white_arr + noise, 0, 255).astype(np.uint8)
    Image.fromarray(white_arr).save(os.path.join(TEXTURES_DIR, "feather_white_hd.png"))

    # 1.2 Detailed Brown Layer Hen Feather Texture (Rich chestnut, amber, and mahogany)
    brown_img = Image.new("RGB", (size, size), color=(175, 82, 32))
    d_b = ImageDraw.Draw(brown_img)
    for y in range(0, size, 16):
        for x in range(0, size, 24):
            x_off = (y // 16) % 2 * 12
            fx = (x + x_off) % size
            r = np.random.randint(145, 205)
            g = int(r * 0.48)
            b = int(r * 0.18)
            d_b.arc([fx - 14, y - 8, fx + 14, y + 20], start=30, end=150, fill=(r, g, b), width=3)
            # Gold fringe
            d_b.arc([fx - 12, y - 6, fx + 12, y + 18], start=35, end=145, fill=(r + 25, g + 25, b + 10), width=1)
            # Dark quill
            d_b.line([fx, y, fx, y + 16], fill=(int(r*0.65), int(g*0.65), int(b*0.65)), width=1)
    brown_arr = np.array(brown_img, dtype=np.float32)
    brown_arr = np.clip(brown_arr + np.random.normal(0, 6, brown_arr.shape), 0, 255).astype(np.uint8)
    Image.fromarray(brown_arr).save(os.path.join(TEXTURES_DIR, "feather_brown_hd.png"))

    # 1.3 Chicken Facial Anatomy (Crimson comb, golden horn beak, wattles, scales)
    anat = Image.new("RGB", (512, 512), color=(220, 30, 30))
    d_a = ImageDraw.Draw(anat)
    # Comb skin stippling (Top-Left: 0,0 to 256,256)
    for _ in range(2500):
        px, py = np.random.randint(0, 256), np.random.randint(0, 256)
        c_val = np.random.randint(180, 255)
        d_a.point((px, py), fill=(c_val, np.random.randint(15, 45), np.random.randint(15, 45)))
    # Beak horn (Top-Right: 256,0 to 512,256)
    d_a.rectangle([(256, 0), (512, 256)], fill=(245, 185, 30))
    for by in range(0, 256, 4):
        d_a.line([(256, by), (512, by)], fill=(230, 165, 20), width=1)
    # Scaled Leg & Foot texture (Bottom-Left: 0,256 to 256,512)
    d_a.rectangle([(0, 256), (256, 512)], fill=(235, 155, 35))
    for sy in range(256, 512, 8):
        for sx in range(0, 256, 12):
            d_a.arc([sx, sy, sx + 12, sy + 8], start=0, end=180, fill=(205, 125, 20), width=2)
    # Eyes & details (Bottom-Right: 256,256 to 512,512)
    d_a.rectangle([(256, 256), (512, 512)], fill=(25, 25, 25))
    d_a.ellipse([(320, 320), (448, 448)], fill=(235, 120, 20))  # Orange Iris
    d_a.ellipse([(356, 356), (412, 412)], fill=(10, 10, 10))    # Pupil
    d_a.ellipse([(368, 368), (382, 382)], fill=(255, 255, 255)) # Specular catchlight
    anat.save(os.path.join(TEXTURES_DIR, "chicken_anatomy_hd.png"))

    # 1.4 Eggshell Textures (White and speckled Farm Brown)
    egg_w = Image.new("RGB", (256, 256), color=(252, 250, 245))
    d_ew = ImageDraw.Draw(egg_w)
    for _ in range(400):
        d_ew.point((np.random.randint(0, 256), np.random.randint(0, 256)), fill=(240, 238, 232))
    egg_w.save(os.path.join(TEXTURES_DIR, "eggshell_white.png"))

    egg_b = Image.new("RGB", (256, 256), color=(218, 160, 115))
    d_eb = ImageDraw.Draw(egg_b)
    for _ in range(800):
        bx, by = np.random.randint(0, 256), np.random.randint(0, 256)
        d_eb.point((bx, by), fill=(np.random.randint(160, 195), np.random.randint(110, 140), np.random.randint(70, 95)))
    egg_b.save(os.path.join(TEXTURES_DIR, "eggshell_brown.png"))

    # 1.5 Molded Pulp Egg Carton / Tray Texture
    pulp = Image.new("RGB", (256, 256), color=(195, 185, 170))
    d_p = ImageDraw.Draw(pulp)
    for _ in range(3000):
        d_p.point((np.random.randint(0, 256), np.random.randint(0, 256)),
                  fill=(np.random.randint(170, 215), np.random.randint(160, 205), np.random.randint(145, 190)))
    pulp.save(os.path.join(TEXTURES_DIR, "egg_carton_pulp.png"))

    # 1.6 Stainless Steel Equipment Metal
    ss = Image.new("RGB", (512, 512), color=(225, 228, 232))
    d_ss = ImageDraw.Draw(ss)
    for y in range(0, 512, 2):
        shade = np.random.randint(215, 235)
        d_ss.line([(0, y), (512, y)], fill=(shade, shade + 2, shade + 5), width=1)
    ss.save(os.path.join(TEXTURES_DIR, "stainless_steel.png"))

    print("--> Textures created successfully.")


# ==============================================================================
# 2. SMOOTH 3D OBJ BUILDER WITH VERTEX NORMAL INTERPOLATION
# ==============================================================================

class SmoothObjBuilder:
    def __init__(self):
        self.vertices = []
        self.uvs = []
        self.faces = []  # list of (mtl, [v1, v2, v3], [vt1, vt2, vt3])
        self.vertex_normals = []
        self.current_mtl = "default"

    def set_material(self, mtl):
        self.current_mtl = mtl

    def add_vertex(self, x, y, z):
        self.vertices.append(np.array([float(x), float(y), float(z)], dtype=np.float32))
        return len(self.vertices)

    def add_uv(self, u, v):
        self.uvs.append((float(u), float(v)))
        return len(self.uvs)

    def add_triangle(self, v1, v2, v3, uv1=(0,0), uv2=(1,0), uv3=(0,1)):
        t1 = self.add_uv(*uv1)
        t2 = self.add_uv(*uv2)
        t3 = self.add_uv(*uv3)
        self.faces.append((self.current_mtl, [v1, v2, v3], [t1, t2, t3]))

    def add_quad(self, v1, v2, v3, v4, uv1=(0,0), uv2=(1,0), uv3=(1,1), uv4=(0,1)):
        self.add_triangle(v1, v2, v3, uv1, uv2, uv3)
        self.add_triangle(v1, v3, v4, uv1, uv3, uv4)

    def add_box(self, cx, cy, cz, dx, dy, dz, mtl=None):
        if mtl:
            self.set_material(mtl)
        hx, hy, hz = dx / 2.0, dy / 2.0, dz / 2.0
        v = [
            self.add_vertex(cx - hx, cy - hy, cz - hz),  # 1
            self.add_vertex(cx + hx, cy - hy, cz - hz),  # 2
            self.add_vertex(cx + hx, cy + hy, cz - hz),  # 3
            self.add_vertex(cx - hx, cy + hy, cz - hz),  # 4
            self.add_vertex(cx - hx, cy - hy, cz + hz),  # 5
            self.add_vertex(cx + hx, cy - hy, cz + hz),  # 6
            self.add_vertex(cx + hx, cy + hy, cz + hz),  # 7
            self.add_vertex(cx - hx, cy + hy, cz + hz),  # 8
        ]
        self.add_quad(v[0], v[3], v[2], v[1])  # -Z
        self.add_quad(v[4], v[5], v[6], v[7])  # +Z
        self.add_quad(v[0], v[1], v[5], v[4])  # -Y
        self.add_quad(v[1], v[2], v[6], v[5])  # +X
        self.add_quad(v[2], v[3], v[7], v[6])  # +Y
        self.add_quad(v[3], v[0], v[4], v[7])  # -X

    def add_cylinder(self, cx, cy, z_bottom, z_top, r_bottom, r_top, segments=16, mtl=None, capped=True):
        if mtl:
            self.set_material(mtl)
        bot_ring = []
        top_ring = []
        for i in range(segments):
            th = 2.0 * math.pi * i / segments
            c, s = math.cos(th), math.sin(th)
            bot_ring.append(self.add_vertex(cx + r_bottom * c, cy + r_bottom * s, z_bottom))
            top_ring.append(self.add_vertex(cx + r_top * c, cy + r_top * s, z_top))

        for i in range(segments):
            next_i = (i + 1) % segments
            v1, v2 = bot_ring[i], bot_ring[next_i]
            v3, v4 = top_ring[next_i], top_ring[i]
            u1 = i / segments
            u2 = (i + 1) / segments
            self.add_quad(v1, v2, v3, v4, uv1=(u1, 0), uv2=(u2, 0), uv3=(u2, 1), uv4=(u1, 1))

        if capped:
            if r_bottom > 1e-4:
                b_center = self.add_vertex(cx, cy, z_bottom)
                for i in range(segments):
                    next_i = (i + 1) % segments
                    self.add_triangle(b_center, bot_ring[next_i], bot_ring[i])
            if r_top > 1e-4:
                t_center = self.add_vertex(cx, cy, z_top)
                for i in range(segments):
                    next_i = (i + 1) % segments
                    self.add_triangle(t_center, top_ring[i], top_ring[next_i])

    def compute_smooth_normals(self):
        """Compute area-weighted smooth vertex normals for continuous organic surfaces."""
        normals = [np.zeros(3, dtype=np.float32) for _ in range(len(self.vertices))]
        for mtl, v_indices, vt_indices in self.faces:
            p1 = self.vertices[v_indices[0] - 1]
            p2 = self.vertices[v_indices[1] - 1]
            p3 = self.vertices[v_indices[2] - 1]
            fn = np.cross(p2 - p1, p3 - p1)
            normals[v_indices[0] - 1] += fn
            normals[v_indices[1] - 1] += fn
            normals[v_indices[2] - 1] += fn

        self.vertex_normals = []
        for n in normals:
            norm = np.linalg.norm(n)
            if norm > 1e-6:
                self.vertex_normals.append(n / norm)
            else:
                self.vertex_normals.append(np.array([0.0, 0.0, 1.0], dtype=np.float32))

    def save(self, filepath, mtl_lib_name=None):
        self.compute_smooth_normals()
        with open(filepath, "w") as f:
            f.write("# High-Fidelity Organic 3D OBJ with Smooth Normals\n")
            if mtl_lib_name:
                f.write(f"mtllib {mtl_lib_name}\n")
            for v in self.vertices:
                f.write(f"v {v[0]:.4f} {v[1]:.4f} {v[2]:.4f}\n")
            for vt in self.uvs:
                f.write(f"vt {vt[0]:.4f} {vt[1]:.4f}\n")
            for vn in self.vertex_normals:
                f.write(f"vn {vn[0]:.4f} {vn[1]:.4f} {vn[2]:.4f}\n")

            curr = None
            for mtl, v_indices, vt_indices in self.faces:
                if mtl != curr:
                    curr = mtl
                    f.write(f"usemtl {curr}\n")
                f_str = " ".join([f"{v}/{vt}/{v}" for v, vt in zip(v_indices, vt_indices)])
                f.write(f"f {f_str}\n")


# ==============================================================================
# 3. HIGH-FIDELITY ORGANIC CHICKEN MODEL GENERATOR
# ==============================================================================

def generate_organic_chicken(pose="standing"):
    """
    Constructs an anatomically authentic, curved chicken with organic body splines,
    sculpted breast, wings with covert layers, arched neck, head, comb, wattles, beak, and legs.
    """
    b = SmoothObjBuilder()

    # Posture offsets
    if pose == "standing":
        body_z = 0.17
        neck_base = (0.07, 0.0, body_z + 0.05)
        head_pos = (0.13, 0.0, 0.31)
        tail_tip = (-0.17, 0.0, 0.26)
    elif pose == "pecking":
        body_z = 0.15
        neck_base = (0.08, 0.0, body_z + 0.03)
        head_pos = (0.19, 0.0, 0.06)  # Pecking near floor / trough
        tail_tip = (-0.18, 0.0, 0.28)
    else:  # resting
        body_z = 0.07
        neck_base = (0.06, 0.0, body_z + 0.04)
        head_pos = (0.11, 0.0, 0.23)
        tail_tip = (-0.16, 0.0, 0.18)

    b.set_material("feathers")

    # 1. Sculpted Avian Torso (Layered ellipsoidal spline rings along spine)
    num_rings = 14
    rad_segs = 16
    x_spine = np.linspace(-0.13, 0.10, num_rings)

    ring_verts = []
    for i, x in enumerate(x_spine):
        # Parametric profile of chicken body
        u = i / (num_rings - 1)
        # Width ry, height rz, center z
        ry = 0.088 * math.sin(u * math.pi) * (1.0 - 0.15 * (u - 0.5))
        rz = 0.095 * math.sin(u * math.pi) * (1.0 + 0.25 * math.cos(u * math.pi))
        cz = body_z + 0.02 * math.sin(u * math.pi) - 0.01 * (u - 0.5)

        # Forward breast bulge
        if u > 0.65:
            rz *= (1.0 + 0.3 * (u - 0.65))
            cz += 0.015 * (u - 0.65)

        ring = []
        for j in range(rad_segs):
            phi = 2.0 * math.pi * j / rad_segs
            vy = ry * math.sin(phi)
            vz = cz + rz * math.cos(phi)
            v_idx = b.add_vertex(x, vy, vz)
            b.add_uv(u, j / rad_segs)
            ring.append(v_idx)
        ring_verts.append(ring)

    # Torso quads
    for i in range(num_rings - 1):
        for j in range(rad_segs):
            nj = (j + 1) % rad_segs
            v1, v2 = ring_verts[i][j], ring_verts[i][nj]
            v3, v4 = ring_verts[i + 1][nj], ring_verts[i + 1][j]
            b.add_quad(v1, v2, v3, v4)

    # Cap front & rear of torso
    v_front = b.add_vertex(x_spine[-1] + 0.02, 0.0, body_z)
    v_rear = b.add_vertex(x_spine[0] - 0.02, 0.0, body_z)
    for j in range(rad_segs):
        nj = (j + 1) % rad_segs
        b.add_triangle(v_front, ring_verts[-1][j], ring_verts[-1][nj])
        b.add_triangle(v_rear, ring_verts[0][nj], ring_verts[0][j])

    # 2. Sculpted Flank Wings (Left & Right)
    for y_sign in [-1.0, 1.0]:
        wing_y = y_sign * 0.082
        # Upper wing covert
        b.add_cylinder(0.01, wing_y, body_z - 0.02, body_z + 0.05, 0.075, 0.065, segments=12, mtl="feathers")
        # Lower flight feathers
        b.add_cylinder(-0.03, y_sign * 0.078, body_z - 0.03, body_z + 0.02, 0.055, 0.035, segments=10, mtl="feathers")

    # 3. Fan Tail (Upward sickle feathers)
    tail_r = 0.045
    b.add_cylinder(tail_tip[0] * 0.7, 0.0, body_z + 0.02, tail_tip[2], tail_r, 0.018, segments=10, mtl="feathers")
    # Sickle plume flares
    b.add_box(tail_tip[0] - 0.02, 0.0, tail_tip[2] + 0.02, dx=0.06, dy=0.025, dz=0.07, mtl="feathers")

    # 4. Graceful Arched Neck & Head
    # Curved loft along neck from neck_base to head_pos
    neck_steps = 6
    neck_rings = []
    for s in range(neck_steps):
        t = s / (neck_steps - 1)
        nx = neck_base[0] * (1 - t) + head_pos[0] * t + 0.015 * math.sin(t * math.pi)
        nz = neck_base[2] * (1 - t) + head_pos[2] * t
        nr = 0.048 * (1 - 0.35 * t)  # Tapers towards head
        ring = []
        for j in range(12):
            phi = 2.0 * math.pi * j / 12
            vx = nx + nr * math.cos(phi) * 0.7
            vy = nr * math.sin(phi)
            vz = nz + nr * math.cos(phi) * 0.5
            ring.append(b.add_vertex(vx, vy, vz))
        neck_rings.append(ring)

    for s in range(neck_steps - 1):
        for j in range(12):
            nj = (j + 1) % 12
            b.add_quad(neck_rings[s][j], neck_rings[s][nj], neck_rings[s + 1][nj], neck_rings[s + 1][j])

    # Head Cranium
    hx, hy, hz = head_pos
    head_v = []
    for i in range(8):
        th = math.pi * i / 7
        for j in range(12):
            phi = 2.0 * math.pi * j / 12
            vx = hx + 0.045 * math.sin(th) * math.cos(phi)
            vy = hy + 0.035 * math.sin(th) * math.sin(phi)
            vz = hz + 0.040 * math.cos(th)
            head_v.append(b.add_vertex(vx, vy, vz))

    # 5. Anatomical Crimson Comb (Undulating 5-point serrated crown)
    b.set_material("comb")
    comb_pts = [
        (hx - 0.025, hz + 0.045, 0.015),
        (hx - 0.010, hz + 0.055, 0.024),
        (hx + 0.005, hz + 0.062, 0.028),
        (hx + 0.020, hz + 0.058, 0.025),
        (hx + 0.032, hz + 0.048, 0.018),
    ]
    # Comb blade
    b.add_box(hx + 0.005, 0.0, hz + 0.042, dx=0.065, dy=0.010, dz=0.025, mtl="comb")
    # Comb serrations
    for px, pz, ph in comb_pts:
        b.add_box(px, 0.0, pz, dx=0.012, dy=0.008, dz=ph, mtl="comb")

    # 6. Throat Wattles (Fleshy pendulous lobes)
    b.add_box(hx + 0.028, -0.010, hz - 0.035, dx=0.018, dy=0.008, dz=0.028, mtl="comb")
    b.add_box(hx + 0.028,  0.010, hz - 0.035, dx=0.018, dy=0.008, dz=0.028, mtl="comb")

    # 7. Curved Beak (Golden cone with downward hook)
    b.set_material("beak")
    bk_base_x = hx + 0.040
    bk_tip_x = hx + 0.078
    bk_z = hz - 0.010
    v_tip = b.add_vertex(bk_tip_x, 0.0, bk_z - 0.004)
    v_b1 = b.add_vertex(bk_base_x, -0.014, bk_z + 0.012)
    v_b2 = b.add_vertex(bk_base_x,  0.014, bk_z + 0.012)
    v_b3 = b.add_vertex(bk_base_x,  0.000, bk_z - 0.014)
    b.add_triangle(v_tip, v_b1, v_b2)
    b.add_triangle(v_tip, v_b2, v_b3)
    b.add_triangle(v_tip, v_b3, v_b1)

    # 8. Eyes (Iris & pupil)
    b.set_material("eyes")
    b.add_cylinder(hx + 0.018, -0.034, hz + 0.008, hz + 0.014, 0.006, 0.006, segments=8, mtl="eyes")
    b.add_cylinder(hx + 0.018,  0.034, hz + 0.008, hz + 0.014, 0.006, 0.006, segments=8, mtl="eyes")

    # 9. Legs & Feet (Tucked drumsticks and scaled shanks with toes)
    if pose in ["standing", "pecking"]:
        b.set_material("legs")
        for y_leg in [-0.045, 0.045]:
            # Drumstick thigh
            b.add_cylinder(-0.01, y_leg, body_z - 0.06, body_z - 0.01, 0.022, 0.030, segments=8, mtl="feathers")
            # Yellow scaled shank
            b.add_cylinder(-0.01, y_leg, 0.015, body_z - 0.06, 0.008, 0.009, segments=8, mtl="legs")
            # Ankle spur
            b.add_box(-0.022, y_leg, 0.025, dx=0.015, dy=0.006, dz=0.008, mtl="legs")
            # Front center toe
            b.add_box(0.018, y_leg, 0.006, dx=0.045, dy=0.007, dz=0.008, mtl="legs")
            # Left toe
            b.add_box(0.012, y_leg - 0.018, 0.006, dx=0.035, dy=0.006, dz=0.008, mtl="legs")
            # Right toe
            b.add_box(0.012, y_leg + 0.018, 0.006, dx=0.035, dy=0.006, dz=0.008, mtl="legs")
            # Rear toe
            b.add_box(-0.025, y_leg, 0.006, dx=0.025, dy=0.006, dz=0.008, mtl="legs")

    return b


def create_enhanced_chicken_model(model_name, breed="white", pose="standing"):
    model_dir = os.path.join(MODELS_DIR, model_name)
    meshes_dir = os.path.join(model_dir, "meshes")
    ensure_dir(meshes_dir)

    builder = generate_organic_chicken(pose)
    obj_filename = f"{model_name}.obj"
    mtl_filename = f"{model_name}.mtl"
    builder.save(os.path.join(meshes_dir, obj_filename), mtl_lib_name=mtl_filename)

    feather_tex = "feather_white_hd.png" if breed == "white" else "feather_brown_hd.png"
    with open(os.path.join(meshes_dir, mtl_filename), "w") as f:
        f.write(f"""# Realistic Chicken Material
newmtl feathers
Ka 1.0 1.0 1.0
Kd 0.95 0.95 0.95
Ks 0.15 0.15 0.15
map_Kd ../../../materials/textures/{feather_tex}

newmtl comb
Ka 1.0 0.1 0.1
Kd 0.9 0.15 0.15
Ks 0.35 0.15 0.15
map_Kd ../../../materials/textures/chicken_anatomy_hd.png

newmtl beak
Ka 1.0 0.8 0.15
Kd 0.95 0.8 0.15
Ks 0.4 0.3 0.1
map_Kd ../../../materials/textures/chicken_anatomy_hd.png

newmtl legs
Ka 0.95 0.65 0.15
Kd 0.95 0.65 0.15
Ks 0.25 0.2 0.05
map_Kd ../../../materials/textures/chicken_anatomy_hd.png

newmtl eyes
Ka 0.1 0.1 0.1
Kd 0.2 0.2 0.2
Ks 0.9 0.9 0.9
map_Kd ../../../materials/textures/chicken_anatomy_hd.png
""")

    with open(os.path.join(model_dir, "model.config"), "w") as f:
        f.write(f"""<?xml version="1.0"?>
<model>
  <name>{model_name}</name>
  <version>2.0</version>
  <sdf version="1.8">model.sdf</sdf>
  <description>High-fidelity realistic {breed.capitalize()} chicken in {pose} pose.</description>
</model>
""")

    with open(os.path.join(model_dir, "model.sdf"), "w") as f:
        f.write(f"""<?xml version="1.0" ?>
<sdf version="1.8">
  <model name="{model_name}">
    <static>true</static>
    <link name="link">
      <visual name="visual">
        <geometry>
          <mesh>
            <uri>model://{model_name}/meshes/{obj_filename}</uri>
          </mesh>
        </geometry>
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
</sdf>
""")


# ==============================================================================
# 4. REALISTIC 3D CHICKEN EGG MODEL (MATHEMATICAL ASYMMETRIC OVOID)
# ==============================================================================

def generate_egg_model(color="white"):
    model_name = f"egg_{color}"
    print(f"--> Building realistic 3D Egg model ({color})...")
    model_dir = os.path.join(MODELS_DIR, model_name)
    meshes_dir = os.path.join(model_dir, "meshes")
    ensure_dir(meshes_dir)

    b = SmoothObjBuilder()
    b.set_material("eggshell")

    # Authentic chicken egg formula: L = 58mm, W = 44mm
    # Asymmetric ovoid: blunt bottom, tapered top
    L = 0.029
    r0 = 0.022
    k = 0.12  # Asymmetry factor
    z_steps = 18
    th_steps = 18

    grid = []
    for i in range(z_steps + 1):
        u = -1.0 + 2.0 * i / z_steps  # -1 to +1
        z = u * L
        # Egg profile radius
        rad = r0 * math.sqrt(max(0.0, 1.0 - u * u)) * (1.0 - k * u)
        row = []
        for j in range(th_steps):
            phi = 2.0 * math.pi * j / th_steps
            x = rad * math.cos(phi)
            y = rad * math.sin(phi)
            row.append(b.add_vertex(x, y, z + L))  # Base at Z = 0
            b.add_uv(j / th_steps, i / z_steps)
        grid.append(row)

    for i in range(z_steps):
        for j in range(th_steps):
            nj = (j + 1) % th_steps
            p1, p2 = grid[i][j], grid[i][nj]
            p3, p4 = grid[i + 1][nj], grid[i + 1][j]
            if i != 0:
                b.add_triangle(p1, p2, p3)
            if i != z_steps - 1:
                b.add_triangle(p1, p3, p4)

    b.save(os.path.join(meshes_dir, f"{model_name}.obj"), mtl_lib_name=f"{model_name}.mtl")

    tex = "eggshell_white.png" if color == "white" else "eggshell_brown.png"
    with open(os.path.join(meshes_dir, f"{model_name}.mtl"), "w") as f:
        f.write(f"""newmtl eggshell
Ka 1.0 1.0 1.0
Kd 0.95 0.95 0.95
Ks 0.25 0.25 0.25
map_Kd ../../../materials/textures/{tex}
""")

    with open(os.path.join(model_dir, "model.config"), "w") as f:
        f.write(f"""<?xml version="1.0"?>
<model>
  <name>{model_name}</name>
  <version>1.0</version>
  <sdf version="1.8">model.sdf</sdf>
  <description>Realistic {color.capitalize()} chicken egg.</description>
</model>
""")

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
      <collision name="collision">
        <pose>0 0 0.029 0 0 0</pose>
        <geometry>
          <sphere><radius>0.025</radius></sphere>
        </geometry>
      </collision>
    </link>
  </model>
</sdf>
""")


# ==============================================================================
# 5. 30-EGG PACKING TRAY & COMMERCIAL CRATES
# ==============================================================================

def generate_egg_tray():
    model_name = "egg_tray_30"
    print("--> Building 30-Egg Honeycomb Packing Tray...")
    model_dir = os.path.join(MODELS_DIR, model_name)
    meshes_dir = os.path.join(model_dir, "meshes")
    ensure_dir(meshes_dir)

    b = SmoothObjBuilder()
    # Tray: 0.30m × 0.30m × 0.05m pulp tray with 5×6 egg dimples filled with eggs
    b.add_box(0, 0, 0.02, dx=0.30, dy=0.30, dz=0.04, mtl="pulp_tray")

    # 30 eggs arranged in 5 rows × 6 cols
    b.set_material("eggshell_tray")
    for r in range(5):
        for c in range(6):
            ex = -0.12 + c * 0.048
            ey = -0.10 + r * 0.050
            ez = 0.045
            b.add_cylinder(ex, ey, ez - 0.015, ez + 0.025, 0.019, 0.015, segments=10, mtl="eggshell_tray")

    b.save(os.path.join(meshes_dir, f"{model_name}.obj"), mtl_lib_name=f"{model_name}.mtl")

    with open(os.path.join(meshes_dir, f"{model_name}.mtl"), "w") as f:
        f.write("""newmtl pulp_tray
Ka 0.8 0.75 0.7
Kd 0.85 0.8 0.75
Ks 0.1 0.1 0.1
map_Kd ../../../materials/textures/egg_carton_pulp.png

newmtl eggshell_tray
Ka 0.95 0.85 0.75
Kd 0.95 0.85 0.75
Ks 0.25 0.25 0.25
map_Kd ../../../materials/textures/eggshell_brown.png
""")

    with open(os.path.join(model_dir, "model.config"), "w") as f:
        f.write(f"""<?xml version="1.0"?>
<model><name>{model_name}</name><version>1.0</version><sdf version="1.8">model.sdf</sdf></model>""")

    with open(os.path.join(model_dir, "model.sdf"), "w") as f:
        f.write(f"""<?xml version="1.0" ?>
<sdf version="1.8">
  <model name="{model_name}">
    <static>true</static>
    <link name="link">
      <visual name="visual"><geometry><mesh><uri>model://{model_name}/meshes/{model_name}.obj</uri></mesh></geometry></visual>
      <collision name="collision"><geometry><box><size>0.30 0.30 0.08</size></box></geometry></collision>
    </link>
  </model>
</sdf>""")


# ==============================================================================
# 6. INDUSTRIAL EGG SEPARATION & GRADING MILL FACILITY
# ==============================================================================

def generate_egg_separation_mill():
    model_name = "egg_separation_mill"
    print("--> Building complete Industrial Egg Separation & Grading Mill...")
    model_dir = os.path.join(MODELS_DIR, model_name)
    meshes_dir = os.path.join(model_dir, "meshes")
    ensure_dir(meshes_dir)

    b = SmoothObjBuilder()

    # Facility Footprint: 4.8m long along X, 2.4m wide along Y, 2.9m high
    # 1. Multi-Tier Egg Infeed Elevator Towers (Receives from all 5 rack levels)
    # Left infeed tower (Y = -0.7) and Right infeed tower (Y = +0.7)
    for ty in [-0.7, 0.7]:
        # Vertical steel tower columns
        b.add_box(-2.2, ty, 1.45, dx=0.45, dy=0.60, dz=2.85, mtl="stainless")
        # 5 Infeed Belt Reception Funnels at the 5 tier heights
        for z_h in [0.40, 0.90, 1.40, 1.90, 2.40]:
            b.add_box(-2.4, ty, z_h, dx=0.40, dy=0.55, dz=0.12, mtl="stainless")
            # Eggs rolling into the elevator
            b.add_cylinder(-2.3, ty, z_h + 0.02, z_h + 0.06, 0.08, 0.08, segments=10, mtl="egg_cluster")
        # Elevator drive motor housing on top
        b.add_box(-2.2, ty, 2.95, dx=0.35, dy=0.35, dz=0.30, mtl="motor_blue")

    # 2. Transverse Egg Collection Conveyor Bed
    b.add_box(-1.7, 0.0, 0.45, dx=0.70, dy=2.0, dz=0.15, mtl="stainless")
    # Roller conveyor spool track
    b.add_box(-1.7, 0.0, 0.54, dx=0.65, dy=1.8, dz=0.04, mtl="rubber_rollers")

    # 3. Candling & Defect Optical Inspection Booth (Darkened hood with LED bar)
    b.add_box(-1.0, 0.0, 0.95, dx=0.75, dy=1.8, dz=0.85, mtl="dark_canopy")
    b.add_box(-1.0, 0.0, 0.55, dx=0.70, dy=1.6, dz=0.06, mtl="candling_light")

    # 4. Enclosed Egg Washing & Sanitizing / Drying Unit
    b.add_box(-0.1, 0.0, 0.90, dx=1.1, dy=1.6, dz=0.90, mtl="stainless")
    # Inspection viewing window
    b.add_box(-0.1, -0.81, 0.95, dx=0.60, dy=0.02, dz=0.45, mtl="viewing_glass")
    # Hot air drying vent chimney on top
    b.add_cylinder(-0.1, 0.0, 1.35, 1.75, 0.15, 0.18, segments=12, mtl="stainless")

    # 5. Core Egg Sizing & Separation Mill (The Weigher & Classifier Drum)
    # Rotating separation drum & multi-lane sorting scales
    b.add_box(0.9, 0.0, 0.85, dx=0.90, dy=1.8, dz=0.80, mtl="stainless")
    # Rotary balance separation wheels
    b.add_cylinder(0.9, 0.0, 1.25, 1.45, 0.35, 0.35, segments=16, mtl="stainless")

    # 6. 4 Output Separation Grade Lanes / Chutes:
    # Lane 1 (Grade XL / Jumbo), Lane 2 (Grade L), Lane 3 (Grade M), Lane 4 (Grade S)
    lane_ys = [-0.65, -0.22, 0.22, 0.65]
    lane_names = ["XL", "L", "M", "S"]
    for idx, ly in enumerate(lane_ys):
        # Sloped gravity discharge chute
        b.add_box(1.7, ly, 0.55, dx=0.85, dy=0.35, dz=0.12, mtl="stainless")
        # Graded eggs rolling down the sorting chute!
        for ex in [1.5, 1.7, 1.9]:
            b.add_cylinder(ex, ly, 0.60, 0.64, 0.045, 0.045, segments=8, mtl="egg_cluster")
        # Packing table at end of chute
        b.add_box(2.2, ly, 0.45, dx=0.38, dy=0.38, dz=0.15, mtl="stainless")
        # 30-egg tray sitting on each packing table!
        b.add_box(2.2, ly, 0.55, dx=0.32, dy=0.32, dz=0.04, mtl="pulp_tray")

    # 7. Operator HMI Touchscreen Console & Status Light Tower
    b.add_box(0.9, 1.05, 1.10, dx=0.25, dy=0.18, dz=0.35, mtl="console_hmi")
    # 3-color status indicator beacon (Green, Amber, Red)
    b.add_cylinder(0.9, 1.05, 1.30, 1.65, 0.03, 0.03, segments=8, mtl="beacon_green")

    # 8. Pallet with Stacked Plastic Egg Crates (Blue & Yellow)
    b.add_box(1.8, 1.1, 0.08, dx=0.80, dy=0.60, dz=0.14, mtl="wood_pallet")
    # Crates stacked
    b.add_box(1.8, 1.1, 0.28, dx=0.70, dy=0.50, dz=0.24, mtl="crate_yellow")
    b.add_box(1.8, 1.1, 0.54, dx=0.70, dy=0.50, dz=0.24, mtl="crate_blue")

    b.save(os.path.join(meshes_dir, f"{model_name}.obj"), mtl_lib_name=f"{model_name}.mtl")

    with open(os.path.join(meshes_dir, f"{model_name}.mtl"), "w") as f:
        f.write("""newmtl stainless
Ka 0.85 0.88 0.90
Kd 0.90 0.92 0.95
Ks 0.75 0.75 0.75
map_Kd ../../../materials/textures/stainless_steel.png

newmtl rubber_rollers
Ka 0.15 0.15 0.15
Kd 0.20 0.20 0.20
Ks 0.1 0.1 0.1

newmtl dark_canopy
Ka 0.1 0.12 0.15
Kd 0.15 0.18 0.22
Ks 0.2 0.2 0.2

newmtl candling_light
Ka 1.0 0.95 0.6
Kd 1.0 0.95 0.6
Ks 0.8 0.8 0.8

newmtl viewing_glass
Ka 0.4 0.6 0.8
Kd 0.4 0.6 0.8
Ks 0.9 0.9 0.9
d 0.55

newmtl egg_cluster
Ka 0.95 0.85 0.75
Kd 0.95 0.85 0.75
Ks 0.3 0.3 0.3
map_Kd ../../../materials/textures/eggshell_brown.png

newmtl pulp_tray
Ka 0.8 0.75 0.7
Kd 0.85 0.8 0.75
Ks 0.1 0.1 0.1
map_Kd ../../../materials/textures/egg_carton_pulp.png

newmtl motor_blue
Ka 0.1 0.3 0.7
Kd 0.15 0.4 0.8
Ks 0.5 0.5 0.5

newmtl console_hmi
Ka 0.1 0.1 0.15
Kd 0.2 0.5 0.3
Ks 0.6 0.6 0.6

newmtl beacon_green
Ka 0.1 0.9 0.2
Kd 0.1 0.9 0.2
Ks 0.8 0.8 0.8

newmtl wood_pallet
Ka 0.7 0.5 0.3
Kd 0.7 0.5 0.3
Ks 0.1 0.1 0.1

newmtl crate_yellow
Ka 0.9 0.8 0.1
Kd 0.95 0.85 0.1
Ks 0.4 0.4 0.4

newmtl crate_blue
Ka 0.1 0.4 0.8
Kd 0.1 0.45 0.85
Ks 0.4 0.4 0.4
""")

    with open(os.path.join(model_dir, "model.config"), "w") as f:
        f.write(f"""<?xml version="1.0"?>
<model>
  <name>{model_name}</name>
  <version>1.0</version>
  <sdf version="1.8">model.sdf</sdf>
  <description>Automated commercial poultry egg separation and grading mill with 5-tier elevator infeed, candler, washer, 4-grade sizing chutes, and packing tables.</description>
</model>
""")

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
      <collision name="collision_base">
        <pose>0 0 0.8 0 0 0</pose>
        <geometry><box><size>4.8 2.4 1.6</size></box></geometry>
      </collision>
      <collision name="collision_towers">
        <pose>-2.2 0 1.5 0 0 0</pose>
        <geometry><box><size>0.6 2.2 3.0</size></box></geometry>
      </collision>
    </link>
  </model>
</sdf>
""")


# ==============================================================================
# MAIN
# ==============================================================================

def main():
    print("==================================================")
    print("Generating High-Fidelity Realistic Farm Assets...")
    print("==================================================")

    generate_enhanced_textures()

    # 1. Realistic Organic Chickens
    for breed in ["white", "brown"]:
        for pose in ["standing", "pecking", "resting"]:
            create_enhanced_chicken_model(f"chicken_{breed}_{pose}", breed=breed, pose=pose)

    # 2. Eggs (White and Brown)
    generate_egg_model("white")
    generate_egg_model("brown")

    # 3. 30-Egg Honeycomb Trays
    generate_egg_tray()

    # 4. Industrial Egg Separation & Grading Mill
    generate_egg_separation_mill()

    print("==================================================")
    print("All Enhanced Assets Successfully Generated!")
    print("==================================================")


if __name__ == "__main__":
    main()
