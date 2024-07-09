#!/usr/bin/env sh

if [ "$1" = "init" ]; then
    docker run -v "$(pwd)/graphhopper_data":/graphhopper_data -p 8989:8989 docker.io/israelhikingmap/graphhopper -i /graphhopper_data/romania-latest.osm.pbf -o /graphhopper_data/cache --import
    exit 0
fi

if [ $(ls -A ./graphhopper_data/cache | wc -l) -ne 0 ]; then
    ./graphhopper.sh init
fi

docker run -v "$(pwd)/graphhopper_data":/graphhopper_data -p 8989:8989 docker.io/israelhikingmap/graphhopper -o /graphhopper_data/cache --host 0.0.0.0
