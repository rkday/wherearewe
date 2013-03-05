from django.http import HttpResponse
from django.template.loader import get_template
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from django.core.exceptions import ObjectDoesNotExist
import django.db
from waw_app import models
import time
from django.db import transaction
from waw_app.utils import ColourCoordinator

def input_form(request):
        t = get_template('input_form.html')
        html = t.render(RequestContext(request, {}))
        return HttpResponse(html)

@transaction.commit_on_success()
def create_map(request):
    # Create a new map
    # FIXME: should fail more nicely when the name is already taken
    my_map = models.Map.objects.create(name=request.POST['mapname'])
    my_map.save()

    successes, failures = 0, 0

    p_objs = models.Postcode.objects
    cc_objs = models.ConstituencyCount.objects

    if 'postcodes' in request.POST and request.POST['postcodes']:
        # Convert postcodes into a standard format - e.g. "OX1 4dd" becomes
        # "OX14DD"
        postcodes = [line.replace(" ", "").upper() for line in request.POST['postcodes'].splitlines()]

        for line in postcodes:
            # Skip blank lines
            if len(line) == 0:
                continue

            # Find out which constituency this postcode is in
            try:
                constit = p_objs.filter(postcode__istartswith=line)[0].constituency_id
            except IndexError:
                failures += 1
                continue

            constit_count_qs = my_map.constituencycount_set.filter(constituency_id__exact=constit)

            # If we don't have a ConstituencyCount object for this map/constituency pair yet, create it
            if constit_count_qs:
                constit_count = constit_count_qs[0]
            else:
                constit_count = cc_objs.create(map=my_map, constituency_id=constit, count=0)
            
            # Increment the count in the ConstituencyCount
            constit_count.count += 1
            constit_count.save()

            successes += 1

    # Once the map is created, send the user to it
    return redirect("/map/see/%s" % request.POST['mapname'])

def show_map(request, mapname):
        t = get_template('map.html')
        html = t.render(RequestContext(request, {"name": mapname}))
        return HttpResponse(html)

def produce_map_js(request, mapname):
    my_map = models.Map.objects.get(name=mapname)

    # Highest and lowest (non-zero) number of postcodes in any constituency -
    # used to create the correct colour transitions
    highest_count = models.ConstituencyCount.objects.filter(map=my_map).order_by('-count')[0].count
    lowest_count = models.ConstituencyCount.objects.filter(map=my_map).order_by('count')[0].count
    
    # Create a mapping between the number of postcodes in that constituency,
    # and the colours we want to display on the map.
    LIGHT_RED = "#ffcccc"
    DARK_RED = "#ff0000"
    colours = ColourCoordinator(lowest_count, highest_count, 30, LIGHT_RED, DARK_RED)
    
    response = "var constituencies_info = {"
    first = 1
    for constituency in models.Constituency.objects.all():
        # Javascript doesn't like a comma at the end of a dictionary
        if not first:
            response += ",\n"
        else:
            first = 0

        try:
            count = my_map.constituencycount_set.get(constituency=constituency).count
        except:
            count = 0

        response += """
        '{0}': {{'text': '{0} ({1})',
                 'count': {1},
                 'colour': '{2}' }}""".format(constituency.name, count, colours.get_colour_mapping(count))

    response += "}"
    return HttpResponse(response, "text/javascript; encoding=utf-8")
