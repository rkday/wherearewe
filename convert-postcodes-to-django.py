import sys
sys.path.append("./django/wherearewe")
import wherearewe.settings
from django.core.management import setup_environ
setup_environ(wherearewe.settings)
import waw_app.models

import re
import time
import MySQLdb
import sys
from shapely.geometry.polygon import LinearRing,Polygon
from shapely.geometry import Point
from ostn02python.eastings_to_decimal_degrees import postcodes_to_points
from utils import get_constituency_list


def guess_unknown_postcodes(unknowns, constituencies):
    postcode_constituencies = {}
    for postcode, point in unknowns:
        best_guess = None
        min_distance_so_far = 1000000 # impossibly high number to start with
        for constituency in constituencies.keys():
            if constituencies[constituency].distance(point) < min_distance_so_far:
                best_guess = constituency
                min_distance_so_far = constituencies[constituency].distance(point)
        postcode_constituencies[postcode] = best_guess
    return postcode_constituencies

def map_postcodes_to_constituencies(postcode_file, constituencies, verbose=False):
    with open(postcode_file) as f:
        postcode_constituencies = {}
        unknowns = []
        last_constituencies = [constituencies.keys()[0]]*5
        n = 0

        for postcode,point in postcodes_to_points(f):
            n += 1
            
            # The postcodes are in alphabetical order - so it's relatively likely
            # that this postcode will be in the same constituency as one of the
            # last five postcodes. Check those first.
            
            for guess in last_constituencies:
                if constituencies[guess].contains(point):
                    last_constituencies.remove(guess)
                    postcode_constituencies[postcode] = guess
                    last_constituencies.append(guess)
            
            # If that didn't work, we should loop through every constituency.

            if postcode not in postcode_constituencies:
                for constituency in constituencies.keys():
                    if constituencies[constituency].contains(point):
                        postcode_constituencies[postcode] = constituency
                        last_constituencies.append(constituency)
                        break

            # Sometimes we don't get a result, usually because of postcodes on
            # Scottish islands which fall outside the constituency boundaries we're
            # using. Collect those postcodes into a list of unknowns, for further
            # processing (eg. a lookup on http://parliament.uk or a best guess by
            # distance).
            if postcode not in postcode_constituencies:
                unknowns.append((postcode, point))
            
            if verbose and 0 == (n % 1000):
                print("%d postcodes processed" % n)
            
    return (postcode_constituencies, unknowns)

if __name__ == "__main__":
    constituencies = get_constituency_list("constituencies.kml")
    (postcode_constituencies, unknowns) = map_postcodes_to_constituencies("all_postcodes.csv", constituencies)
    postcode_constituencies.update(guess_unknown_postcodes(unknowns, constituencies))
    
    for postcode in postcode_constituencies:
        this_constituency = waw_app.models.Constituency.objects.filter(name__exact=postcode_constituencies[postcode])[0]
        new_postcode = waw_app.models.Postcode.objects.create(postcode=postcode, constituency=this_constituency)
        new_postcode.save()

