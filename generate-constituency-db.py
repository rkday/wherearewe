#!/usr/bin/python
import sys
sys.path.append("./django/")
import mysite.settings
from django.core.management import setup_environ
setup_environ(mysite.settings)
import waw_app.models
import csv

with open("raw_data/constituency_population.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        waw_app.models.Constituency.objects.create(name=row['Constituency'], population=int(row['Population'].replace(",",""))).save()
