from EarthSphereLib import *
import random
import math
import copy

MAX_ITERATIONS = 1e3
ERR_RATE = 20 #percent
DISTANCE = 1 #percent

ONE = 0
TWO = 1
THREE = 2

def GetThreeRandomPoints(arrayOfSpeeds):
        # type: ([gps_point]) -> None
    close_by = False
    i = 0
    while not close_by and i < MAX_ITERATIONS:
        arr = []
        strt = random.randint(0,len(arrayOfSpeeds)-8)
        strt_point = arrayOfSpeeds[strt]
        point = arrayOfSpeeds[strt + random.randint(0,7)]
        if(get_change(point.lat,strt_point.lat) > DISTANCE or get_change(point.long,strt_point.long) > DISTANCE):
            continue 
        arr.append(point)
        point = arrayOfSpeeds[strt + random.randint(0,7)]
        if(get_change(point.lat,strt_point.lat) > DISTANCE or get_change(point.long,strt_point.long) > DISTANCE):
            continue 
        arr.append(point)
        return arr

STRT = 0
def GetThreeRandomPointsAndPop(arrayOfSpeeds):
    # type: ([gps_point]) -> None
    close_by = False
    i = 0
    global STRT
    STRT += 1
    if(STRT >= len(arrayOfSpeeds)-9):
        STRT = 0
    arr = []
    strt = STRT
    strt_point = arrayOfSpeeds.pop(strt)
    arr.append(strt_point)
    point = arrayOfSpeeds.pop(random.randint(strt,len(arrayOfSpeeds) - 1))

    arr.append(point)
    point = arrayOfSpeeds.pop(random.randint(strt,len(arrayOfSpeeds) - 1))

    arr.append(point)
    return arr

def GetThreeRandomPointsAndPop2(arrayOfSpeeds):
    # type: ([gps_point]) -> None
    global ONE
    global TWO
    global THREE
    arr = []


    ONE += 1 
    if(ONE >= len(arrayOfSpeeds)-1):
        ONE = 0
        TWO += 1
    if(TWO >= len(arrayOfSpeeds)-1):
        TWO = 0
        THREE += 1
    if(THREE >= len(arrayOfSpeeds)-2):
        print('ALL')
        return 0
    
    if(get_change(arrayOfSpeeds[ONE].lat,arrayOfSpeeds[TWO].lat) > DISTANCE or get_change(arrayOfSpeeds[ONE].long,arrayOfSpeeds[TWO].long) > DISTANCE):
        return 1
    if(get_change(arrayOfSpeeds[TWO].lat,arrayOfSpeeds[THREE].lat) > DISTANCE or get_change(arrayOfSpeeds[TWO].long,arrayOfSpeeds[THREE].long) > DISTANCE):
        return 1
    
    arr.append(arrayOfSpeeds.pop(ONE))
    arr.append(arrayOfSpeeds.pop(TWO))
    arr.append(arrayOfSpeeds.pop(THREE))
    return arr

def GetThreeRandomPoints2(arrayOfSpeeds): # type: ([gps_point]) -> None
    global ONE
    global TWO
    global THREE
    arr = []

    arr.append(arrayOfSpeeds[ONE])
    arr.append(arrayOfSpeeds[TWO])
    arr.append(arrayOfSpeeds[THREE])
    ONE += 1 
    if(ONE == len(arrayOfSpeeds)):
        ONE = 0
        TWO += 1
    if(TWO == len(arrayOfSpeeds)):
        TWO = 0
        THREE += 1
    if(THREE == len(arrayOfSpeeds)):
        return 0
    return arr

def get_change(current, previous):
    if current == previous:
        return 0
    try:
        return (abs(current - previous) / abs(previous)) * 100.0
    except ZeroDivisionError:
        return 0
    
def ValidatePoints(Speeds,Polus_lat,Polus_long): # type: ([gps_point],float,float) -> bool
    valid = 0
    global ERR_RATE
    for p in Speeds:
        point = copy.deepcopy(p)
        point.set_polus(polus_lat=Polus_lat,polus_long=Polus_long)
        if(get_change(point.Ve,p.Ve) < ERR_RATE and get_change(point.Vn,p.Vn) < ERR_RATE):
            valid += 1
            if valid == len(Speeds):
                return True
    return False




Gl_speeds = 0
def AddRestOfPoints(points_in_block,i): # type: ([gps_point],int) -> ([gps_point], bool)
    
    points = copy.deepcopy(points_in_block)
    points.append(Gl_speeds[0])
    if Gl_speeds[0] == None:
         del Gl_speeds[0]
         return points_in_block, False
    del Gl_speeds[0]
    gamma, phi = reverse(points_in_block)
    gamma, phi = reverse(points)
    if(ValidatePoints([points[-1]],math.degrees(gamma),math.degrees(phi))):
        return points, True
        
    return points_in_block, False


def methodOne(arrayOfSpeeds): # type: ([gps_point]) -> None
    global Gl_speeds
    found_block = False
    i = 0

    if(len(arrayOfSpeeds) < 9):
        return []

    while not found_block and i < MAX_ITERATIONS:
        i += 1
        points = GetThreeRandomPoints(arrayOfSpeeds)
        if points == 0:
            return
        gamma, phi = reverse(points)
        if(ValidatePoints(points,math.degrees(gamma),math.degrees(phi))):
            found_block = True
    
    adding_points = 9999

    Gl_speeds = copy.deepcopy(arrayOfSpeeds)
    end = len(arrayOfSpeeds)
    i = 0
    while i < end:
        points, success = AddRestOfPoints(points,i)
        i+=1
        if success:
            if i >= len(arrayOfSpeeds):
                break
            del arrayOfSpeeds[0]
            

    if found_block == False:
        return None
    return points


def methodThree(arrayOfSpeeds): # type: ([gps_point]) -> None
    global Gl_speeds
    global ONE
    global TWO
    global THREE
    ONE = 0
    TWO = 0
    THREE = 0
    Gl_speeds = copy.deepcopy(arrayOfSpeeds)
    found_block = False
    i = 0

    if(len(arrayOfSpeeds) < 9):
        return []
    
    blocks = []
    while i < MAX_ITERATIONS:
        found_block = False
        while not found_block and i < MAX_ITERATIONS and len(arrayOfSpeeds) > 9:
         
            points = GetThreeRandomPointsAndPop2(arrayOfSpeeds)
            if points == 0:
                i = MAX_ITERATIONS
                break
            if points == 1:
                continue
            i += 1
            gamma, phi = reverse(points)
            if(ValidatePoints(points,math.degrees(gamma),math.degrees(phi))):
                found_block = True
                print(len(arrayOfSpeeds))
                i = 0
                blocks.append(points)
                ONE = 0
                TWO = 0
                THREE = 0
            else:
                arrayOfSpeeds.extend(points)
        if isinstance(points,list):
            blocks.append(points)
        if len(arrayOfSpeeds) <= 9:
            break
    if len(blocks) == 0:
        return []
    smallest = 1999
    smallest_points = 0
    for b in blocks:
        gamma, phi = reverse(b)
        check_val = 0
        for p in b:
            point = copy.deepcopy(p)
            point.set_polus(polus_lat=math.degrees(gamma),polus_long=math.degrees(phi))
            check_val += get_change(point.Ve,p.Ve) + get_change(point.Ve,p.Ve)
        
        if smallest > check_val:
            smallest = check_val
            smallest_points = b


    while len(Gl_speeds) > 0:
        smallest_points, success = AddRestOfPoints(smallest_points,i)


    return smallest_points
