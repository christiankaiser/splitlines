#!/usr/bin/env python
"""
Splits a line vector layer at the point locations coming from another vector layer.

Code under Creative Commons licence (Attribution-ShareAlike 3.0 United States CC BY-SA 3.0 US).
Some parts are taken from http://sgillies.net/blog/1040/shapely-recipes/.
"""

__version__ = '1.0.0'
__date__ = '2015-09-21'
__author__ = 'Christian Kaiser <chri.kais@gmail.com>'


from optparse import OptionParser
import sys
import json
import codecs
import shapely
import shapely.geometry
from shapely.geometry import LineString, Point


USAGE = """splitlines
    --lines INPUT_LINE_LAYER --points INPUT_POINT_LAYER 
    --output OUTPUT_LAYER --snapdist SNAPPING_DISTANCE
    
    Input layers need to be GeoJSON files. Output is also a GeoJSON file.
    Files are expected to be in UTF-8 encoding.
    """


def splitlines(linefc, pointfc, outfile, snapdist):
    print "    %i lines and %i points" % (len(linefc['features']), len(pointfc['features']))
    print "    snapping distance is %f" % snapdist
    print "    output file is %s" % outfile
    lines = []
    for feat in linefc['features']:
        lines.append(shapely.geometry.shape(feat['geometry']))
    pts = []
    for feat in pointfc['features']:
        pts.append(shapely.geometry.shape(feat['geometry']))
    outlines = []
    for i in range(len(lines)):
        splitted_lines = [lines[i]]
        print "    splitting line %i of %i..." % (i+1, len(lines))
        for p in pts:
            # check if point is on one of the lines
            splitted_lines = point_splitlines(p, splitted_lines, snapdist)
        outlines += splitted_lines
    outjson = {
        "type": "FeatureCollection",
        "features": []
    }
    for i in range(len(outlines)):
        l = outlines[i]
        f = {
            "type": "Feature", 
            "properties": { "id": i+1 }, 
            "geometry": shapely.geometry.geo.mapping(l)
        }
        outjson['features'].append(f)
    fout = codecs.open(outfile, 'w', 'utf-8')
    fout.write(json.dumps(outjson))
    fout.close()


def point_splitlines(p, ls, snapdist):
    """
    Takes one point and an array of lines. Splits a line if it the point is on it, or close
    to it.
    """
    outlines = []
    for l in ls:
        if p.distance(l) <= snapdist:
            outlines += cut_line_at_point(l, p)
        else:
            outlines.append(l)
    return outlines


def cut_line_at_point(l, p):
    return cut_line_at_distance(l, l.project(p))


def cut_line_at_distance(line, distance):
    """
    Cuts a line in two at a distance from its starting point
    Function from http://sgillies.net/blog/1040/shapely-recipes/
    """
    if distance <= 0.0 or distance >= line.length:
        return [LineString(line)]
    coords = list(line.coords)
    for i, p in enumerate(coords):
        pd = line.project(Point(p))
        if pd == distance:
            return [
                LineString(coords[:i+1]),
                LineString(coords[i:])]
        if pd > distance:
            cp = line.interpolate(distance)
            return [
                LineString(coords[:i] + [(cp.x, cp.y)]),
                LineString([(cp.x, cp.y)] + coords[i:])]


if __name__ == "__main__":
    parser = OptionParser(usage=USAGE)
    parser.add_option(
        '-l', '--lines', dest="lines",
        help="GeoJSON input line file",
        metavar="INPUT_LINE_LAYER"
    )
    parser.add_option(
        '-p', '--points', dest="points",
        help="GeoJSON input point file",
        metavar="INPUT_POINT_LAYER"
    )
    parser.add_option(
        '-o', '--output', dest="output",
        help="Path to output GeoJSON file",
        metavar="OUTPUT_LAYER"
    )
    parser.add_option(
        '-s', '--snapdist', dest="snapdist",
        help="Distance for snapping points to the lines",
        metavar="SNAPPING_DISTANCE"
    )
    (options, args) = parser.parse_args()
    try:
        lines = options.lines
        points = options.points
        outfile = options.output
        snapdist = float(options.snapdist)
    except:
        print "Error reading your input parameters."
        sys.exit(0)
    if lines == None or points == None or outfile == None:
        print USAGE
        sys.exit(0)
    print("splitlines starting...")
    flines = codecs.open(lines, 'r', 'utf-8')
    linefc = json.load(flines)
    flines.close()
    fpoints = codecs.open(points, 'r', 'utf-8')
    pointfc = json.load(fpoints)
    fpoints.close()
    splitlines(linefc, pointfc, outfile, snapdist)
    print("splitlines done.")
