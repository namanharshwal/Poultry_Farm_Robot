#!/usr/bin/env python3
import math
import numpy as np
import trimesh

def create_ellipsoid_mesh(center, radii, n_rings=16, n_slices=16):
    """Creates a smooth UV ellipsoid."""
    cx, cy, cz = center
    rx, ry, rz = radii
    verts = []
    uvs = []
    faces = []
    for i in range(n_rings + 1):
        u = -1.0 + 2.0 * i / n_rings
        th = math.pi * (0.5 - 0.5 * u)  # 0 to pi
        z = cz + rz * math.cos(th)
        r_xy = math.sin(th)
        for j in range(n_slices):
            phi = 2.0 * math.pi * j / n_slices
            x = cx + rx * r_xy * math.cos(phi)
            y = cy + ry * r_xy * math.sin(phi)
            verts.append([x, y, z])
            uvs.append([j / n_slices, i / n_rings])

    for i in range(n_rings):
        for j in range(n_slices):
            nj = (j + 1) % n_slices
            p1 = i * n_slices + j
            p2 = i * n_slices + nj
            p3 = (i + 1) * n_slices + nj
            p4 = (i + 1) * n_slices + j
            if i != 0:
                faces.append([p1, p2, p3])
            if i != n_rings - 1:
                faces.append([p1, p3, p4])
    return trimesh.Trimesh(vertices=verts, faces=faces)

def create_lofted_chicken_body(body_z=0.17, n_rings=24, n_slices=24):
    """
    Creates an anatomically sculpted avian torso with full breast and keel contour.
    """
    x_coords = np.linspace(-0.14, 0.12, n_rings)
    verts = []
    faces = []
    
    for i, x in enumerate(x_coords):
        t = i / (n_rings - 1)  # 0 (tail end) to 1 (breast end)
        # Chicken body profile: wide breast, deep keel, tapered rump
        sin_t = math.sin(t * math.pi)
        ry = 0.092 * sin_t * (1.0 - 0.15 * (t - 0.5))
        rz = 0.105 * sin_t * (1.0 + 0.35 * sin_t)
        cz = body_z + 0.025 * sin_t - 0.015 * (t - 0.5)
        
        # Keel protrusion at breast
        if t > 0.55:
            rz *= (1.0 + 0.25 * (t - 0.55))
            cz += 0.015 * (t - 0.55)

        for j in range(n_slices):
            phi = 2.0 * math.pi * j / n_slices
            vy = ry * math.sin(phi)
            vz = cz + rz * math.cos(phi)
            verts.append([x, vy, vz])

    for i in range(n_rings - 1):
        for j in range(n_slices):
            nj = (j + 1) % n_slices
            p1 = i * n_slices + j
            p2 = i * n_slices + nj
            p3 = (i + 1) * n_slices + nj
            p4 = (i + 1) * n_slices + j
            faces.append([p1, p2, p3])
            faces.append([p1, p3, p4])

    # End caps
    v_front_idx = len(verts)
    verts.append([x_coords[-1] + 0.02, 0.0, body_z + 0.02])
    v_back_idx = len(verts)
    verts.append([x_coords[0] - 0.02, 0.0, body_z])

    for j in range(n_slices):
        nj = (j + 1) % n_slices
        # Front cap
        f1 = (n_rings - 1) * n_slices + j
        f2 = (n_rings - 1) * n_slices + nj
        faces.append([v_front_idx, f1, f2])
        # Back cap
        b1 = j
        b2 = nj
        faces.append([v_back_idx, b2, b1])

    return trimesh.Trimesh(vertices=verts, faces=faces)

if __name__ == '__main__':
    body = create_lofted_chicken_body()
    print('Chicken body mesh:')
    print('  Vertices:', len(body.vertices))
    print('  Faces:', len(body.faces))
    print('  Watertight?', body.is_watertight)
    print('  Extents:', body.extents)
