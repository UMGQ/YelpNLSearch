import math

# calculate the distance between two lat lng points in miles
# point: (lat, lng)

def toRad(degree):
    return degree*math.pi/180

def distance(p1, p2):
    R = 3963
    dLat = toRad(p2[0] - p1[0])
    dLng = toRad(p2[1] - p1[1])
    lat1 = toRad(p1[0])
    lat2 = toRad(p2[0])

    a = math.sin(dLat/2)*math.sin(dLat/2) + math.sin(dLng/2)*math.sin(dLng/2)*math.cos(lat1)*math.cos(lat2)
    c = 2*math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = R*c

    return d

"""
p1 = (42.280826, -83.743038) # ann arbor
p2 = (41.878114, -87.629798) # chicago
print distance(p1, p2)
"""
