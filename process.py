#!/usr/bin/env python3

import json
import csv
import os
import subprocess
import signal
import time
import requests
import numpy as np

def city_name(city):
    return "%s, %s, %d" % (city["properties"]["name"], city["properties"]["countyMn"], city["properties"]["natCode"])

graphhopper_proc = None
try:
    graphhopper_proc = subprocess.Popen(["./graphhopper.sh"], stdin=None, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=False, preexec_fn=os.setsid)

    while True:
        try:
            requests.get("http://localhost:8989/health")
            break
        except Exception as e:
            print(e)
            time.sleep(1)

    with open(os.getenv("DISTANTE_INPUT") or "ro_localitati_punct.geojson", "r") as file:
        data = json.load(file)

    cities = data["features"]
    cities_max = os.getenv("DISTANTE_MAX")
    if cities_max and cities_max.isdecimal():
        cities = cities[0:int(cities_max)]

    distances = np.zeros((len(cities), len(cities)))

    for i in range(1, len(cities)):
        print("%d/%d" % (i, len(cities)))
        for j in range(i):
            r = requests.post("http://localhost:8989/route", json={
                "points": [cities[i]["geometry"]["coordinates"] for i in [i, j]],
                "profile": "car",
                "instructions": False,
                "calc_points": False,
            })
            result = r.json()

            if "paths" not in result or len(result["paths"]) == 0:
                print("Drum izolat: %s - %s" % (city_name(cities[i]), city_name(cities[j])))
                continue
            distance = sorted(result["paths"], key=lambda x: x["distance"])[0]["distance"] / 1000
            distances[i][j] = distance
            distances[j][i] = distance

    print("%d/%d - Calcul finalizat" % (len(cities), len(cities)))

    with open(os.getenv("DISTANTE_OUTPUT") or "distante.csv", "w") as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow([""] + [city_name(city) for city in cities])
        for i in range(len(cities)):
            csv_writer.writerow([city_name(cities[i])] + ["%.1f" % d for d in distances[i]])
finally:
    if graphhopper_proc:
        os.killpg(os.getpgid(graphhopper_proc.pid), signal.SIGTERM)
