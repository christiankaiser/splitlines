# splitlines.py

This simple Python script takes two input vector layers:

1. a **line vector file** in GeoJSON format
2. a **point vector file** in GeoJSON format

It splits the lines in the vector files at all point locations within a snapping distance to be specified.

The script can be used as follows:

    python splitlines.py --lines data/lines.geojson --points data/points.geojson --output splitted.geojson --snapdist 0.05

if you want to use the example provided with the script.

Note that the distance calculation is done using simple Euclidean distance and not any geodesic distance. Therefore, the use of a projected spatial reference system is recommended if you want to get a controlled result (but from a calculation point it is not required).

The script is released under [a Creative Commons licence](http://creativecommons.org/licenses/by-sa/3.0/us/). Some parts of the script have been taken from [http://sgillies.net/blog/1040/shapely-recipes/](http://sgillies.net/blog/1040/shapely-recipes/).

