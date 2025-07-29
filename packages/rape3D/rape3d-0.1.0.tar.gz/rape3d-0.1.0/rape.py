import numpy as np
import math
from dataclasses import dataclass

# --- VECTOR 3D + OPERATIONS ---
@dataclass
class Vector3D:
    x: float
    y: float
    z: float

    def __add__(self, other):
        return Vector3D(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Vector3D(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar: float):
        return Vector3D(self.x * scalar, self.y * scalar, self.z * scalar)

    def __rmul__(self, scalar: float):
        return self.__mul__(scalar)

    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other):
        return Vector3D(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x,
        )

    def length(self):
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

    def normalize(self):
        l = self.length()
        if l == 0:
            return Vector3D(0, 0, 0)
        return self * (1.0 / l)

    def to_np(self):
        return np.array([self.x, self.y, self.z])

    def __repr__(self):
        return f"Vector3D({self.x:.3f}, {self.y:.3f}, {self.z:.3f})"

# --- MATRIX 4x4 CLASS + OPERATIONS ---
class Matrix4x4:
    def __init__(self, data=None):
        if data is None:
            self.data = np.identity(4, dtype=np.float64)
        else:
            self.data = np.array(data, dtype=np.float64).reshape((4,4))

    def __matmul__(self, other):
        if isinstance(other, Matrix4x4):
            return Matrix4x4(np.dot(self.data, other.data))
        raise TypeError("Unsupported operand for @ with Matrix4x4")

    def transform_vector(self, vec: Vector3D) -> Vector3D:
        v = np.array([vec.x, vec.y, vec.z, 1.0])
        res = self.data @ v
        w = res[3] if res[3] != 0 else 1.0
        return Vector3D(res[0]/w, res[1]/w, res[2]/w)

    @staticmethod
    def translation(tx, ty, tz):
        m = np.identity(4)
        m[0, 3] = tx
        m[1, 3] = ty
        m[2, 3] = tz
        return Matrix4x4(m)

    @staticmethod
    def scale(sx, sy, sz):
        m = np.identity(4)
        m[0, 0] = sx
        m[1, 1] = sy
        m[2, 2] = sz
        return Matrix4x4(m)

    @staticmethod
    def rotation_x(angle_rad):
        c = math.cos(angle_rad)
        s = math.sin(angle_rad)
        m = np.identity(4)
        m[1, 1] = c
        m[1, 2] = -s
        m[2, 1] = s
        m[2, 2] = c
        return Matrix4x4(m)

    @staticmethod
    def rotation_y(angle_rad):
        c = math.cos(angle_rad)
        s = math.sin(angle_rad)
        m = np.identity(4)
        m[0, 0] = c
        m[0, 2] = s
        m[2, 0] = -s
        m[2, 2] = c
        return Matrix4x4(m)

    @staticmethod
    def rotation_z(angle_rad):
        c = math.cos(angle_rad)
        s = math.sin(angle_rad)
        m = np.identity(4)
        m[0, 0] = c
        m[0, 1] = -s
        m[1, 0] = s
        m[1, 1] = c
        return Matrix4x4(m)

    def __repr__(self):
        return f"Matrix4x4(\n{self.data}\n)"

# --- LIGHT 3D (basic) ---
@dataclass
class Light3D:
    position: Vector3D
    intensity: float = 1.0
    color: tuple = (1.0, 1.0, 1.0)  # RGB normalized

    def __repr__(self):
        return f"Light3D(pos={self.position}, intensity={self.intensity}, color={self.color})"

# --- MATERIAL (diffuse + specular) ---
@dataclass
class Material:
    diffuse_color: tuple = (1.0, 1.0, 1.0)
    specular_color: tuple = (1.0, 1.0, 1.0)
    shininess: float = 32.0

# --- OBJECT 3D: Vertices + Faces (triangles) ---
class Object3D:
    def __init__(self, vertices: list[Vector3D], faces: list[tuple[int,int,int]], material: Material = None):
        self.vertices = vertices
        self.faces = faces
        self.material = material if material else Material()

    def transformed(self, matrix: Matrix4x4):
        new_verts = [matrix.transform_vector(v) for v in self.vertices]
        return Object3D(new_verts, self.faces, self.material)

    def bounding_box(self):
        xs = [v.x for v in self.vertices]
        ys = [v.y for v in self.vertices]
        zs = [v.z for v in self.vertices]
        return (min(xs), max(xs)), (min(ys), max(ys)), (min(zs), max(zs))

# --- CAMERA CLASS ---
class Camera:
    def __init__(self, position: Vector3D, target: Vector3D, up=Vector3D(0,1,0), fov_deg=60, aspect=1.0, near=0.1, far=1000):
        self.position = position
        self.target = target
        self.up = up
        self.fov_deg = fov_deg
        self.aspect = aspect
        self.near = near
        self.far = far
        self.view_matrix = Rape3D.look_at(position, target, up)
        self.projection_matrix = Rape3D.perspective(fov_deg, aspect, near, far)

    def update(self, position=None, target=None):
        if position:
            self.position = position
        if target:
            self.target = target
        self.view_matrix = Rape3D.look_at(self.position, self.target, self.up)

# --- Rape3D main utility class ---
class Rape3D:
    Vector3D = Vector3D
    Matrix4x4 = Matrix4x4
    Light3D = Light3D
    Material = Material
    Object3D = Object3D
    Camera = Camera

    @staticmethod
    def is_face_visible(face_normal: Vector3D, camera_position: Vector3D, face_point: Vector3D):
        """
        Backface culling: True se face visível.
        """
        to_camera = (camera_position - face_point).normalize()
        dot = face_normal.dot(to_camera)
        return dot > 0

    @staticmethod
    def compute_face_normal(v0: Vector3D, v1: Vector3D, v2: Vector3D):
        """
        Calcula normal de face a partir de 3 vértices (Vector3D)
        """
        edge1 = v1 - v0
        edge2 = v2 - v0
        normal = edge1.cross(edge2).normalize()
        return normal

    @staticmethod
    def batch_culling(vertices_np: np.ndarray, faces_indices: np.ndarray, camera_pos_np: np.ndarray):
        """
        Backface culling usando numpy em batch.
        vertices_np: np.array shape (N, 3)
        faces_indices: np.array shape (M, 3) - índices de triângulos
        camera_pos_np: np.array (3,)

        Retorna lista booleana indicando visibilidade de cada face.
        """
        v0 = vertices_np[faces_indices[:, 0]]
        v1 = vertices_np[faces_indices[:, 1]]
        v2 = vertices_np[faces_indices[:, 2]]

        edge1 = v1 - v0
        edge2 = v2 - v0
        normals = np.cross(edge1, edge2)
        norm_len = np.linalg.norm(normals, axis=1, keepdims=True)
        normals = normals / np.clip(norm_len, 1e-8, None)  # evita div/0

        to_camera = camera_pos_np - v0
        to_camera_norm = to_camera / np.linalg.norm(to_camera, axis=1, keepdims=True)

        dots = np.einsum('ij,ij->i', normals, to_camera_norm)
        return dots > 0

    @staticmethod
    def transform_vectors(matrix: Matrix4x4, vectors: list[Vector3D]):
        """
        Aplica transformação matricial (Matrix4x4) a uma lista de Vector3D,
        retornando np.array shape (N, 3)
        """
        v_np = np.array([v.to_np() for v in vectors])
        v_homo = np.hstack([v_np, np.ones((v_np.shape[0], 1))])
        transformed = (matrix.data @ v_homo.T).T
        return transformed[:, :3]

    @staticmethod
    def look_at(eye: Vector3D, target: Vector3D, up: Vector3D = Vector3D(0,1,0)):
        """
        Gera matriz lookAt para câmera (direção, lado e up)
        """
        zaxis = (eye - target).normalize()      # forward
        xaxis = up.cross(zaxis).normalize()     # right
        yaxis = zaxis.cross(xaxis).normalize()  # up recalculado

        m = np.identity(4)
        m[0, 0] = xaxis.x
        m[0, 1] = xaxis.y
        m[0, 2] = xaxis.z
        m[1, 0] = yaxis.x
        m[1, 1] = yaxis.y
        m[1, 2] = yaxis.z
        m[2, 0] = zaxis.x
        m[2, 1] = zaxis.y
        m[2, 2] = zaxis.z

        m[0, 3] = -xaxis.dot(eye)
        m[1, 3] = -yaxis.dot(eye)
        m[2, 3] = -zaxis.dot(eye)
        return Matrix4x4(m)

    @staticmethod
    def perspective(fov_deg, aspect, near, far):
        """
        Matriz perspectiva padrão (OpenGL style)
        """
        f = 1.0 / math.tan(math.radians(fov_deg) / 2)
        m = np.zeros((4,4))
        m[0, 0] = f / aspect
        m[1, 1] = f
        m[2, 2] = (far + near) / (near - far)
        m[2, 3] = (2 * far * near) / (near - far)
        m[3, 2] = -1.0
        return Matrix4x4(m)

    @staticmethod
    def phong_lighting(point: Vector3D, normal: Vector3D, camera_pos: Vector3D, light: Light3D, material: Material):
        """
        Calcula cor do ponto com modelo Phong simplificado.
        """
        # normalize tudo
        n = normal.normalize()
        l = (light.position - point).normalize()
        v = (camera_pos - point).normalize()

        # Diffuse
        diff = max(n.dot(l), 0.0)
        diffuse = tuple(diff * c * light.intensity for c in material.diffuse_color)

        # Specular
        reflect = (n * (2 * n.dot(l)) - l).normalize()
        spec_angle = max(reflect.dot(v), 0.0)
        spec = math.pow(spec_angle, material.shininess)
        specular = tuple(spec * c * light.intensity for c in material.specular_color)

        # Final color clamp 0..1
        r = min(diffuse[0] + specular[0], 1.0)
        g = min(diffuse[1] + specular[1], 1.0)
        b = min(diffuse[2] + specular[2], 1.0)
        return (r, g, b)

    @staticmethod
    def create_cube(size=1.0, center=Vector3D(0,0,0), material=None):
        """
        Cria cubo unitário centrado em center.
        """
        hs = size / 2
        verts = [
            Vector3D(center.x - hs, center.y - hs, center.z - hs),
            Vector3D(center.x + hs, center.y - hs, center.z - hs),
            Vector3D(center.x + hs, center.y + hs, center.z - hs),
            Vector3D(center.x - hs, center.y + hs, center.z - hs),
            Vector3D(center.x - hs, center.y - hs, center.z + hs),
            Vector3D(center.x + hs, center.y - hs, center.z + hs),
            Vector3D(center.x + hs, center.y + hs, center.z + hs),
            Vector3D(center.x - hs, center.y + hs, center.z + hs),
        ]
        # Faces (triangles) - 12 triângulos (2 por face)
        faces = [
            (0,1,2), (0,2,3),  # back
            (4,6,5), (4,7,6),  # front
            (0,4,5), (0,5,1),  # bottom
            (3,2,6), (3,6,7),  # top
            (1,5,6), (1,6,2),  # right
            (0,3,7), (0,7,4),  # left
        ]
        return Object3D(verts, faces, material)

    @staticmethod
    def create_sphere(radius=1.0, lat_segments=12, lon_segments=24, center=Vector3D(0,0,0), material=None):
        """
        Gera esfera em triangulos simples (lat/lon segmentation)
        """
        verts = []
        faces = []

        for lat in range(lat_segments + 1):
            theta = lat * math.pi / lat_segments
            sin_theta = math.sin(theta)
            cos_theta = math.cos(theta)

            for lon in range(lon_segments + 1):
                phi = lon * 2 * math.pi / lon_segments
                sin_phi = math.sin(phi)
                cos_phi = math.cos(phi)

                x = center.x + radius * sin_theta * cos_phi
                y = center.y + radius * cos_theta
                z = center.z + radius * sin_theta * sin_phi
                verts.append(Vector3D(x,y,z))

        for lat in range(lat_segments):
            for lon in range(lon_segments):
                first = lat * (lon_segments + 1) + lon
                second = first + lon_segments + 1
                faces.append((first, second, first + 1))
                faces.append((second, second + 1, first + 1))

        return Object3D(verts, faces, material)

    @staticmethod
    def wireframe_edges(object3d: Object3D):
        """
        Retorna lista de arestas (tupla de dois Vector3D) para desenhar wireframe
        """
        edges = set()
        for f in object3d.faces:
            edges.add(tuple(sorted([f[0], f[1]])))
            edges.add(tuple(sorted([f[1], f[2]])))
            edges.add(tuple(sorted([f[2], f[0]])))
        return [(object3d.vertices[e[0]], object3d.vertices[e[1]]) for e in edges]

    @staticmethod
    def interpolate_vertex_normal(vertex_idx, faces, vertices):
        """
        Gera normal interpolada do vértice pelo average das normais das faces adjacentes.
        """
        adjacent_normals = []
        for f in faces:
            if vertex_idx in f:
                n = Rape3D.compute_face_normal(vertices[f[0]], vertices[f[1]], vertices[f[2]])
                adjacent_normals.append(n)
        if not adjacent_normals:
            return Vector3D(0,0,0)
        avg = Vector3D(
            sum(n.x for n in adjacent_normals) / len(adjacent_normals),
            sum(n.y for n in adjacent_normals) / len(adjacent_normals),
            sum(n.z for n in adjacent_normals) / len(adjacent_normals),
        ).normalize()
        return avg

    @staticmethod
    def bounding_box_debug(object3d: Object3D):
        """
        Retorna vértices dos 8 cantos da bounding box para debug visual
        """
        (xmin, xmax), (ymin, ymax), (zmin, zmax) = object3d.bounding_box()
        return [
            Vector3D(xmin, ymin, zmin),
            Vector3D(xmax, ymin, zmin),
            Vector3D(xmax, ymax, zmin),
            Vector3D(xmin, ymax, zmin),
            Vector3D(xmin, ymin, zmax),
            Vector3D(xmax, ymin, zmax),
            Vector3D(xmax, ymax, zmax),
            Vector3D(xmin, ymax, zmax),
        ]
