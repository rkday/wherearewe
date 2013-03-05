from utils import get_constituency_list

constituencies = get_constituency_list()

print "var constituency_polygons = {"
for i, name in enumerate(sorted(constituencies.keys())):
    simple_constit = constituencies[name].simplify(0.01)
    if i > 0:
        print ","
    print """
    "{0}": {{
        'exterior_coordinates': {1},
        'interior_coordinates': {2} }}
    """.format(
            name,
            [[x, y] for x,y in list(simple_constit.exterior.coords)],
            [[[x,y] for x,y in list(i.coords)] for i in list(simple_constit.interiors)])
print "}"
