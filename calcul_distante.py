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

def city_county_filter(county):
    if county is None:
        return lambda x: True
    return (lambda city: city["properties"]["countyMn"] == county)

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

def compute_distances(city_filter, big_city_filter, compute="time", output_path="timpi.csv"):
    with GraphHopper() as graph:
        with open("ro_localitati_punct.geojson", "r") as file:
            data = json.load(file)

        cities = data["features"]
        cities = [city for city in cities if city_filter(city)]

        distances = np.zeros((len(cities), len(cities)))

        for i in range(1, len(cities)):
            print("%d/%d" % (i, len(cities)))
            for j in range(i):
                if not big_city_filter(cities[i]) and not big_city_filter(cities[j]):
                    continue
                dist = graph.compute_distance(cities[i]["geometry"]["coordinates"], cities[j]["geometry"]["coordinates"], compute)

                if dist == -1:
                    print("Drum izolat %s - %s" % (city_name(cities[i]), city_name(cities[j])))

                distances[i][j] = dist
                distances[j][i] = dist

        print("%d/%d - Calcul finalizat" % (len(cities), len(cities)))

        with open(output_path, "w") as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow([""] + [city_name(city) for city in cities])
            for i in range(len(cities)):
                csv_writer.writerow([city_name(cities[i])] + ["%.1f" % d for d in distances[i]])

if __name__ == "__main__":
    city_filter = city_county_filter(os.getenv("DISTANTE_JUDET"))
    big_city_filter = is_big_city if os.getenv("DISTANTE_ORASE") else (lambda x: True)
    compute_distances(city_filter, big_city_filter, os.getenv("DISTANTE_TIP") or "time", os.getenv("DISTANTE_OUTPUT") or "timpi.csv")
