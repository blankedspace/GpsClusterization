from EarthSphereLib import *
import math

def calculate(points):
    poluses = []

    points_length = len(points)

    for point1 in range(points_length - 2):
        for point2 in range(point1 + 1, points_length - 1):
                point3 = point2 - 1
                polus = find_pole(points[point1], points[point2])
                if polus is not None:
                    poluses.append(polus)
                    points[point1].pole = polus
                    points[point2].pole = polus
    return poluses







def find_pole(point1, point2):  # type: (gps_point, gps_point, gps_point) -> bool:
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
    point3 = point2
    if in_pole(wp, polus(pn, pe), point3):
        find_pole = True
        return polus(pn, pe)
    return None



def in_pole(wp, polus, point3):
    in_pole = False
    x3 = point3.lat / 180 * math.pi
    y3 = point3.long / 180 * math.pi
    if point3.Va > 0:
        a3 = math.pi - point3.Va
    else:
        a3 = abs(point3.Va)
    
    d3 = math.sin(x3) * math.sin(polus.pn) + math.cos(x3) * math.cos(polus.pn) * math.cos(polus.pe - y3)
    if abs(d3) >= 1:
        return
    d3 = math.atan(-d3 / math.sqrt(-d3 * d3 + 1)) + 2 * math.atan(1)
    w3 = math.sqrt(point3.Ve ** 2 + point3.Vn ** 2) / (11.12 * math.sin(d3))
    

    if y3 == polus.pe:
        j = math.pi / 2
    else:
        j = math.atan((x3 - polus.pn) / (y3 - polus.pe))
    
    if (point3.Va > (-math.pi / 2 - j)) and (point3.Va < (math.pi / 2 - j)):
        i = 1
    else:
        i = -1
    
    if (y3 - polus.pe) < 0:
        i = -i
    
    w3 = w3 * i
    
    arf3 = math.atan(math.sin(y3 - polus.pe) / (math.sin(math.pi / 2 - x3) / math.tan(math.pi / 2 - polus.pn) - math.cos(math.pi / 2 - x3) * math.cos(y3 - polus.pe)))
    arf = abs(arf3)
    
    arf3 = arf3 + math.pi / 2
    
    if polus.pn > x3:
        if w3 < 0:
            arf3 = -abs(arf3)
        else:
            arf3 = abs(arf3)
    else:
        if w3 < 0:
            arf3 = abs(arf3)
        else:
            arf3 = -abs(arf3)
    error_a = 0.01
    error_v = 0.01
    wp = 1
    if (abs(arf3 - point3.Va) < error_a) and (abs((w3 - wp) / wp) < error_v) and (abs((w3 - wp) / w3) < error_v):
        in_pole = True

    return in_pole
