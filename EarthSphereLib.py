from math import *
import numpy as np

def to_decart(lat, long):
    long = radians(long)
    lat = radians(lat)
    x = np.cos(lat) * np.cos(long)
    y = np.cos(lat) * np.sin(long)
    z = np.sin(lat)
    return [x, y, z]

def from_decart(y, z):
    lat = asin(z)
    lon = asin(y/cos(lat))
    return gps_point(degrees(lat), degrees(lon))

def globalToLocalMatrix(gamma, phi):
    gamma = radians(gamma)
    phi = radians(phi)
    T = [[-sin(gamma)*cos(phi), -sin(gamma)*sin(phi), cos(gamma)],
         [-sin(phi), cos(phi), 0],
         [-cos(gamma)*cos(phi), -cos(gamma)*sin(phi), -sin(gamma)]]
    return T
class gps_point:
    #local
    Ve = 0.
    Vn = 0.
    lat = 0.
    long = 0.

    #global
    Vx = 0.
    Vy = 0.
    Vz = 0.
    x = 0.
    y = 0.
    z = 0.
    def __init__(self, lat, long,):
        self.lat = lat
        self.long = long

        xyz = to_decart(lat, long)
        self.x = xyz[0]
        self.y = xyz[1]
        self.z = xyz[2]

    # angular_speed * RADIUS ?
    def set_polus(self, polus_lat, polus_long):
        v = radians(0.2069) *6371* np.cross(np.array(to_decart(polus_lat, polus_long)),
                     np.array(to_decart(self.lat, self.long)))
        t = globalToLocalMatrix(self.lat, self.long)
        self.Vx = v[0]
        self.Vy = v[1]
        self.Vz = v[2]
        v = np.dot(t, v)

        self.Vn = v[0]
        self.Ve = v[1]
        self.Vd = v[2]

    def set_velocity(self,Vn, Ve):
        self.Vn = Vn
        self.Ve = Ve

        t = np.linalg.inv(globalToLocalMatrix(self.lat, self.long))
        v = [Vn, Ve, 0]
        global_v = np.dot(t, v)

        self.Vx = global_v[0]
        self.Vy = global_v[1]
        self.Vz = global_v[2]

def reverse(arrayOfSpeeds):
        # type: ([gps_point]) -> None
    A = 0
    B = 0
    C = 0

    a = 0
    b = 0
    c = 0

    D1 = 0
    D2 = 0
    D3 = 0
    for p in arrayOfSpeeds:
        A += p.x * p.x + p.y * p.y
        B += p.y * p.y + p.z * p.z
        C += p.x * p.x + p.z * p.z

        a += p.x * p.y
        b += p.y * p.z
        c += p.z * p.x

        D1 += p.Vz * p.y - p.Vy * p.z
        D2 += p.Vx * p.z - p.Vz * p.x
        D3 += p.Vy * p.x - p.Vx * p.y

    M1 = np.array([[B, -a, -c], [-a, C, -b], [-c, -b, A]])
    v1 = np.array([D1, D2, D3])
    ans = 0
    try:
        ans = np.linalg.solve(M1, v1)
    except Exception:
        return 999, 999
    wx = ans[0]
    wy = ans[1]
    wz = ans[2]
    tang = wz / sqrt(wx * wx + wy * wy)
    tanphi = wy / wx

    gamma = atan(tang)
    phi = atan(tanphi)

    return gamma, phi
