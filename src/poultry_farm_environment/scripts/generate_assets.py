#!/usr/bin/env python3
"""
Procedural Asset Generator for Gazebo Poultry Farm World.
Generates:
  - Textures: litter bedding, corrugated metal, concrete, galvanized steel, wood, chicken plumage, ArUco markers.
  - 3D OBJ Meshes & Materials: chickens (standing, pecking, resting), feed silos, feeder pans, drinker lines,
    exhaust fans, brooder heaters, perches, nesting boxes, barn structure, and paddock fences.
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
# 1. TEXTURE GENERATORS
# ==============================================================================

def generate_textures():
    print("--> Generating realistic textures...")
    ensure_dir(TEXTURES_DIR)

    # 1.1 Poultry Litter / Bedding (wood shavings, straw, sawdust mixture)
    size = 512
    litter = np.zeros((size, size, 3), dtype=np.uint8)
    base_color = np.array([210, 185, 140], dtype=np.float32)  # Tan/straw
    noise1 = np.random.normal(0, 18, (size, size, 1))
    noise2 = np.random.normal(0, 10, (size, size, 3))
    litter_arr = np.clip(base_color + noise1 + noise2, 0, 255).astype(np.uint8)

    # Add straw / shaving flecks
    img = Image.fromarray(litter_arr)
    draw = ImageDraw.Draw(img)
    for _ in range(1200):
        x1 = np.random.randint(0, size)
        y1 = np.random.randint(0, size)
        length = np.random.randint(5, 18)
        angle = np.random.uniform(0, 2 * math.pi)
        x2 = int(x1 + length * math.cos(angle))
        y2 = int(y1 + length * math.sin(angle))
        fleck_col = (
            int(np.random.randint(160, 240)),
            int(np.random.randint(140, 205)),
            int(np.random.randint(85, 150))
        )
        draw.line([(x1, y1), (x2, y2)], fill=fleck_col, width=np.random.randint(1, 3))
    img.save(os.path.join(TEXTURES_DIR, "litter_bedding.png"))

    # 1.2 Corrugated Galvanized Metal
    corr = np.zeros((size, size, 3), dtype=np.uint8)
    x = np.linspace(0, 16 * math.pi, size)
    wave = (np.sin(x) * 0.5 + 0.5)[:, None]  # sinusoidal corrugation
    base_metal = np.array([170, 175, 182], dtype=np.float32)
    metal_arr = (base_metal[None, None, :] * (0.75 + 0.45 * wave)).astype(np.float32)
    noise_metal = np.random.normal(0, 8, (size, size, 3))
    metal_arr = np.clip(metal_arr + noise_metal, 0, 255).astype(np.uint8)
    Image.fromarray(metal_arr).save(os.path.join(TEXTURES_DIR, "corrugated_metal.png"))

    # 1.3 Concrete Floor
    base_concrete = np.array([180, 180, 180], dtype=np.float32)
    noise_c = np.random.normal(0, 12, (size, size, 3))
    conc_arr = np.clip(base_concrete + noise_c, 0, 255).astype(np.uint8)
    img_conc = Image.fromarray(conc_arr)
    draw_conc = ImageDraw.Draw(img_conc)
    # Expansion joint grooves
    draw_conc.line([(0, size // 2), (size, size // 2)], fill=(120, 120, 120), width=3)
    draw_conc.line([(size // 2, 0), (size // 2, size)], fill=(120, 120, 120), width=3)
    img_conc.save(os.path.join(TEXTURES_DIR, "concrete_floor.png"))

    # 1.4 Galvanized Zinc Spangle (for Silo & Fans)
    base_spangle = np.array([205, 210, 218], dtype=np.float32)
    spangle_arr = np.clip(base_spangle + np.random.normal(0, 15, (size, size, 3)), 0, 255).astype(np.uint8)
    Image.fromarray(spangle_arr).save(os.path.join(TEXTURES_DIR, "galvanized_steel.png"))

    # 1.5 Wood Plank (Perches & Nesting Boxes)
    wood_arr = np.zeros((size, size, 3), dtype=np.uint8)
    y_lines = np.linspace(0, 40 * math.pi, size)
    grain = (np.sin(y_lines) * 0.2 + 0.8)[:, None]
    base_wood = np.array([195, 150, 105], dtype=np.float32)
    wood_arr = np.clip((base_wood[None, None, :] * grain) + np.random.normal(0, 7, (size, size, 3)), 0, 255).astype(np.uint8)
    Image.fromarray(wood_arr).save(os.path.join(TEXTURES_DIR, "wood_plank.png"))

    # 1.6 Chicken Plumage - White Broiler
    white_base = np.array([242, 240, 235], dtype=np.float32)
    white_feather = np.clip(white_base + np.random.normal(0, 8, (size, size, 3)), 0, 255).astype(np.uint8)
    Image.fromarray(white_feather).save(os.path.join(TEXTURES_DIR, "feather_white.png"))

    # 1.7 Chicken Plumage - Brown Hen (Rhode Island Red / Lohmann Brown)
    brown_base = np.array([160, 75, 35], dtype=np.float32)
    noise_b = np.random.normal(0, 14, (size, size, 3))
    brown_feather = np.clip(brown_base + noise_b, 0, 255).astype(np.uint8)
    Image.fromarray(brown_feather).save(os.path.join(TEXTURES_DIR, "feather_brown.png"))

    # 1.8 Chicken Anatomy Atlas (Comb: red, Beak: yellow, Legs: yellow-orange, Eyes: black)
    atlas = Image.new("RGB", (256, 256), color=(255, 255, 255))
    draw_a = ImageDraw.Draw(atlas)
    draw_a.rectangle([(0, 0), (128, 128)], fill=(215, 25, 28))      # Comb / Wattle (bright red)
    draw_a.rectangle([(128, 0), (256, 128)], fill=(245, 185, 25))   # Beak (golden yellow)
    draw_a.rectangle([(0, 128), (128, 256)], fill=(235, 150, 35))   # Legs / Feet (yellowish orange)
    draw_a.rectangle([(128, 128), (256, 256)], fill=(25, 25, 25))   # Eyes / Pupils (dark)
    atlas.save(os.path.join(TEXTURES_DIR, "chicken_atlas.png"))

    # 1.9 Outdoor Pasture Grass / Soil
    grass_base = np.array([95, 140, 60], dtype=np.float32)
    grass_noise = np.random.normal(0, 16, (size, size, 3))
    grass_arr = np.clip(grass_base + grass_noise, 0, 255).astype(np.uint8)
    Image.fromarray(grass_arr).save(os.path.join(TEXTURES_DIR, "grass_pasture.png"))

    # 1.10 ArUco Navigation Markers (for robot camera SLAM / inspection)
    for marker_id in [0, 1, 2, 3]:
        m_img = Image.new("RGB", (256, 256), color=(255, 255, 255))
        d_m = ImageDraw.Draw(m_img)
        # Black border
        d_m.rectangle([(28, 28), (228, 228)], fill=(0, 0, 0))
        # Inner grid 4x4
        np.random.seed(42 + marker_id)
        grid = np.random.choice([0, 255], size=(4, 4))
        # Outer framing white
        cell_size = 36
        start_xy = 56
        for r in range(4):
            for c in range(4):
                val = int(grid[r, c])
                d_m.rectangle(
                    [(start_xy + c * cell_size, start_xy + r * cell_size),
                     (start_xy + (c + 1) * cell_size, start_xy + (r + 1) * cell_size)],
                    fill=(val, val, val)
                )
        m_img.save(os.path.join(TEXTURES_DIR, f"aruco_marker_{marker_id}.png"))

    print("--> Textures created successfully.")


# ==============================================================================
# 2. 3D OBJ MESH BUILDER HELPER CLASS
# ==============================================================================

class ObjBuilder:
    def __init__(self, mtl_name=None):
        self.vertices = []
        self.normals = []
        self.uvs = []
        self.faces = []  # list of tuples: (usemtl_name, [(v_idx, vt_idx, vn_idx), ...])
        self.current_mtl = mtl_name or "default"

    def set_material(self, mtl_name):
        self.current_mtl = mtl_name

    def add_vertex(self, x, y, z):
        self.vertices.append((float(x), float(y), float(z)))
        return len(self.vertices)

    def add_normal(self, nx, ny, nz):
        l = math.sqrt(nx*nx + ny*ny + nz*nz)
        if l < 1e-6:
            nx, ny, nz = 0.0, 0.0, 1.0
        else:
            nx, ny, nz = nx/l, ny/l, nz/l
        self.normals.append((float(nx), float(ny), float(nz)))
        return len(self.normals)

    def add_uv(self, u, v):
        self.uvs.append((float(u), float(v)))
        return len(self.uvs)

    def add_face(self, v_indices, vt_indices=None, vn_indices=None):
        n = len(v_indices)
        if vt_indices is None:
            vt_indices = [1] * n
        if vn_indices is None:
            vn_indices = [1] * n
        face_verts = list(zip(v_indices, vt_indices, vn_indices))
        self.faces.append((self.current_mtl, face_verts))

    def add_quad(self, v1, v2, v3, v4, uv1=(0,0), uv2=(1,0), uv3=(1,1), uv4=(0,1), normal=None):
        """Add planar quad with 2 triangles."""
        if normal is None:
            # Compute cross product (v2 - v1) x (v4 - v1)
            p1 = self.vertices[v1 - 1]
            p2 = self.vertices[v2 - 1]
            p4 = self.vertices[v4 - 1]
            ax, ay, az = p2[0]-p1[0], p2[1]-p1[1], p2[2]-p1[2]
            bx, by, bz = p4[0]-p1[0], p4[1]-p1[1], p4[2]-p1[2]
            normal = (ay*bz - az*by, az*bx - ax*bz, ax*by - ay*bx)
        n_idx = self.add_normal(*normal)
        t1 = self.add_uv(*uv1)
        t2 = self.add_uv(*uv2)
        t3 = self.add_uv(*uv3)
        t4 = self.add_uv(*uv4)
        self.add_face([v1, v2, v3], [t1, t2, t3], [n_idx, n_idx, n_idx])
        self.add_face([v1, v3, v4], [t1, t3, t4], [n_idx, n_idx, n_idx])

    def add_box(self, cx, cy, cz, dx, dy, dz, mtl=None):
        if mtl:
            self.set_material(mtl)
        hx, hy, hz = dx / 2.0, dy / 2.0, dz / 2.0
        # 8 corners
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
        # Bottom (-Z)
        self.add_quad(v[0], v[3], v[2], v[1], normal=(0, 0, -1))
        # Top (+Z)
        self.add_quad(v[4], v[5], v[6], v[7], normal=(0, 0, 1))
        # Front (-Y)
        self.add_quad(v[0], v[1], v[5], v[4], normal=(0, -1, 0))
        # Right (+X)
        self.add_quad(v[1], v[2], v[6], v[5], normal=(1, 0, 0))
        # Back (+Y)
        self.add_quad(v[2], v[3], v[7], v[6], normal=(0, 1, 0))
        # Left (-X)
        self.add_quad(v[3], v[0], v[4], v[7], normal=(-1, 0, 0))

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

        # Side quads
        for i in range(segments):
            next_i = (i + 1) % segments
            v1, v2 = bot_ring[i], bot_ring[next_i]
            v3, v4 = top_ring[next_i], top_ring[i]
            th_mid = 2.0 * math.pi * (i + 0.5) / segments
            n = (math.cos(th_mid), math.sin(th_mid), 0.0)
            u1 = i / segments
            u2 = (i + 1) / segments
            self.add_quad(v1, v2, v3, v4, uv1=(u1, 0), uv2=(u2, 0), uv3=(u2, 1), uv4=(u1, 1), normal=n)

        if capped:
            # Bottom cap
            if r_bottom > 1e-4:
                b_center = self.add_vertex(cx, cy, z_bottom)
                nb = self.add_normal(0, 0, -1)
                t_c = self.add_uv(0.5, 0.5)
                for i in range(segments):
                    next_i = (i + 1) % segments
                    self.add_face([b_center, bot_ring[next_i], bot_ring[i]], [t_c, t_c, t_c], [nb, nb, nb])
            # Top cap
            if r_top > 1e-4:
                t_center = self.add_vertex(cx, cy, z_top)
                nt = self.add_normal(0, 0, 1)
                t_c = self.add_uv(0.5, 0.5)
                for i in range(segments):
                    next_i = (i + 1) % segments
                    self.add_face([t_center, top_ring[i], top_ring[next_i]], [t_c, t_c, t_c], [nt, nt, nt])

    def add_ellipsoid(self, cx, cy, cz, rx, ry, rz, u_steps=12, v_steps=10, mtl=None):
        if mtl:
            self.set_material(mtl)
        # Lat/Long sphere deformed
        grid = []
        for i in range(v_steps + 1):
            theta = math.pi * i / v_steps  # 0 to pi (north pole to south pole)
            row = []
            sin_t = math.sin(theta)
            cos_t = math.cos(theta)
            for j in range(u_steps):
                phi = 2.0 * math.pi * j / u_steps
                sin_p = math.sin(phi)
                cos_p = math.cos(phi)
                vx = cx + rx * sin_t * cos_p
                vy = cy + ry * sin_t * sin_p
                vz = cz + rz * cos_t
                v_idx = self.add_vertex(vx, vy, vz)
                u = j / u_steps
                v = i / v_steps
                t_idx = self.add_uv(u, v)
                nx = sin_t * cos_p
                ny = sin_t * sin_p
                nz = cos_t
                n_idx = self.add_normal(nx, ny, nz)
                row.append((v_idx, t_idx, n_idx))
            grid.append(row)

        for i in range(v_steps):
            for j in range(u_steps):
                next_j = (j + 1) % u_steps
                p1 = grid[i][j]
                p2 = grid[i][next_j]
                p3 = grid[i + 1][next_j]
                p4 = grid[i + 1][j]
                if i != 0:
                    self.add_face([p1[0], p2[0], p3[0]], [p1[1], p2[1], p3[1]], [p1[2], p2[2], p3[2]])
                if i != v_steps - 1:
                    self.add_face([p1[0], p3[0], p4[0]], [p1[1], p3[1], p4[1]], [p1[2], p3[2], p4[2]])

    def save(self, filepath, mtl_lib_name=None):
        with open(filepath, "w") as f:
            f.write("# Procedural 3D OBJ - Poultry Farm Gazebo World\n")
            if mtl_lib_name:
                f.write(f"mtllib {mtl_lib_name}\n")
            if not self.normals:
                self.add_normal(0, 0, 1)
            if not self.uvs:
                self.add_uv(0, 0)
            for v in self.vertices:
                f.write(f"v {v[0]:.4f} {v[1]:.4f} {v[2]:.4f}\n")
            for vt in self.uvs:
                f.write(f"vt {vt[0]:.4f} {vt[1]:.4f}\n")
            for vn in self.normals:
                f.write(f"vn {vn[0]:.4f} {vn[1]:.4f} {vn[2]:.4f}\n")

            curr = None
            for mtl, face in self.faces:
                if mtl != curr:
                    curr = mtl
                    f.write(f"usemtl {curr}\n")
                f_str = " ".join([f"{v}/{vt}/{vn}" for v, vt, vn in face])
                f.write(f"f {f_str}\n")


# ==============================================================================
# 3. 3D MODEL GENERATORS
# ==============================================================================

def generate_chicken_model(pose="standing"):
    """
    Generates an anatomically structured chicken mesh.
    pose in ["standing", "pecking", "resting"]
    """
    print(f"--> Building chicken model ({pose})...")
    builder = ObjBuilder()

    # Dimensions (meters): approx 0.28m long, 0.18m wide, 0.32m tall
    # Body center
    if pose == "standing":
        body_z = 0.17
        neck_ang = math.radians(65)
        head_x = 0.11
        head_z = 0.29
        tail_z = 0.22
    elif pose == "pecking":
        body_z = 0.14
        head_x = 0.17
        head_z = 0.07  # Head near the floor
        tail_z = 0.24
    else:  # resting
        body_z = 0.08
        head_x = 0.09
        head_z = 0.22
        tail_z = 0.14

    # 1. Body (Ellipsoid Plumage)
    builder.add_ellipsoid(0.0, 0.0, body_z, rx=0.12, ry=0.08, rz=0.09, u_steps=14, v_steps=10, mtl="feathers")

    # 2. Wings (Flanks)
    builder.add_ellipsoid(0.01, -0.075, body_z + 0.01, rx=0.09, ry=0.025, rz=0.06, u_steps=10, v_steps=8, mtl="feathers")
    builder.add_ellipsoid(0.01, 0.075, body_z + 0.01, rx=0.09, ry=0.025, rz=0.06, u_steps=10, v_steps=8, mtl="feathers")

    # 3. Tail Feathers (Tilted fan)
    builder.add_cylinder(-0.11, 0.0, body_z + 0.02, tail_z, r_bottom=0.04, r_top=0.015, segments=8, mtl="feathers")

    # 4. Neck & Head
    builder.add_cylinder(head_x * 0.5, 0.0, body_z + 0.04, head_z - 0.03, r_bottom=0.045, r_top=0.035, segments=10, mtl="feathers")
    builder.add_ellipsoid(head_x, 0.0, head_z, rx=0.042, ry=0.035, rz=0.04, u_steps=10, v_steps=8, mtl="feathers")

    # 5. Comb (Red fleshy serrated crown)
    comb_top = head_z + 0.055
    comb_x = head_x - 0.01
    builder.add_box(comb_x, 0.0, head_z + 0.042, dx=0.05, dy=0.01, dz=0.025, mtl="comb")
    # Comb spikes
    builder.add_box(comb_x - 0.015, 0.0, head_z + 0.055, dx=0.012, dy=0.008, dz=0.018, mtl="comb")
    builder.add_box(comb_x + 0.005, 0.0, head_z + 0.058, dx=0.012, dy=0.008, dz=0.022, mtl="comb")

    # 6. Wattle (Red throat lobes)
    builder.add_box(head_x + 0.025, -0.008, head_z - 0.035, dx=0.016, dy=0.006, dz=0.022, mtl="comb")
    builder.add_box(head_x + 0.025, 0.008, head_z - 0.035, dx=0.016, dy=0.006, dz=0.022, mtl="comb")

    # 7. Beak (Golden cone pointing forward)
    beak_base_x = head_x + 0.038
    beak_tip_x = head_x + 0.075
    beak_z = head_z - 0.01
    v_tip = builder.add_vertex(beak_tip_x, 0.0, beak_z)
    v_b1 = builder.add_vertex(beak_base_x, -0.015, beak_z + 0.012)
    v_b2 = builder.add_vertex(beak_base_x, 0.015, beak_z + 0.012)
    v_b3 = builder.add_vertex(beak_base_x, 0.0, beak_z - 0.015)
    builder.set_material("beak")
    builder.add_face([v_tip, v_b1, v_b2])
    builder.add_face([v_tip, v_b2, v_b3])
    builder.add_face([v_tip, v_b3, v_b1])

    # 8. Eyes (Small dark beads)
    builder.add_ellipsoid(head_x + 0.015, -0.032, head_z + 0.01, rx=0.006, ry=0.004, rz=0.006, u_steps=6, v_steps=6, mtl="eyes")
    builder.add_ellipsoid(head_x + 0.015, 0.032, head_z + 0.01, rx=0.006, ry=0.004, rz=0.006, u_steps=6, v_steps=6, mtl="eyes")

    # 9. Legs & Feet (if standing or pecking)
    if pose in ["standing", "pecking"]:
        leg_z_top = body_z - 0.04
        for y_leg in [-0.04, 0.04]:
            # Thigh / Drumstick
            builder.add_cylinder(-0.01, y_leg, leg_z_top - 0.03, leg_z_top, r_bottom=0.018, r_top=0.025, segments=8, mtl="feathers")
            # Shank / Leg bone
            builder.add_cylinder(-0.01, y_leg, 0.01, leg_z_top - 0.03, r_bottom=0.007, r_top=0.008, segments=6, mtl="legs")
            # Toes (3 front, 1 rear spur)
            foot_z = 0.005
            # Center toe
            builder.add_cylinder(-0.01 + 0.02, y_leg, foot_z - 0.003, foot_z + 0.003, r_bottom=0.005, r_top=0.005, segments=6, mtl="legs")
            builder.add_box(-0.01 + 0.025, y_leg, foot_z, dx=0.04, dy=0.007, dz=0.006, mtl="legs")
            # Left toe
            builder.add_box(-0.01 + 0.018, y_leg - 0.015, foot_z, dx=0.03, dy=0.006, dz=0.006, mtl="legs")
            # Right toe
            builder.add_box(-0.01 + 0.018, y_leg + 0.015, foot_z, dx=0.03, dy=0.006, dz=0.006, mtl="legs")
            # Rear spur
            builder.add_box(-0.01 - 0.015, y_leg, foot_z, dx=0.02, dy=0.005, dz=0.006, mtl="legs")

    return builder


def create_chicken_files(model_dir, breed="white", pose="standing"):
    ensure_dir(model_dir)
    meshes_dir = os.path.join(model_dir, "meshes")
    ensure_dir(meshes_dir)

    mesh_filename = f"chicken_{pose}.obj"
    mtl_filename = f"chicken_{breed}.mtl"
    obj_path = os.path.join(meshes_dir, mesh_filename)

    builder = generate_chicken_model(pose)
    builder.save(obj_path, mtl_lib_name=mtl_filename)

    # MTL file
    feather_tex = "feather_white.png" if breed == "white" else "feather_brown.png"
    mtl_path = os.path.join(meshes_dir, mtl_filename)
    with open(mtl_path, "w") as f:
        f.write(f"""# Chicken Material
newmtl feathers
Ka 1.0 1.0 1.0
Kd 0.9 0.9 0.9
Ks 0.1 0.1 0.1
map_Kd ../../../materials/textures/{feather_tex}

newmtl comb
Ka 1.0 0.2 0.2
Kd 0.85 0.1 0.1
Ks 0.3 0.1 0.1

newmtl beak
Ka 1.0 0.8 0.1
Kd 0.95 0.75 0.1
Ks 0.4 0.3 0.1

newmtl legs
Ka 0.9 0.6 0.15
Kd 0.9 0.6 0.15
Ks 0.2 0.15 0.05

newmtl eyes
Ka 0.05 0.05 0.05
Kd 0.1 0.1 0.1
Ks 0.8 0.8 0.8
""")

    # model.config
    with open(os.path.join(model_dir, "model.config"), "w") as f:
        f.write(f"""<?xml version="1.0"?>
<model>
  <name>chicken_{breed}_{pose}</name>
  <version>1.0</version>
  <sdf version="1.8">model.sdf</sdf>
  <author>
    <name>Antigravity Robotics</name>
    <email>robotics@antigravity.ai</email>
  </author>
  <description>Realistic {breed.capitalize()} poultry chicken model in {pose} pose.</description>
</model>
""")

    # model.sdf
    with open(os.path.join(model_dir, "model.sdf"), "w") as f:
        f.write(f"""<?xml version="1.0" ?>
<sdf version="1.8">
  <model name="chicken_{breed}_{pose}">
    <static>true</static>
    <link name="link">
      <inertial>
        <mass>2.4</mass>
        <inertia>
          <ixx>0.015</ixx><ixy>0</ixy><ixz>0</ixz>
          <iyy>0.018</iyy><iyz>0</iyz>
          <izz>0.012</izz>
        </inertia>
      </inertial>
      <visual name="visual">
        <geometry>
          <mesh>
            <uri>model://chicken_{breed}_{pose}/meshes/{mesh_filename}</uri>
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
# 4. FEED SILO MODEL
# ==============================================================================

def generate_feed_silo():
    print("--> Building external Feed Silo...")
    model_dir = os.path.join(MODELS_DIR, "feed_silo")
    meshes_dir = os.path.join(model_dir, "meshes")
    ensure_dir(meshes_dir)

    builder = ObjBuilder()

    # Silo parameters
    radius = 1.4
    cyl_height = 4.2
    hopper_height = 1.8
    roof_height = 1.1
    leg_height = 1.9

    # 1. 4 Sturdy Steel Legs
    for angle in [math.pi/4, 3*math.pi/4, 5*math.pi/4, 7*math.pi/4]:
        lx = (radius * 1.05) * math.cos(angle)
        ly = (radius * 1.05) * math.sin(angle)
        builder.add_box(lx, ly, leg_height / 2.0, dx=0.14, dy=0.14, dz=leg_height, mtl="galvanized")
        # Base plate
        builder.add_box(lx, ly, 0.02, dx=0.35, dy=0.35, dz=0.04, mtl="galvanized")

    # Cross bracing ring
    builder.add_cylinder(0, 0, leg_height * 0.5, leg_height * 0.5 + 0.08, radius * 1.02, radius * 1.02, segments=20, mtl="galvanized", capped=False)

    # 2. Conical Bottom Discharge Hopper
    z_cone_bot = leg_height
    z_cone_top = leg_height + hopper_height
    builder.add_cylinder(0, 0, z_cone_bot, z_cone_top, r_bottom=0.25, r_top=radius, segments=24, mtl="galvanized")

    # 3. Discharge Boot & Auger Motor Unit
    builder.add_box(0, 0, z_cone_bot - 0.25, dx=0.55, dy=0.55, dz=0.45, mtl="equipment_blue")
    # Feed transport pipe extending horizontally
    builder.add_cylinder(0, 1.2, z_cone_bot - 0.25, z_cone_bot - 0.25 + 0.12, 0.08, 0.08, segments=12, mtl="galvanized")

    # 4. Main Cylindrical Corrugated Body
    z_cyl_top = z_cone_top + cyl_height
    builder.add_cylinder(0, 0, z_cone_top, z_cyl_top, radius, radius, segments=32, mtl="galvanized")

    # Corrugated Rings (horizontal structural ribs)
    for zh in np.linspace(z_cone_top + 0.5, z_cyl_top - 0.5, 6):
        builder.add_cylinder(0, 0, zh - 0.04, zh + 0.04, radius * 1.02, radius * 1.02, segments=32, mtl="galvanized", capped=False)

    # 5. Top Conical Roof
    z_apex = z_cyl_top + roof_height
    builder.add_cylinder(0, 0, z_cyl_top, z_apex, r_bottom=radius * 1.03, r_top=0.18, segments=32, mtl="galvanized")

    # Roof vent cap
    builder.add_cylinder(0, 0, z_apex, z_apex + 0.35, 0.25, 0.28, segments=16, mtl="galvanized")

    # 6. Safety Inspection Ladder with Safety Cage
    ladder_x = radius + 0.12
    # Vertical rails
    builder.add_box(ladder_x, -0.22, (z_cyl_top + leg_height)/2, dx=0.04, dy=0.04, dz=z_cyl_top - leg_height, mtl="galvanized")
    builder.add_box(ladder_x, 0.22, (z_cyl_top + leg_height)/2, dx=0.04, dy=0.04, dz=z_cyl_top - leg_height, mtl="galvanized")
    # Rungs
    for rz in np.linspace(leg_height + 0.4, z_cyl_top, 16):
        builder.add_box(ladder_x, 0, rz, dx=0.03, dy=0.44, dz=0.03, mtl="galvanized")

    obj_path = os.path.join(meshes_dir, "feed_silo.obj")
    mtl_path = os.path.join(meshes_dir, "feed_silo.mtl")
    builder.save(obj_path, mtl_lib_name="feed_silo.mtl")

    with open(mtl_path, "w") as f:
        f.write("""newmtl galvanized
Ka 0.8 0.85 0.9
Kd 0.8 0.85 0.9
Ks 0.5 0.5 0.5
map_Kd ../../../materials/textures/galvanized_steel.png

newmtl equipment_blue
Ka 0.1 0.2 0.6
Kd 0.1 0.3 0.7
Ks 0.4 0.4 0.4
""")

    with open(os.path.join(model_dir, "model.config"), "w") as f:
        f.write("""<?xml version="1.0"?>
<model>
  <name>feed_silo</name>
  <version>1.0</version>
  <sdf version="1.8">model.sdf</sdf>
  <description>Agricultural commercial poultry feed storage silo with auger boot.</description>
</model>
""")

    with open(os.path.join(model_dir, "model.sdf"), "w") as f:
        f.write("""<?xml version="1.0" ?>
<sdf version="1.8">
  <model name="feed_silo">
    <static>true</static>
    <link name="link">
      <visual name="visual">
        <geometry>
          <mesh>
            <uri>model://feed_silo/meshes/feed_silo.obj</uri>
          </mesh>
        </geometry>
      </visual>
      <collision name="collision">
        <pose>0 0 4.0 0 0 0</pose>
        <geometry>
          <cylinder>
            <radius>1.6</radius>
            <length>8.0</length>
          </cylinder>
        </geometry>
      </collision>
    </link>
  </model>
</sdf>
""")


# ==============================================================================
# 5. AUTOMATED FEEDER PAN UNIT
# ==============================================================================

def generate_feeder_pan():
    print("--> Building automated Feeder Pan unit...")
    model_dir = os.path.join(MODELS_DIR, "feeder_pan")
    meshes_dir = os.path.join(model_dir, "meshes")
    ensure_dir(meshes_dir)

    builder = ObjBuilder()

    # Feeder pan: Dish diameter 36cm, yellow plastic dish, drop tube, galvanized conveyor pipe
    # 1. Circular Bottom Dish (Yellow)
    dish_r = 0.18
    builder.add_cylinder(0, 0, 0.0, 0.05, r_bottom=dish_r * 0.85, r_top=dish_r, segments=20, mtl="feeder_yellow")
    # Stepped lip
    builder.add_cylinder(0, 0, 0.05, 0.07, r_bottom=dish_r, r_top=dish_r * 0.98, segments=20, mtl="feeder_yellow")
    # Inner feed cone (disperser)
    builder.add_cylinder(0, 0, 0.01, 0.12, r_bottom=dish_r * 0.65, r_top=0.04, segments=16, mtl="feeder_yellow")

    # 2. Radial Anti-Rake Grills (10 spokes)
    for i in range(10):
        ang = 2 * math.pi * i / 10
        gx = (dish_r * 0.8) * math.cos(ang)
        gy = (dish_r * 0.8) * math.sin(ang)
        builder.add_cylinder(gx * 0.5, gy * 0.5, 0.06, 0.18, 0.005, 0.005, segments=6, mtl="grill_red")

    # Top grill collar
    builder.add_cylinder(0, 0, 0.17, 0.20, 0.07, 0.07, segments=16, mtl="grill_red")

    # 3. Center Drop Cylinder
    builder.add_cylinder(0, 0, 0.12, 0.26, 0.045, 0.045, segments=12, mtl="feeder_yellow")

    # 4. Galvanized Conveyor Auger Pipe Passing Through (length 2.0m along X)
    builder.add_box(0, 0, 0.28, dx=2.0, dy=0.045, dz=0.045, mtl="galvanized")

    # 5. Suspension Cable Drop Clamp
    builder.add_box(0, 0, 0.32, dx=0.06, dy=0.06, dz=0.06, mtl="galvanized")
    # Thin cable heading upwards
    builder.add_cylinder(0, 0, 0.35, 1.8, 0.003, 0.003, segments=6, mtl="galvanized", capped=False)

    builder.save(os.path.join(meshes_dir, "feeder_pan.obj"), mtl_lib_name="feeder_pan.mtl")

    with open(os.path.join(meshes_dir, "feeder_pan.mtl"), "w") as f:
        f.write("""newmtl feeder_yellow
Ka 0.9 0.75 0.05
Kd 0.95 0.8 0.1
Ks 0.4 0.4 0.4

newmtl grill_red
Ka 0.8 0.1 0.1
Kd 0.85 0.15 0.15
Ks 0.3 0.3 0.3

newmtl galvanized
Ka 0.7 0.75 0.8
Kd 0.75 0.8 0.85
Ks 0.4 0.4 0.4
map_Kd ../../../materials/textures/galvanized_steel.png
""")

    with open(os.path.join(model_dir, "model.config"), "w") as f:
        f.write("""<?xml version="1.0"?>
<model>
  <name>feeder_pan</name>
  <version>1.0</version>
  <sdf version="1.8">model.sdf</sdf>
  <description>Automated commercial poultry feeder pan unit with anti-waste grill.</description>
</model>
""")

    with open(os.path.join(model_dir, "model.sdf"), "w") as f:
        f.write("""<?xml version="1.0" ?>
<sdf version="1.8">
  <model name="feeder_pan">
    <static>true</static>
    <link name="link">
      <visual name="visual">
        <geometry>
          <mesh>
            <uri>model://feeder_pan/meshes/feeder_pan.obj</uri>
          </mesh>
        </geometry>
      </visual>
      <collision name="collision">
        <pose>0 0 0.12 0 0 0</pose>
        <geometry>
          <cylinder>
            <radius>0.20</radius>
            <length>0.25</length>
          </cylinder>
        </geometry>
      </collision>
    </link>
  </model>
</sdf>
""")


# ==============================================================================
# 6. AUTOMATED NIPPLE DRINKER LINE UNIT
# ==============================================================================

def generate_drinker_line():
    print("--> Building automated Nipple Drinker line...")
    model_dir = os.path.join(MODELS_DIR, "drinker_line")
    meshes_dir = os.path.join(model_dir, "meshes")
    ensure_dir(meshes_dir)

    builder = ObjBuilder()

    # Drinker line: 2m segment along X
    # 1. Aluminum Support Channel on top
    builder.add_box(0, 0, 0.34, dx=2.0, dy=0.035, dz=0.035, mtl="aluminum")

    # 2. Square PVC Water Supply Pipe
    builder.add_box(0, 0, 0.28, dx=2.0, dy=0.028, dz=0.028, mtl="pvc_white")

    # 3. 5 Nipple Drinkers with Orange Drip Cups
    for dx_pos in np.linspace(-0.8, 0.8, 5):
        # Stainless nipple pin
        builder.add_cylinder(dx_pos, 0, 0.24, 0.27, 0.005, 0.005, segments=6, mtl="stainless")
        # Orange drip cup arm and catch cup
        builder.add_box(dx_pos, 0.02, 0.22, dx=0.015, dy=0.015, dz=0.07, mtl="cup_orange")
        builder.add_cylinder(dx_pos, 0.0, 0.17, 0.20, r_bottom=0.025, r_top=0.035, segments=12, mtl="cup_orange")

    # 4. Anti-Roost Electric Shock Wire along top
    builder.add_box(0, 0, 0.40, dx=2.0, dy=0.005, dz=0.005, mtl="stainless")
    builder.add_cylinder(0, 0, 0.35, 0.40, 0.004, 0.004, segments=6, mtl="aluminum")

    # 5. Overhead suspension line
    builder.add_cylinder(0, 0, 0.40, 1.8, 0.002, 0.002, segments=6, mtl="aluminum", capped=False)

    builder.save(os.path.join(meshes_dir, "drinker_line.obj"), mtl_lib_name="drinker_line.mtl")

    with open(os.path.join(meshes_dir, "drinker_line.mtl"), "w") as f:
        f.write("""newmtl aluminum
Ka 0.8 0.8 0.8
Kd 0.85 0.85 0.85
Ks 0.5 0.5 0.5

newmtl pvc_white
Ka 0.95 0.95 0.95
Kd 0.95 0.95 0.95
Ks 0.2 0.2 0.2

newmtl stainless
Ka 0.7 0.7 0.75
Kd 0.7 0.7 0.75
Ks 0.8 0.8 0.8

newmtl cup_orange
Ka 0.9 0.45 0.05
Kd 0.95 0.5 0.05
Ks 0.3 0.3 0.3
""")

    with open(os.path.join(model_dir, "model.config"), "w") as f:
        f.write("""<?xml version="1.0"?>
<model>
  <name>drinker_line</name>
  <version>1.0</version>
  <sdf version="1.8">model.sdf</sdf>
  <description>Nipple drinker waterline with drip cups for poultry sheds.</description>
</model>
""")

    with open(os.path.join(model_dir, "model.sdf"), "w") as f:
        f.write("""<?xml version="1.0" ?>
<sdf version="1.8">
  <model name="drinker_line">
    <static>true</static>
    <link name="link">
      <visual name="visual">
        <geometry>
          <mesh>
            <uri>model://drinker_line/meshes/drinker_line.obj</uri>
          </mesh>
        </geometry>
      </visual>
      <collision name="collision">
        <pose>0 0 0.28 0 0 0</pose>
        <geometry>
          <box>
            <size>2.0 0.1 0.25</size>
          </box>
        </geometry>
      </collision>
    </link>
  </model>
</sdf>
""")


# ==============================================================================
# 7. INDUSTRIAL TUNNEL VENTILATION FAN
# ==============================================================================

def generate_tunnel_fan():
    print("--> Building industrial Tunnel Ventilation Fan...")
    model_dir = os.path.join(MODELS_DIR, "tunnel_fan")
    meshes_dir = os.path.join(model_dir, "meshes")
    ensure_dir(meshes_dir)

    builder = ObjBuilder()

    # Fan Dimensions: 1.4m x 1.4m square frame, 0.45m deep, 1.25m circular cowl
    # 1. Outer Square Steel Box Frame
    builder.add_box(0, 0, 0, dx=0.40, dy=1.40, dz=1.40, mtl="galvanized")

    # 2. Circular Venturi Aerodynamic Shroud / Cowl
    builder.add_cylinder(0, 0, -0.60, 0.60, 0.62, 0.62, segments=24, mtl="cowl_black", capped=False)

    # 3. Center Electric Motor Hub
    builder.add_box(-0.05, 0, 0, dx=0.28, dy=0.24, dz=0.24, mtl="motor_blue")

    # 4. 6 Aerodynamic Fan Blades (Galvanized / Stainless)
    blade_r = 0.58
    for i in range(6):
        ang = 2 * math.pi * i / 6
        by = (blade_r * 0.5) * math.cos(ang)
        bz = (blade_r * 0.5) * math.sin(ang)
        # Tilted blade plate
        builder.add_box(0.02, by, bz, dx=0.03, dy=0.18, dz=0.18, mtl="blade_steel")

    # 5. Protective Safety Wire Mesh / Guard
    builder.add_box(0.18, 0, 0, dx=0.01, dy=1.35, dz=1.35, mtl="wire_mesh")

    # 6. Automatic Exhaust Gravity Louvers / Shutters on Back
    for lz in np.linspace(-0.55, 0.55, 8):
        builder.add_box(-0.19, 0, lz, dx=0.05, dy=1.32, dz=0.02, mtl="galvanized")

    builder.save(os.path.join(meshes_dir, "tunnel_fan.obj"), mtl_lib_name="tunnel_fan.mtl")

    with open(os.path.join(meshes_dir, "tunnel_fan.mtl"), "w") as f:
        f.write("""newmtl galvanized
Ka 0.7 0.75 0.8
Kd 0.75 0.8 0.85
Ks 0.4 0.4 0.4
map_Kd ../../../materials/textures/galvanized_steel.png

newmtl cowl_black
Ka 0.15 0.15 0.15
Kd 0.2 0.2 0.2
Ks 0.3 0.3 0.3

newmtl motor_blue
Ka 0.1 0.25 0.6
Kd 0.15 0.35 0.75
Ks 0.5 0.5 0.5

newmtl blade_steel
Ka 0.8 0.85 0.9
Kd 0.85 0.9 0.95
Ks 0.7 0.7 0.7

newmtl wire_mesh
Ka 0.3 0.3 0.3
Kd 0.4 0.4 0.4
Ks 0.2 0.2 0.2
""")

    with open(os.path.join(model_dir, "model.config"), "w") as f:
        f.write("""<?xml version="1.0"?>
<model>
  <name>tunnel_fan</name>
  <version>1.0</version>
  <sdf version="1.8">model.sdf</sdf>
  <description>1.4m Industrial tunnel ventilation exhaust fan for poultry barns.</description>
</model>
""")

    with open(os.path.join(model_dir, "model.sdf"), "w") as f:
        f.write("""<?xml version="1.0" ?>
<sdf version="1.8">
  <model name="tunnel_fan">
    <static>true</static>
    <link name="link">
      <visual name="visual">
        <geometry>
          <mesh>
            <uri>model://tunnel_fan/meshes/tunnel_fan.obj</uri>
          </mesh>
        </geometry>
      </visual>
      <collision name="collision">
        <geometry>
          <box>
            <size>0.45 1.40 1.40</size>
          </box>
        </geometry>
      </collision>
    </link>
  </model>
</sdf>
""")


# ==============================================================================
# 8. SUSPENDED RADIANT BROODER HEATER
# ==============================================================================

def generate_brooder_heater():
    print("--> Building suspended Brooder Heater...")
    model_dir = os.path.join(MODELS_DIR, "brooder_heater")
    meshes_dir = os.path.join(model_dir, "meshes")
    ensure_dir(meshes_dir)

    builder = ObjBuilder()

    # Radiant heater: 0.85m diameter reflector canopy, suspended 1.8m above floor
    # 1. Spun Aluminum Canopy
    canopy_r = 0.42
    builder.add_cylinder(0, 0, 0.0, 0.16, r_bottom=canopy_r, r_top=0.14, segments=24, mtl="reflector_aluminum")

    # 2. Ceramic Infrared Burner Emitter
    builder.add_cylinder(0, 0, 0.04, 0.12, 0.09, 0.09, segments=16, mtl="burner_ceramic")

    # 3. Control Valve Box on top
    builder.add_box(0, 0, 0.22, dx=0.14, dy=0.14, dz=0.12, mtl="galvanized")

    # 4. Suspension Chains
    for ang in [0, 2*math.pi/3, 4*math.pi/3]:
        cx = (canopy_r * 0.85) * math.cos(ang)
        cy = (canopy_r * 0.85) * math.sin(ang)
        builder.add_cylinder(cx, cy, 0.15, 1.2, 0.003, 0.003, segments=6, mtl="galvanized", capped=False)

    builder.save(os.path.join(meshes_dir, "brooder_heater.obj"), mtl_lib_name="brooder_heater.mtl")

    with open(os.path.join(meshes_dir, "brooder_heater.mtl"), "w") as f:
        f.write("""newmtl reflector_aluminum
Ka 0.85 0.85 0.85
Kd 0.9 0.9 0.9
Ks 0.8 0.8 0.8

newmtl burner_ceramic
Ka 0.8 0.3 0.1
Kd 0.85 0.35 0.1
Ks 0.2 0.2 0.2

newmtl galvanized
Ka 0.7 0.7 0.7
Kd 0.75 0.75 0.75
Ks 0.4 0.4 0.4
""")

    with open(os.path.join(model_dir, "model.config"), "w") as f:
        f.write("""<?xml version="1.0"?>
<model>
  <name>brooder_heater</name>
  <version>1.0</version>
  <sdf version="1.8">model.sdf</sdf>
  <description>Suspended radiant infrared brooder heater for brooding chicks.</description>
</model>
""")

    with open(os.path.join(model_dir, "model.sdf"), "w") as f:
        f.write("""<?xml version="1.0" ?>
<sdf version="1.8">
  <model name="brooder_heater">
    <static>true</static>
    <link name="link">
      <visual name="visual">
        <geometry>
          <mesh>
            <uri>model://brooder_heater/meshes/brooder_heater.obj</uri>
          </mesh>
        </geometry>
      </visual>
      <collision name="collision">
        <pose>0 0 0.10 0 0 0</pose>
        <geometry>
          <cylinder>
            <radius>0.45</radius>
            <length>0.25</length>
          </cylinder>
        </geometry>
      </collision>
    </link>
  </model>
</sdf>
""")


# ==============================================================================
# 9. A-FRAME PERCH & NESTING BOX (FARM ENRICHMENT)
# ==============================================================================

def generate_perch_frame():
    print("--> Building A-Frame Perch unit...")
    model_dir = os.path.join(MODELS_DIR, "perch_a_frame")
    meshes_dir = os.path.join(model_dir, "meshes")
    ensure_dir(meshes_dir)

    builder = ObjBuilder()

    # Perch length: 2.4m along X, A-frame width 0.8m, height 0.75m
    length = 2.4
    # Two end A-frames
    for x_end in [-length/2, length/2]:
        # Left leg
        builder.add_box(x_end, -0.35, 0.38, dx=0.06, dy=0.06, dz=0.76, mtl="wood")
        # Right leg
        builder.add_box(x_end, 0.35, 0.38, dx=0.06, dy=0.06, dz=0.76, mtl="wood")
        # Tie strut
        builder.add_box(x_end, 0, 0.15, dx=0.04, dy=0.70, dz=0.04, mtl="wood")

    # 3 Horizontal Roosting Bars at graduated heights
    builder.add_box(0, -0.28, 0.28, dx=length, dy=0.05, dz=0.04, mtl="wood")
    builder.add_box(0, 0.28, 0.28, dx=length, dy=0.05, dz=0.04, mtl="wood")
    builder.add_box(0, 0.0, 0.72, dx=length, dy=0.06, dz=0.04, mtl="wood")

    builder.save(os.path.join(meshes_dir, "perch_frame.obj"), mtl_lib_name="perch_frame.mtl")

    with open(os.path.join(meshes_dir, "perch_frame.mtl"), "w") as f:
        f.write("""newmtl wood
Ka 0.8 0.6 0.4
Kd 0.8 0.6 0.4
Ks 0.2 0.2 0.2
map_Kd ../../../materials/textures/wood_plank.png
""")

    with open(os.path.join(model_dir, "model.config"), "w") as f:
        f.write("""<?xml version="1.0"?>
<model>
  <name>perch_a_frame</name>
  <version>1.0</version>
  <sdf version="1.8">model.sdf</sdf>
  <description>Timber A-frame roosting perch enrichment for poultry.</description>
</model>
""")

    with open(os.path.join(model_dir, "model.sdf"), "w") as f:
        f.write("""<?xml version="1.0" ?>
<sdf version="1.8">
  <model name="perch_a_frame">
    <static>true</static>
    <link name="link">
      <visual name="visual">
        <geometry>
          <mesh>
            <uri>model://perch_a_frame/meshes/perch_frame.obj</uri>
          </mesh>
        </geometry>
      </visual>
      <collision name="collision">
        <pose>0 0 0.38 0 0 0</pose>
        <geometry>
          <box>
            <size>2.4 0.8 0.76</size>
          </box>
        </geometry>
      </collision>
    </link>
  </model>
</sdf>
""")


def generate_nesting_box():
    print("--> Building Nesting Box unit...")
    model_dir = os.path.join(MODELS_DIR, "nesting_box")
    meshes_dir = os.path.join(model_dir, "meshes")
    ensure_dir(meshes_dir)

    builder = ObjBuilder()

    # Nesting box: 2-tier communal unit, 1.6m wide, 0.6m deep, 0.9m tall
    # Main outer cabinet
    builder.add_box(0, 0, 0.45, dx=1.60, dy=0.55, dz=0.90, mtl="wood")

    # Front compartment openings (4 per tier)
    for tier_z in [0.25, 0.70]:
        # Landing perch rail in front
        builder.add_box(0, 0.38, tier_z - 0.12, dx=1.60, dy=0.04, dz=0.04, mtl="wood")
        # Perch support arms
        for px in [-0.7, 0, 0.7]:
            builder.add_box(px, 0.33, tier_z - 0.12, dx=0.03, dy=0.12, dz=0.03, mtl="wood")

    # Sloped anti-roost roof on top
    builder.add_box(0, 0.05, 0.95, dx=1.62, dy=0.60, dz=0.04, mtl="wood")

    builder.save(os.path.join(meshes_dir, "nesting_box.obj"), mtl_lib_name="nesting_box.mtl")

    with open(os.path.join(meshes_dir, "nesting_box.mtl"), "w") as f:
        f.write("""newmtl wood
Ka 0.8 0.6 0.4
Kd 0.8 0.6 0.4
Ks 0.2 0.2 0.2
map_Kd ../../../materials/textures/wood_plank.png
""")

    with open(os.path.join(model_dir, "model.config"), "w") as f:
        f.write("""<?xml version="1.0"?>
<model>
  <name>nesting_box</name>
  <version>1.0</version>
  <sdf version="1.8">model.sdf</sdf>
  <description>Two-tier communal laying nesting box unit with landing perches.</description>
</model>
""")

    with open(os.path.join(model_dir, "model.sdf"), "w") as f:
        f.write("""<?xml version="1.0" ?>
<sdf version="1.8">
  <model name="nesting_box">
    <static>true</static>
    <link name="link">
      <visual name="visual">
        <geometry>
          <mesh>
            <uri>model://nesting_box/meshes/nesting_box.obj</uri>
          </mesh>
        </geometry>
      </visual>
      <collision name="collision">
        <pose>0 0 0.45 0 0 0</pose>
        <geometry>
          <box>
            <size>1.60 0.65 0.90</size>
          </box>
        </geometry>
      </collision>
    </link>
  </model>
</sdf>
""")


# ==============================================================================
# 10. POULTRY BARN BUILDING STRUCTURE
# ==============================================================================

def generate_poultry_barn():
    print("--> Building Poultry Barn architectural model...")
    model_dir = os.path.join(MODELS_DIR, "poultry_barn")
    meshes_dir = os.path.join(model_dir, "meshes")
    ensure_dir(meshes_dir)

    builder = ObjBuilder()

    # Barn Specifications:
    # Length: 24.0m (X: -12.0 to +12.0)
    # Width:  10.0m (Y: -5.0 to +5.0)
    # Eaves height: 3.0m (Z)
    # Apex height:  4.2m (Z) at Y = 0
    L = 24.0
    W = 10.0
    H_eaves = 3.0
    H_apex = 4.2

    # 1. Concrete Foundation Curb Wall (Perimeter foundation)
    curb_thick = 0.25
    curb_h = 0.45
    # North & South Curb walls
    builder.add_box(0, -W/2, curb_h/2, dx=L, dy=curb_thick, dz=curb_h, mtl="concrete")
    builder.add_box(0, W/2, curb_h/2, dx=L, dy=curb_thick, dz=curb_h, mtl="concrete")
    # Front & Back Curb walls
    builder.add_box(-L/2, 0, curb_h/2, dx=curb_thick, dy=W, dz=curb_h, mtl="concrete")
    builder.add_box(L/2, 0, curb_h/2, dx=curb_thick, dy=W, dz=curb_h, mtl="concrete")

    # 2. Structural Steel Portal Frames (6 columns & trusses along length)
    x_frames = np.linspace(-L/2 + 0.2, L/2 - 0.2, 6)
    for xf in x_frames:
        # Left column
        builder.add_box(xf, -W/2 + 0.15, H_eaves/2, dx=0.20, dy=0.20, dz=H_eaves, mtl="steel_frame")
        # Right column
        builder.add_box(xf, W/2 - 0.15, H_eaves/2, dx=0.20, dy=0.20, dz=H_eaves, mtl="steel_frame")
        # Horizontal Tie Rafter beam
        builder.add_box(xf, 0, H_eaves, dx=0.16, dy=W - 0.4, dz=0.16, mtl="steel_frame")
        # King Post to roof apex
        builder.add_box(xf, 0, (H_eaves + H_apex)/2, dx=0.14, dy=0.14, dz=H_apex - H_eaves, mtl="steel_frame")
        # Diagonal Rafters Left & Right
        # Left rafter
        builder.add_box(xf, -W/4, (H_eaves + H_apex)/2, dx=0.14, dy=W/2, dz=0.12, mtl="steel_frame")
        # Right rafter
        builder.add_box(xf, W/4, (H_eaves + H_apex)/2, dx=0.14, dy=W/2, dz=0.12, mtl="steel_frame")

    # 3. Longitudinal Purlins & Ridge Beam (running along full X length)
    builder.add_box(0, 0, H_apex - 0.08, dx=L, dy=0.12, dz=0.14, mtl="steel_frame")
    builder.add_box(0, -W/2 + 0.15, H_eaves - 0.08, dx=L, dy=0.12, dz=0.14, mtl="steel_frame")
    builder.add_box(0, W/2 - 0.15, H_eaves - 0.08, dx=L, dy=0.12, dz=0.14, mtl="steel_frame")

    # 4. Lower Siding Panels (Corrugated metal lower 1.2m of walls)
    builder.add_box(0, -W/2, 0.45 + 0.45, dx=L, dy=0.08, dz=0.90, mtl="corrugated_metal")
    builder.add_box(0, W/2, 0.45 + 0.45, dx=L, dy=0.08, dz=0.90, mtl="corrugated_metal")

    # 5. Upper Ventilation Curtain / Mesh Openings (Height 1.35m to 2.85m)
    # Allows realistic light and cross ventilation while keeping chickens inside
    builder.add_box(0, -W/2, 2.10, dx=L, dy=0.02, dz=1.50, mtl="curtain_mesh")
    builder.add_box(0, W/2, 2.10, dx=L, dy=0.02, dz=1.50, mtl="curtain_mesh")

    # 6. Front Gable End Wall (X = -L/2)
    # Mobile robot roll-up door (2.8m wide, 2.6m high) in center, personnel door to side
    # Left front panel
    builder.add_box(-L/2, -3.2, 1.5, dx=0.10, dy=3.6, dz=3.0, mtl="corrugated_metal")
    # Right front panel
    builder.add_box(-L/2, 3.2, 1.5, dx=0.10, dy=3.6, dz=3.0, mtl="corrugated_metal")
    # Header above robot door
    builder.add_box(-L/2, 0, 2.8, dx=0.10, dy=2.8, dz=0.4, mtl="corrugated_metal")
    # Front gable triangle
    builder.add_box(-L/2, 0, (H_eaves + H_apex)/2 + 0.1, dx=0.08, dy=W * 0.7, dz=H_apex - H_eaves, mtl="corrugated_metal")

    # 7. Back Gable End Fan Wall (X = +L/2)
    # Houses the bank of 4 large tunnel ventilation fans
    # Wall around the fans
    builder.add_box(L/2, -3.8, 1.5, dx=0.12, dy=2.4, dz=3.0, mtl="corrugated_metal")
    builder.add_box(L/2, 3.8, 1.5, dx=0.12, dy=2.4, dz=3.0, mtl="corrugated_metal")
    builder.add_box(L/2, 0, 0.4, dx=0.12, dy=5.2, dz=0.8, mtl="corrugated_metal")
    builder.add_box(L/2, 0, 2.6, dx=0.12, dy=5.2, dz=0.8, mtl="corrugated_metal")
    builder.add_box(L/2, 0, (H_eaves + H_apex)/2 + 0.1, dx=0.08, dy=W * 0.7, dz=H_apex - H_eaves, mtl="corrugated_metal")

    # 8. Roof Pitch Slopes (Left & Right) with Eaves Overhang
    # Slope length sqrt((W/2)^2 + (H_apex - H_eaves)^2) ~ 5.14m
    # Pitch Left Roof (-Y side)
    roof_y_mid = -W/4
    roof_z_mid = (H_eaves + H_apex)/2
    builder.add_box(0, -W/4 - 0.2, roof_z_mid + 0.05, dx=L + 0.8, dy=W/2 + 0.5, dz=0.08, mtl="corrugated_metal")
    # Pitch Right Roof (+Y side)
    builder.add_box(0, W/4 + 0.2, roof_z_mid + 0.05, dx=L + 0.8, dy=W/2 + 0.5, dz=0.08, mtl="corrugated_metal")
    # Ridge Cap along apex
    builder.add_box(0, 0, H_apex + 0.12, dx=L + 0.8, dy=0.45, dz=0.08, mtl="steel_frame")

    # 9. Concrete Entrance Apron (outside front door)
    builder.add_box(-L/2 - 2.5, 0, 0.04, dx=5.0, dy=6.0, dz=0.08, mtl="concrete")

    # 10. Concrete Pad for Silos (outside front-left corner)
    builder.add_box(-L/2 - 1.5, -W/2 - 2.5, 0.06, dx=4.5, dy=4.5, dz=0.12, mtl="concrete")

    builder.save(os.path.join(meshes_dir, "poultry_barn.obj"), mtl_lib_name="poultry_barn.mtl")

    with open(os.path.join(meshes_dir, "poultry_barn.mtl"), "w") as f:
        f.write("""newmtl concrete
Ka 0.8 0.8 0.8
Kd 0.85 0.85 0.85
Ks 0.1 0.1 0.1
map_Kd ../../../materials/textures/concrete_floor.png

newmtl corrugated_metal
Ka 0.75 0.78 0.82
Kd 0.8 0.82 0.86
Ks 0.4 0.4 0.4
map_Kd ../../../materials/textures/corrugated_metal.png

newmtl steel_frame
Ka 0.4 0.45 0.5
Kd 0.45 0.5 0.55
Ks 0.5 0.5 0.5

newmtl curtain_mesh
Ka 0.9 0.9 0.85
Kd 0.9 0.9 0.85
Ks 0.1 0.1 0.1
d 0.65
""")

    with open(os.path.join(model_dir, "model.config"), "w") as f:
        f.write("""<?xml version="1.0"?>
<model>
  <name>poultry_barn</name>
  <version>1.0</version>
  <sdf version="1.8">model.sdf</sdf>
  <description>24m x 10m commercial poultry barn shed structure with ventilation curtains, portal frames, and gable walls.</description>
</model>
""")

    with open(os.path.join(model_dir, "model.sdf"), "w") as f:
        f.write("""<?xml version="1.0" ?>
<sdf version="1.8">
  <model name="poultry_barn">
    <static>true</static>
    <link name="link">
      <visual name="visual">
        <geometry>
          <mesh>
            <uri>model://poultry_barn/meshes/poultry_barn.obj</uri>
          </mesh>
        </geometry>
      </visual>
      <!-- Concrete curb collision North -->
      <collision name="curb_north">
        <pose>0 5.0 0.22 0 0 0</pose>
        <geometry><box><size>24.0 0.25 0.45</size></box></geometry>
      </collision>
      <!-- Concrete curb collision South -->
      <collision name="curb_south">
        <pose>0 -5.0 0.22 0 0 0</pose>
        <geometry><box><size>24.0 0.25 0.45</size></box></geometry>
      </collision>
      <!-- Front wall collision West -->
      <collision name="front_wall_left">
        <pose>-12.0 -3.2 1.5 0 0 0</pose>
        <geometry><box><size>0.25 3.6 3.0</size></box></geometry>
      </collision>
      <collision name="front_wall_right">
        <pose>-12.0 3.2 1.5 0 0 0</pose>
        <geometry><box><size>0.25 3.6 3.0</size></box></geometry>
      </collision>
      <!-- Back fan wall collision East -->
      <collision name="back_wall">
        <pose>12.0 0 1.5 0 0 0</pose>
        <geometry><box><size>0.25 10.0 3.0</size></box></geometry>
      </collision>
      <!-- Side walls collision -->
      <collision name="wall_south">
        <pose>0 -5.0 1.5 0 0 0</pose>
        <geometry><box><size>24.0 0.25 3.0</size></box></geometry>
      </collision>
      <collision name="wall_north">
        <pose>0 5.0 1.5 0 0 0</pose>
        <geometry><box><size>24.0 0.25 3.0</size></box></geometry>
      </collision>
    </link>
  </model>
</sdf>
""")


# ==============================================================================
# 11. ARUCO MARKER CUBE (ROBOT NAVIGATION & CALIBRATION)
# ==============================================================================

def generate_aruco_markers():
    print("--> Building ArUco visual navigation markers...")
    for marker_id in [0, 1, 2, 3]:
        model_name = f"aruco_marker_{marker_id}"
        model_dir = os.path.join(MODELS_DIR, model_name)
        ensure_dir(model_dir)

        with open(os.path.join(model_dir, "model.config"), "w") as f:
            f.write(f"""<?xml version="1.0"?>
<model>
  <name>{model_name}</name>
  <version>1.0</version>
  <sdf version="1.8">model.sdf</sdf>
  <description>Visual ArUco Marker ID {marker_id} for autonomous robot localization.</description>
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
          <box>
            <size>0.02 0.35 0.35</size>
          </box>
        </geometry>
        <material>
          <ambient>1 1 1 1</ambient>
          <diffuse>1 1 1 1</diffuse>
          <pbr>
            <metal>
              <albedo_map>model://poultry_farm_world/materials/textures/aruco_marker_{marker_id}.png</albedo_map>
            </metal>
          </pbr>
        </material>
      </visual>
      <collision name="collision">
        <geometry>
          <box>
            <size>0.02 0.35 0.35</size>
          </box>
        </geometry>
      </collision>
    </link>
  </model>
</sdf>
""")


# ==============================================================================
# 12. ENVIRONMENTAL SENSOR NODE
# ==============================================================================

def generate_sensor_node():
    print("--> Building Environmental Sensor Node...")
    model_dir = os.path.join(MODELS_DIR, "sensor_node")
    meshes_dir = os.path.join(model_dir, "meshes")
    ensure_dir(meshes_dir)

    builder = ObjBuilder()
    # Sensor box: 20cm x 15cm x 8cm IP65 enclosure with antenna and LCD screen
    builder.add_box(0, 0, 0, dx=0.08, dy=0.18, dz=0.14, mtl="box_white")
    # LCD Display window
    builder.add_box(0.041, 0, 0.02, dx=0.005, dy=0.10, dz=0.05, mtl="lcd_screen")
    # Rubber antenna
    builder.add_cylinder(0, 0.07, 0.07, 0.22, 0.006, 0.004, segments=6, mtl="antenna_black")
    # Wall mount bracket
    builder.add_box(-0.045, 0, 0, dx=0.01, dy=0.20, dz=0.16, mtl="box_white")

    builder.save(os.path.join(meshes_dir, "sensor_box.obj"), mtl_lib_name="sensor_box.mtl")

    with open(os.path.join(meshes_dir, "sensor_box.mtl"), "w") as f:
        f.write("""newmtl box_white
Ka 0.9 0.9 0.9
Kd 0.9 0.9 0.9
Ks 0.3 0.3 0.3

newmtl lcd_screen
Ka 0.1 0.4 0.2
Kd 0.1 0.6 0.3
Ks 0.7 0.7 0.7

newmtl antenna_black
Ka 0.1 0.1 0.1
Kd 0.15 0.15 0.15
Ks 0.2 0.2 0.2
""")

    with open(os.path.join(model_dir, "model.config"), "w") as f:
        f.write("""<?xml version="1.0"?>
<model>
  <name>sensor_node</name>
  <version>1.0</version>
  <sdf version="1.8">model.sdf</sdf>
  <description>Wireless telemetry sensor box (NH3, CO2, Temp, RH) for climate monitoring.</description>
</model>
""")

    with open(os.path.join(model_dir, "model.sdf"), "w") as f:
        f.write("""<?xml version="1.0" ?>
<sdf version="1.8">
  <model name="sensor_node">
    <static>true</static>
    <link name="link">
      <visual name="visual">
        <geometry>
          <mesh>
            <uri>model://sensor_node/meshes/sensor_box.obj</uri>
          </mesh>
        </geometry>
      </visual>
      <collision name="collision">
        <geometry>
          <box>
            <size>0.10 0.20 0.20</size>
          </box>
        </geometry>
      </collision>
    </link>
  </model>
</sdf>
""")


# ==============================================================================
# 13. 5-TIER BATTERY / COLONY CAGE RACK SYSTEM (LAYER HOUSE)
# ==============================================================================

def generate_cage_rack_5tier():
    print("--> Building 5-Tier Battery / Colony Cage Rack unit...")
    model_dir = os.path.join(MODELS_DIR, "cage_rack_5tier")
    meshes_dir = os.path.join(model_dir, "meshes")
    ensure_dir(meshes_dir)

    builder = ObjBuilder()

    # Rack Dimensions:
    # Length: 4.0m along X (from -2.0 to +2.0)
    # Width:  1.0m along Y (from -0.5 to +0.5)
    # 5 Tiers:
    #   Tier 0: z = 0.35 to 0.78
    #   Tier 1: z = 0.85 to 1.28
    #   Tier 2: z = 1.35 to 1.78
    #   Tier 3: z = 1.85 to 2.28
    #   Tier 4: z = 2.35 to 2.78
    # Total Height: ~2.85m

    tier_h = 0.43
    tier_gap = 0.07
    z_starts = [0.35 + i * (tier_h + tier_gap) for i in range(5)]

    # 1. Structural Steel Vertical Legs (5 portal frames along X)
    x_posts = [-2.0, -1.0, 0.0, 1.0, 2.0]
    for xp in x_posts:
        # Left post (Y = -0.5)
        builder.add_box(xp, -0.50, 1.45, dx=0.06, dy=0.06, dz=2.85, mtl="galvanized")
        # Right post (Y = +0.5)
        builder.add_box(xp,  0.50, 1.45, dx=0.06, dy=0.06, dz=2.85, mtl="galvanized")
        # Base anchor footplates
        builder.add_box(xp, -0.50, 0.02, dx=0.15, dy=0.15, dz=0.04, mtl="galvanized")
        builder.add_box(xp,  0.50, 0.02, dx=0.15, dy=0.15, dz=0.04, mtl="galvanized")
        # Top cross tie beam
        builder.add_box(xp, 0.0, 2.85, dx=0.05, dy=1.00, dz=0.05, mtl="galvanized")

    # 2. Top Longitudinal Rails along X
    builder.add_box(0, -0.50, 2.85, dx=4.0, dy=0.05, dz=0.05, mtl="galvanized")
    builder.add_box(0,  0.50, 2.85, dx=4.0, dy=0.05, dz=0.05, mtl="galvanized")
    builder.add_box(0,  0.0,  2.85, dx=4.0, dy=0.05, dz=0.05, mtl="galvanized")

    # 3. For each of the 5 Tiers:
    for tier_idx, z_bot in enumerate(z_starts):
        z_top = z_bot + tier_h

        # A. Manure Conveyor Belt Platform underneath tier
        builder.add_box(0, 0, z_bot - 0.03, dx=4.0, dy=0.96, dz=0.02, mtl="manure_belt")
        # Belt support roller pipes at post positions
        for xp in x_posts:
            builder.add_cylinder(xp, 0, z_bot - 0.04, z_bot - 0.02, 0.02, 0.02, segments=8, mtl="galvanized")

        # B. Sloped Wire Floor
        builder.add_box(0, -0.26, z_bot + 0.02, dx=4.0, dy=0.52, dz=0.015, mtl="wire_mesh")
        builder.add_box(0,  0.26, z_bot + 0.02, dx=4.0, dy=0.52, dz=0.015, mtl="wire_mesh")

        # C. Front and Back Egg Roll-out Trays / Cradles
        builder.add_box(0, -0.58, z_bot + 0.02, dx=4.0, dy=0.12, dz=0.04, mtl="galvanized")
        builder.add_box(0,  0.58, z_bot + 0.02, dx=4.0, dy=0.12, dz=0.04, mtl="galvanized")

        # Add realistic eggs resting in the egg trays
        egg_xs = np.linspace(-1.8, 1.8, 10)
        for ex in egg_xs:
            if (tier_idx + int(ex*2)) % 2 == 0:
                mtl_egg = "egg_white" if int(ex*3) % 2 == 0 else "egg_brown"
                builder.add_ellipsoid(ex, -0.58, z_bot + 0.035, rx=0.025, ry=0.018, rz=0.018, u_steps=6, v_steps=6, mtl=mtl_egg)
            if (tier_idx + int(ex*2)) % 3 == 0:
                mtl_egg = "egg_brown" if int(ex*3) % 2 == 0 else "egg_white"
                builder.add_ellipsoid(ex + 0.08, 0.58, z_bot + 0.035, rx=0.025, ry=0.018, rz=0.018, u_steps=6, v_steps=6, mtl=mtl_egg)

        # D. Feed Troughs (Continuous V-channel mounted along front & back)
        builder.add_box(0, -0.54, z_bot + 0.12, dx=4.0, dy=0.12, dz=0.10, mtl="feeder_trough")
        builder.add_box(0,  0.54, z_bot + 0.12, dx=4.0, dy=0.12, dz=0.10, mtl="feeder_trough")

        # E. Front and Back Wire Grills
        builder.add_box(0, -0.50, z_bot + tier_h / 2.0, dx=4.0, dy=0.01, dz=tier_h, mtl="wire_mesh")
        builder.add_box(0,  0.50, z_bot + tier_h / 2.0, dx=4.0, dy=0.01, dz=tier_h, mtl="wire_mesh")

        # F. Center Divider Wire Partition along Y = 0
        builder.add_box(0, 0.0, z_bot + tier_h / 2.0, dx=4.0, dy=0.01, dz=tier_h, mtl="wire_mesh")

        # G. Transverse Wire Partitions (every 0.8m along X)
        for xp in [-1.6, -0.8, 0.0, 0.8, 1.6]:
            builder.add_box(xp, 0.0, z_bot + tier_h / 2.0, dx=0.01, dy=0.98, dz=tier_h, mtl="wire_mesh")

        # H. Top Ceiling Wire of the Tier
        builder.add_box(0, 0.0, z_top, dx=4.0, dy=0.98, dz=0.01, mtl="wire_mesh")

        # I. Nipple Drinker Waterline Pipe inside cage
        builder.add_cylinder(0, -0.20, z_top - 0.08, z_top - 0.08, 0.015, 0.015, segments=8, mtl="water_pvc")
        builder.add_cylinder(0,  0.20, z_top - 0.08, z_top - 0.08, 0.015, 0.015, segments=8, mtl="water_pvc")

    builder.save(os.path.join(meshes_dir, "cage_rack_5tier.obj"), mtl_lib_name="cage_rack_5tier.mtl")

    with open(os.path.join(meshes_dir, "cage_rack_5tier.mtl"), "w") as f:
        f.write("""newmtl galvanized
Ka 0.75 0.8 0.85
Kd 0.8 0.85 0.9
Ks 0.5 0.5 0.5
map_Kd ../../../materials/textures/galvanized_steel.png

newmtl wire_mesh
Ka 0.5 0.52 0.55
Kd 0.6 0.62 0.65
Ks 0.3 0.3 0.3
d 0.55

newmtl manure_belt
Ka 0.9 0.9 0.9
Kd 0.92 0.92 0.92
Ks 0.2 0.2 0.2

newmtl feeder_trough
Ka 0.7 0.75 0.8
Kd 0.75 0.8 0.85
Ks 0.4 0.4 0.4
map_Kd ../../../materials/textures/galvanized_steel.png

newmtl water_pvc
Ka 0.95 0.95 0.95
Kd 0.95 0.95 0.95
Ks 0.2 0.2 0.2

newmtl egg_white
Ka 0.98 0.96 0.92
Kd 0.98 0.96 0.92
Ks 0.3 0.3 0.3

newmtl egg_brown
Ka 0.85 0.65 0.45
Kd 0.88 0.68 0.48
Ks 0.3 0.3 0.3
""")

    with open(os.path.join(model_dir, "model.config"), "w") as f:
        f.write("""<?xml version="1.0"?>
<model>
  <name>cage_rack_5tier</name>
  <version>1.0</version>
  <sdf version="1.8">model.sdf</sdf>
  <description>5-Tier automated commercial layer battery cage rack system with egg roll-out cradles, feed troughs, manure belt platforms, and drinker lines.</description>
</model>
""")

    with open(os.path.join(model_dir, "model.sdf"), "w") as f:
        f.write("""<?xml version="1.0" ?>
<sdf version="1.8">
  <model name="cage_rack_5tier">
    <static>true</static>
    <link name="link">
      <visual name="visual">
        <geometry>
          <mesh>
            <uri>model://cage_rack_5tier/meshes/cage_rack_5tier.obj</uri>
          </mesh>
        </geometry>
      </visual>
      <collision name="collision_main">
        <pose>0 0 1.42 0 0 0</pose>
        <geometry>
          <box>
            <size>4.0 1.15 2.85</size>
          </box>
        </geometry>
      </collision>
    </link>
  </model>
</sdf>
""")


# ==============================================================================
# MAIN ENTRY POINT
# ==============================================================================

def main():
    print("==================================================")
    print("Generating High-Fidelity Poultry Farm Assets...")
    print("==================================================")

    generate_textures()

    # Chicken variants:
    # 1. White Broiler standing, pecking, resting
    create_chicken_files(os.path.join(MODELS_DIR, "chicken_white_standing"), breed="white", pose="standing")
    create_chicken_files(os.path.join(MODELS_DIR, "chicken_white_pecking"), breed="white", pose="pecking")
    create_chicken_files(os.path.join(MODELS_DIR, "chicken_white_resting"), breed="white", pose="resting")

    # 2. Brown Hen standing, pecking, resting
    create_chicken_files(os.path.join(MODELS_DIR, "chicken_brown_standing"), breed="brown", pose="standing")
    create_chicken_files(os.path.join(MODELS_DIR, "chicken_brown_pecking"), breed="brown", pose="pecking")
    create_chicken_files(os.path.join(MODELS_DIR, "chicken_brown_resting"), breed="brown", pose="resting")

    # Farm Equipment & Architecture
    generate_feed_silo()
    generate_feeder_pan()
    generate_drinker_line()
    generate_tunnel_fan()
    generate_brooder_heater()
    generate_perch_frame()
    generate_nesting_box()
    generate_poultry_barn()
    generate_aruco_markers()
    generate_sensor_node()
    generate_cage_rack_5tier()

    print("==================================================")
    print("All Poultry Farm 3D models and textures generated!")
    print("==================================================")


if __name__ == "__main__":
    main()
