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

def is_big_city(city):
    rank = city["properties"]["rank"]
    return rank in ["0", "I", "II", "III"]

class GraphHopper:
    def __init__(self):
        self.graphhopper_proc = subprocess.Popen(["./graphhopper.sh"], stdin=None, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=False, preexec_fn=os.setsid)

    def __enter__(self):
        while True:
            try:
                requests.get("http://localhost:8989/health")
                return self
            except Exception as e:
                print(e)
                time.sleep(1)

    def __exit__(self, exc_type, exc_value, traceback):
        os.killpg(os.getpgid(self.graphhopper_proc.pid), signal.SIGTERM)

    def compute_distance(self, coord1, coord2, compute="distance"):
        r = requests.post("http://localhost:8989/route", json={
            "points": [coord1, coord2],
            "profile": "car",
            "instructions": False,
            "calc_points": False,
        })
        result = r.json()

        if "paths" not in result or len(result["paths"]) == 0:
            return -1

        if compute == "time":
            time = sorted(result["paths"], key=lambda x: x["time"])[0]["time"] / (1000 * 60)
            return time
        else:
            distance = sorted(result["paths"], key=lambda x: x["distance"])[0]["distance"] / 1000
            return distance

with GraphHopper() as graph:
    with open(os.getenv("DISTANTE_INPUT") or "ro_localitati_punct.geojson", "r") as file:
        data = json.load(file)

    cities = data["features"]
    # TODO: filtrare orașe
    cities = cities[0:10]

    distances = np.zeros((len(cities), len(cities)))

    for i in range(1, len(cities)):
        # TODO: alege numai anumite orașe
        print("%d/%d" % (i, len(cities)))
        for j in range(i):
            dist = graph.compute_distance(cities[i]["geometry"]["coordinates"], cities[j]["geometry"]["coordinates"])

            if dist == -1:
                print("Drum izolat %s - %s" % (city_name(cities[i]), city_name(cities[j])))

            distances[i][j] = dist
            distances[j][i] = dist

    print("%d/%d - Calcul finalizat" % (len(cities), len(cities)))

    with open(os.getenv("DISTANTE_OUTPUT") or "distante.csv", "w") as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow([""] + [city_name(city) for city in cities])
        for i in range(len(cities)):
            csv_writer.writerow([city_name(cities[i])] + ["%.1f" % d for d in distances[i]])
