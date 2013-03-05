import sys
sys.path.append("./django/")
import mysite.settings

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")

from django.core.management import setup_environ
from django.db import transaction
setup_environ(mysite.settings)
import waw_app.models

import re
import time
import sys
from shapely.geometry.polygon import LinearRing,Polygon
from shapely.geometry import Point
from ostn02python.eastings_to_decimal_degrees import postcodes_to_points
from utils import get_constituency_list
from multiprocessing import Pool

def guess_constituency(postcode, point, constituencies):
    best_guess = None
    min_distance_so_far = 1000000 # impossibly high number to start with
    for constituency in constituencies.keys():
        if constituencies[constituency].distance(point) < min_distance_so_far:
            best_guess = constituency
            min_distance_so_far = constituencies[constituency].distance(point)
    return best_guess

@transaction.commit_on_success
def map_postcodes_to_constituencies(postcode_file, constituencies, ids):
    with open(postcode_file) as f:
        postcode_constituencies = {}
        unknowns = []
        last_constituencies = [constituencies.keys()[0]]*5
        n = 0

        for postcode,point in postcodes_to_points(f):
            constituency = None
            n += 1
            
            # The postcodes are in alphabetical order - so it's relatively
            # likely that this postcode will be in the same constituency as one
            # of the last five postcodes.  Check those first.

            for guess in reversed(last_constituencies):
                if constituencies[guess].contains(point):
                    last_constituencies.remove(guess)
                    constituency = guess
            
            # If that didn't work, we should loop through every constituency.

            if postcode not in postcode_constituencies:
                for possible_constituency in constituencies.keys():
                    if constituencies[possible_constituency].contains(point):
                        constituency = possible_constituency
                        break

            # Sometimes we don't get a result, usually because of postcodes on
            # Scottish islands which fall outside the constituency boundaries
            # we're using.  Make a best guess.

            if constituency is None:
                constituency = guess_constituency(postcode, point, constituencies)

            if constituency not in ids:
                ids[constituency] = waw_app.models.Constituency.objects.filter(
                    name__exact=constituency)[0]
            
            new_postcode = waw_app.models.Postcode.objects.create(
                postcode=postcode, constituency=ids[constituency])
            new_postcode.save()
            last_constituencies.append(constituency)

if __name__ == "__main__":
    constituencies = get_constituency_list()
    for file_name in os.listdir("./raw_data/postcode_files/"):
        print file_name
        base = time.time()
        map_postcodes_to_constituencies("".join(["./raw_data/postcode_files/", file_name]), constituencies, {})
        print (time.time() - base)
