# Activity 3: 3D Coordinate Geometry and Bounding Volumes
import math, random


# ---------- Task 3.1: Classes ----------
class Point3D:
    def __init__(self, x: float, y: float, z: float):
        self.x, self.y, self.z = x, y, z

    def __add__(self, other):
        return Point3D(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Point3D(self.x - other.x, self.y - other.y, self.z - other.z)

    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other):
        return Point3D(self.y * other.z - self.z * other.y,
                       self.z * other.x - self.x * other.z,
                       self.x * other.y - self.y * other.x)

    def distance_sq_to(self, other):
        return (self.x - other.x)**2 + (self.y - other.y)**2 + (self.z - other.z)**2

    def distance_to(self, other):
        return math.sqrt(self.distance_sq_to(other))

    def octant(self):
        if self.x == 0 or self.y == 0 or self.z == 0:
            return 'on an axis or plane'
        names = {(1, 1, 1): 'I', (-1, 1, 1): 'II', (-1, -1, 1): 'III', (1, -1, 1): 'IV',
                 (1, 1, -1): 'V', (-1, 1, -1): 'VI', (-1, -1, -1): 'VII', (1, -1, -1): 'VIII'}
        sign = lambda v: 1 if v > 0 else -1
        return names[(sign(self.x), sign(self.y), sign(self.z))]

    def __repr__(self):
        return '(%g, %g, %g)' % (self.x, self.y, self.z)


class Sphere3D:
    def __init__(self, center: Point3D, radius: float):
        self.center = center
        self.radius = radius

    def contains_point(self, p):
        return self.center.distance_sq_to(p) <= self.radius**2

    def intersects_sphere(self, other):
        # compare squared values -> no math.sqrt needed
        return self.center.distance_sq_to(other.center) <= (self.radius + other.radius)**2


class AABB:
    def __init__(self, min_pt: Point3D, max_pt: Point3D):
        self.min_pt = min_pt
        self.max_pt = max_pt

    def intersects(self, other):
        # boxes overlap only if they overlap on x, y AND z
        return (self.min_pt.x <= other.max_pt.x and self.max_pt.x >= other.min_pt.x and
                self.min_pt.y <= other.max_pt.y and self.max_pt.y >= other.min_pt.y and
                self.min_pt.z <= other.max_pt.z and self.max_pt.z >= other.min_pt.z)


def sphere_from_equation(D, E, F, G):
    # x^2 + y^2 + z^2 + Dx + Ey + Fz + G = 0
    # completing the squares -> center (-D/2, -E/2, -F/2), r^2 = (D^2 + E^2 + F^2)/4 - G
    center = Point3D(-D / 2, -E / 2, -F / 2)
    radius = math.sqrt((D**2 + E**2 + F**2) / 4 - G)
    return Sphere3D(center, radius)


# ---------- Run all tasks ----------
print('TASK 3.1: Vector operations')
a, b = Point3D(1, 2, 3), Point3D(4, -5, 6)
print('  a =', a, '  b =', b)
print('  a + b =', a + b)
print('  a - b =', a - b)
print('  a . b =', a.dot(b))
print('  a x b =', a.cross(b))
print('  octant of (3, -4, 5) =', Point3D(3, -4, 5).octant())
print('  octant of (-3, -4, -5) =', Point3D(-3, -4, -5).octant())

print('\nTASK 3.2: Example 3 - distance from P(2, -1, 7) to Q(1, -3, 5)')
P, Q = Point3D(2, -1, 7), Point3D(1, -3, 5)
d = P.distance_to(Q)
print('  d = sqrt((1-2)^2 + (-3+1)^2 + (5-7)^2) = sqrt(1 + 4 + 4) = sqrt(9) =', d)
print('  d == 3.0 ?', d == 3.0)

print('\nTASK 3.3: Example 5 - x^2 + y^2 + z^2 + 4x - 6y + 2z + 6 = 0')
print('  (x^2 + 4x + 4) + (y^2 - 6y + 9) + (z^2 + 2z + 1) = -6 + 4 + 9 + 1')
print('  (x + 2)^2 + (y - 3)^2 + (z + 1)^2 = 8')
s = sphere_from_equation(4, -6, 2, 6)
print('  Center =', s.center, '  Radius = sqrt(8) = %.3f' % s.radius)

print('\nTASK 3.4: Broad-phase collision test with 100 random objects')
random.seed(1)
spheres, boxes = [], []
for i in range(50):
    c = Point3D(random.uniform(0, 100), random.uniform(0, 100), random.uniform(0, 100))
    spheres.append(Sphere3D(c, random.uniform(2, 8)))
for i in range(50):
    x, y, z = random.uniform(0, 90), random.uniform(0, 90), random.uniform(0, 90)
    size = random.uniform(4, 12)
    boxes.append(AABB(Point3D(x, y, z), Point3D(x + size, y + size, z + size)))

sphere_hits = 0
for i in range(len(spheres)):
    for j in range(i + 1, len(spheres)):
        if spheres[i].intersects_sphere(spheres[j]):
            sphere_hits += 1
            print('  Sphere %d hits Sphere %d' % (i, j))

box_hits = 0
for i in range(len(boxes)):
    for j in range(i + 1, len(boxes)):
        if boxes[i].intersects(boxes[j]):
            box_hits += 1
            print('  Box %d hits Box %d' % (i, j))

print('  Sphere pairs tested: %d, colliding: %d' % (50 * 49 // 2, sphere_hits))
print('  Box pairs tested:    %d, colliding: %d' % (50 * 49 // 2, box_hits))
