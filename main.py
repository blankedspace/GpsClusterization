import copy
import li_method
import EarthSphereLib
import folium
import Clastrization
import random
import math
from sklearn.cluster import KMeans
def open_file(filename):
    with open(filename) as f:
        lines = f.readlines()
    return lines

def divide_string_by_space(string):
    return string.split('\t')

world_map = folium.Map()
def draw_map_of_world(points, color):

    for point in points:
        # draw arrow of gps speed
        magnitude = 0.01
        folium.PolyLine([[point.lat, point.long],
                         [point.lat + point.Vn * magnitude, point.long + point.Ve * magnitude]],
                         color=color, weight=4.5, opacity=1).add_to(world_map)
        folium.CircleMarker(color=color, fill=True, radius=2, location=[point.lat, point.long], popup="{} {} {} {}".format(point.lat, point.long, point.Vn, point.Ve)).add_to(world_map)
        
        if len(points) >= 3:
            down_hemi_circle = -1
            if point.Vn < 0:
                down_hemi_circle = 0
            point = copy.deepcopy(point)
            gamma, phi = Clastrization.reverse_old(points)
            
            point.set_polus(polus_lat=math.degrees(gamma), polus_long= math.degrees(phi))
            folium.PolyLine([[point.lat, point.long],
                        [point.lat + point.Vn * magnitude, point.long + point.Ve * magnitude]],
                        color='red', weight=1.5, opacity=1).add_to(world_map)
        # draw point at line end


lines = open_file("D:/newest_job/input_data/inputdata_Mclusky.txt")
# File format: 
#long	lat	Ve	Vn
#46.37	39.51	3.3	9.6
#45.66	39.84	4.6	10.1
#45.14	40.91	4	7.4
values = []
map_index_dict = {"long": 0, "lat": 1, "Ve": 2, "Vn": 3}
data_set = {}
points = []
for line in lines[1:]:
    values = divide_string_by_space(line)
    data_set["long"] = float(values[map_index_dict["long"]])
    data_set["lat"] = float(values[map_index_dict["lat"]])
    data_set["Ve"] = float(values[map_index_dict["Ve"]])
    data_set["Vn"] = float(values[map_index_dict["Vn"]])
    point = EarthSphereLib.gps_point(data_set["lat"], data_set["long"])
    point.set_velocity(data_set["Vn"], data_set["Ve"])
    points.append(point)

clusters = []
method = 2
if method==0:
    Clastrization.ERR_RATE = 100
    for i in range(10):
        cpy = copy.deepcopy(points)
        claster_points = Clastrization.methodOne(cpy)
        if claster_points is None:
            break
        clusters.append(claster_points)
        i = 0
        while i < len(points):
            for p in claster_points:
                if p.Ve == points[i].Ve and p.Vn == points[i].Vn and p.lat == points[i].lat:
                    points.pop(i)
                    i-=1
                    break
            i+=1
        Clastrization.DISTANCE += 1
        if(len(points) < 15):
            break
    #self.claster.append(self.points)

elif method==1:
    poluses = li_method.calculate(points)
    i = -1
    for polus in poluses:
        i += 1
        clusters.append([])
        for point in points:
            if point.pole == polus:
                clusters[i].append(point)
elif method==2:
    p_list = []
    for p in points:
        p_list.append([p.lat, p.long, p.Vn, p.Ve])
    # Assuming your data is stored in a variable called 'points'
    for i in range(30):
        clusters.append([])
    kmeans = KMeans(n_clusters=30)
    clusters_id = kmeans.fit_predict(p_list)
    for c in range(len(clusters_id)):
        clusters[clusters_id[c]].append(points[c])

for cluster in clusters:

    r = lambda: random.randint(0,255)
    color = ('#%02X%02X%02X' % (r(),r(),r()))
    draw_map_of_world(cluster, color)
world_map.save("map.html")
test = 1
