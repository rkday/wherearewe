import shapefile
import os
from shapely.geometry.polygon import LinearRing, Polygon
from shapely.geometry import Point
from ostn02python.OSGB import grid_to_ll
from warnings import warn
import csv

def get_constituency_list():
    r = shapefile.Reader("raw_data/westminster_const_region.shp")
    rs = r.shapeRecords()
    constituencies = {}
    for j, rec in enumerate(rs):
        name = " ".join(rec.record[0].split(" ")[:-2]).replace(".", "")
        coords = []
        for i in range(len(rec.shape.parts)):
            start = rec.shape.parts[i]
            if i == len(rec.shape.parts)-1:
                end = None
            else:
                end = rec.shape.parts[i+1]
            coords.append(_transform_points(rec.shape.points[start:end]))
        constituencies[name] = Polygon(coords[0], coords[1:])
    return constituencies

def postcodes_to_points(csv_file):
    postcodes_not_listed = []
    postcodes = {}
    reader = csv.reader(csv_file)
    for row in reader:
        try:
            lat, lng = grid_to_ll(float(row[2]), float(row[3]))
        except:
            warn("Postcode %s not given a location, using a nearby value" % row[0])
        yield [row[0], Point(lat, lng)]

def _parse_coords(str_coords):
    coords_iter = str_coords.split(" ")
    result_coords = []
    for pair in coords_iter:
        i, j = pair.split(",")
        result_coords.append((float(i), float(j)))
    return result_coords

def _transform_points(points):
    return [grid_to_ll(*point) for point in points]
