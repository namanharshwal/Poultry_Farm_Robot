#!/usr/bin/env python3
import math
import numpy as np
import trimesh

def create_photorealistic_egg(L=0.029, r0=0.022, k=0.12, n_rings=48, n_slices=48):
    """
    Creates an authentic asymmetric avian egg mesh with analytical surface normals.
    Cartesian Oval / Narushin equation.
    """
    verts = []
    normals = []
    uvs = []
    faces = []

    # Vertex grid
    for i in range(n_rings + 1):
        u = -1.0 + 2.0 * i / n_rings  # u in [-1, 1]
        z = u * L
        # Egg profile radius
        rad = r0 * math.sqrt(max(0.0, 1.0 - u * u)) * (1.0 - k * u)
        
        # Derivative dz/du and drad/du for exact surface normals
        # rad(u) = r0 * (1 - u^2)^0.5 * (1 - k*u)
        # drad/du = r0 * [-u / (1 - u^2)^0.5 * (1 - k*u) - k * (1 - u^2)^0.5]
        if abs(u) < 0.999:
            sqrt_term = math.sqrt(1.0 - u * u)
            drad_du = r0 * (-u / sqrt_term * (1.0 - k * u) - k * sqrt_term)
            dz_du = L
            # Tangent vector in (rad, z) plane: T = (drad_du, dz_du)
            # Inward/outward normal in (rad, z) plane: N = (dz_du, -drad_du)
            nr_base = dz_du
            nz_base = -drad_du
            norm_len = math.hypot(nr_base, nz_base)
            nr_base /= norm_len
            nz_base /= norm_len
        else:
            # At poles
            nr_base = 0.0
            nz_base = 1.0 if u < 0 else -1.0

        for j in range(n_slices):
            phi = 2.0 * math.pi * j / n_slices
            cp = math.cos(phi)
            sp = math.sin(phi)
            
            x = rad * cp
            y = rad * sp
            # Set base at Z = 0
            verts.append([x, y, z + L])
            
            # Exact 3D normal
            nx = nr_base * cp
            ny = nr_base * sp
            nz = nz_base
            normals.append([nx, ny, nz])
            
            # UV mapping
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

    mesh = trimesh.Trimesh(
        vertices=np.array(verts, dtype=np.float64),
        faces=np.array(faces, dtype=np.int64),
        vertex_normals=np.array(normals, dtype=np.float64)
    )
    return mesh, np.array(uvs, dtype=np.float64)

if __name__ == '__main__':
    egg_mesh, egg_uvs = create_photorealistic_egg()
    print('Egg mesh generated:')
    print('  Vertices:', len(egg_mesh.vertices))
    print('  Faces:', len(egg_mesh.faces))
    print('  Watertight?', egg_mesh.is_watertight)
    print('  Bounding box extents (m):', egg_mesh.extents)
