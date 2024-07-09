#!/usr/bin/env sh

if [ "$1" = "init" ] || [ "$1" = "reset" ]; then
    if [ "$1" = "reset" ]; then
        rm -r ./graphhopper_data/*
        rm ./ro_localitati_punct.geojson
    fi

    [ -f ./graphhopper_data/romania-latest.osm.pbf ] || curl "https://download.geofabrik.de/europe/romania-latest.osm.pbf" -o ./graphhopper_data/romania-latest.osm.pbf
    [ -f ./ro_localitati_punct.geojson ] || curl "https://geo-spatial.org/vechi/file_download/29543" -o ./ro_localitati_punct.geojson

    docker run -v "$(pwd)/graphhopper_data":/graphhopper_data -p 8989:8989 docker.io/israelhikingmap/graphhopper -i /graphhopper_data/romania-latest.osm.pbf -o /graphhopper_data/cache --import
    exit 0
fi

if [ $(ls -A ./graphhopper_data/cache | wc -l) -ne 0 ]; then
    ./graphhopper.sh init
fi

docker run -v "$(pwd)/graphhopper_data":/graphhopper_data -p 8989:8989 docker.io/israelhikingmap/graphhopper -o /graphhopper_data/cache --host 0.0.0.0
