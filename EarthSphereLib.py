from math import *
import numpy as np
import math
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


class polus:
    pn = 0.
    pe = 0.
    def __init__(self, pn, pe):
        self.pn = pn
        self.pe = pe

class gps_point:
    #local
    Ve = 0.
    Vn = 0.
    lat = 0.
    long = 0.

    #global
    Va = 0.
    Vx = 0.
    Vy = 0.
    Vz = 0.
    x = 0.
    y = 0.
    z = 0.

    pole = polus(-999,-999)
    def __init__(self, lat, long):
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

        if self.Vn == 0:
            if self.Ve > 0:
                self.Va = math.pi/2
            else:
                self.Va = -math.pi/2
        elif self.Ve == 0:
                if self.Vn > 0:
                    self.Va = 0
                else:
                    self.Va = math.pi
        else:
             self.Va = math.atan(self.Ve / self.Vn)
             if self.Vn < 0 and self.Ve > 0:
                  self.Va = self.Va + math.pi
             if self.Vn < 0 and self.Ve < 0:
                  self.Va = self.Va - math.pi

def reverse(arrayOfSpeeds):
    point1 = arrayOfSpeeds[0]
    point2 = arrayOfSpeeds[1]
    point3 = arrayOfSpeeds[2]
    find_pole = False

    if point1.long > point2.long:
        point1, point2 = point2, point1

    x1 = point1.lat / 180 * math.pi
    y1 = point1.long / 180 * math.pi
    x2 = point2.lat / 180 * math.pi
    y2 = point2.long / 180 * math.pi
    
    if point1.Va > 0:
        a1 = math.pi - point1.Va
    else:
        a1 = abs(point1.Va)
    
    if point2.Va > 0:
        a2 = math.pi - point2.Va
    else:
        a2 = abs(point2.Va)


    g1 = a1 - math.pi / 2
    g2 = math.pi / 2 - a2

    D = math.sin(x1) * math.sin(x2) + math.cos(x1) * math.cos(x2) * math.cos(y2 - y1)
    if (abs(D) >= 1):
        return None
    D = math.atan(-D / math.sqrt(-D * D + 1)) + 2 * math.atan(1)

    F1 = math.sin(math.pi / 2 - x2) * math.sin(y2 - y1) / math.sin(D)
    F2 = math.sin(math.pi / 2 - x1) * math.sin(y2 - y1) / math.sin(D)

    if (abs(F1) >= 1) or (abs(F2) >= 1):
        return None
    
    F1 = math.atan(F1 / math.sqrt(-F1 * F1 + 1))
    if g1 < 0:
        F1 = -F1
    F2 = math.atan(F2 / math.sqrt(-F2 * F2 + 1))
    if F1 > 0:
        F2 = -F2

    h1 = F1 + g1
    h2 = F2 + g2
    z1 = math.atan(math.sin(D) / (math.sin(h1) / math.tan(h2) + math.cos(h1) * math.cos(D)))
    
    if g1 < 0:
        z1 = -z1

    q = math.cos(z1) * math.cos(math.pi / 2 - x1) + math.sin(z1) * math.sin(math.pi / 2 - x1) * math.cos(g1)
    if (abs(q) >= 1):
        return None
    q = math.atan(-q / math.sqrt(-q * q + 1)) + 2 * math.atan(1)
    arf1 = math.sin(z1) * math.sin(g1) / math.sin(q)
    if (abs(arf1) >= 1):
        return None
    arf1 = math.atan(arf1 / math.sqrt(-arf1 * arf1 + 1))

    pn = math.pi / 2 - q
    pe = y1 - arf1
    
    if q < 0:
        return None
    
    d = math.sin(x1) * math.sin(pn) + math.cos(x1) * math.cos(pn) * math.cos(pe - y1)
    if abs(d) >= 1:
        return None
    d = math.atan(-d / math.sqrt(-d * d + 1)) + 2 * math.atan(1)
    w1 = math.sqrt(point1.Ve**2 + point1.Vn ** 2) / (11.12 * math.sin(d))
    point3 = gps_point(0, 0)
    if (point3.y == pe):
        j = math.pi / 2 
    else:
        j = math.atan((point3.x - pn) / (point3.y - pe))
    if (point3.Va > (-math.pi / 2 - j)) and (point3.Va < (math.pi / 2 - j)):
        i = 1
    else:
        i = -1
    if (point3.y - pe) < 0:
        i = -i
    wp = i * w1
    return pe, pn


def reverse_old(arrayOfSpeeds):
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


