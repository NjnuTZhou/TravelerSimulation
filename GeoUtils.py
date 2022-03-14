import math
import copy
from geopy.distance import geodesic


def distance(lnglat1, lnglat2):
    return geodesic((lnglat1[1], lnglat1[0]), (lnglat2[1], lnglat2[0])).m


def coord_to_str(join, coord):
    return str(coord[0]) + join + str(coord[1])


def get_route_id(id1, id2):
    return str(min(int(id1), int(id2))) + '_' + str(max(int(id1), int(id2)))


def get_ordered_route_section(id1, id2, mxl_routes):
    _id = get_route_id(id1, id2)
    if int(id1) < int(id2):
        route_section = mxl_routes[_id]
    else:
        route_section = list(reversed(mxl_routes[_id]))
    return copy.deepcopy(route_section)
