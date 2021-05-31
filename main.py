from enum import IntFlag
from typing import NamedTuple
from matplotlib import patches, pyplot as plt
import sys

class Position (IntFlag):
    INSIDE = 0
    LEFT = 1
    RIGHT = 2
    BOTTOM = 4
    TOP = 8

Point = NamedTuple('Point', [('x', float), ('y', float)])
PointPair = NamedTuple('PointPair', [('a', Point), ('b', Point)])

def lineClipCohen(region: PointPair, line: PointPair):
    xmin, ymin = region.a
    xmax, ymax = region.b

    def getPos(p: Point):
        x, y = p
        pos = Position.INSIDE
        if x < xmin:
            pos |= Position.LEFT
        elif x > xmax:
            pos |= Position.RIGHT

        if y < ymin:
            pos |= Position.BOTTOM
        elif y > ymax:
            pos |= Position.TOP

        return pos

    def isInside(pos1: Position, pos2: Position):
        return not (pos1 | pos2)

    def isOutside(pos1: Position, pos2: Position):
        return bool(pos1 & pos2)

    a, b = line
    posA = getPos(a)
    posB = getPos(b)

    def clip(posOut: Position, a: Point, b: Point):
        if posOut & Position.TOP:
            return Point(a.x + (b.x - a.x) * (ymax - a.y) / (b.y - a.y), ymax)
        if posOut & Position.BOTTOM:
            return Point(a.x + (b.x - a.x) * (ymin - a.y) / (b.y - a.y), ymin)
        if posOut & Position.RIGHT:
            return Point(a.y + (b.y - a.y) * (xmax - a.x) / (b.x - a.x), xmax)
        if posOut & Position.LEFT:
            return Point(a.y + (b.y - a.y) * (xmin - a.x) / (b.x - a.x), xmin)

    while not isInside(posA, posB) and not isOutside(posA, posB):
        if posB > posA:
            b = clip(posB, a, b)
            posB = getPos(b)
        else:
            a = clip(posA, a, b)
            posA = getPos(a)

    if isInside(posA, posB):
        return a, b
    else:
        return False

def clipPolySuthHodg(subjectPolygon: list[Point], clipPolygon: list[Point]):
   def inside(p):
      return(cp2[0]-cp1[0])*(p[1]-cp1[1]) > (cp2[1]-cp1[1])*(p[0]-cp1[0])

   def computeIntersection():
      dc = [ cp1[0] - cp2[0], cp1[1] - cp2[1] ]
      dp = [ s[0] - e[0], s[1] - e[1] ]
      n1 = cp1[0] * cp2[1] - cp1[1] * cp2[0]
      n2 = s[0] * e[1] - s[1] * e[0]
      n3 = 1.0 / (dc[0] * dp[1] - dc[1] * dp[0])
      return ((n1*dp[0] - n2*dc[0]) * n3, (n1*dp[1] - n2*dc[1]) * n3)

   outputList = subjectPolygon
   cp1 = clipPolygon[-1]

   for clipVertex in clipPolygon:
      cp2 = clipVertex
      inputList = outputList
      outputList = []
      s = inputList[-1]

      for e in inputList:
         if inside(e):
            if not inside(s):
               outputList.append(computeIntersection())
            outputList.append(e)
         elif inside(s):
            outputList.append(computeIntersection())
         s = e
      cp1 = cp2
   return(outputList)

def show_rect_clip(rect: PointPair, lines: list[PointPair]):
    fig, ax = plt.subplots()
    width = rect.b.x - rect.a.x
    height = rect.b.y - rect.a.y
    ax.add_patch(patches.Rectangle(rect.a, width, height, linewidth=1, edgecolor='black', facecolor='none'))

    for line in lines:
        ax.plot([line.a.x, line.b.x], [line.a.y, line.b.y], color='blue')
        clipped_line = lineClipCohen(rect, line)
        if clipped_line:
            a, b = clipped_line
            ax.plot([a.x, b.x], [a.y, b.y], color='red')
    plt.show()

def show_poly_clip(subjectPoly: list[Point], clipPoly: list[Point]):
    def plot_poly(poly: list[Point], color: str, linewidth):
        poly.append(poly[0])
        ax.plot(*zip(*poly), color, linewidth)

    fig, ax = plt.subplots()
    outPoly = clipPolySuthHodg(subjectPoly, clipPoly)
    plot_poly(subjectPoly, 'blue', 1)
    plot_poly(clipPoly, 'black', 1)
    plot_poly(outPoly, 'red', 3)
    plt.show()
    # print(outPoly, clipPoly)

def main():
    method = sys.argv[1]
    filename = sys.argv[2]

    def read_point(f):
        x = int(f.readline())
        y = int(f.readline())
        return Point(x, y)

    def read_point_pair(f):
        p1 = read_point(f)
        p2 = read_point(f)
        return PointPair(p1, p2)

    def read_poly(f, n):
        poly = []
        for i in range(n):
            poly.append(read_point(f))
        return poly

    if method == 'line':
        f = open(filename)
        n = int(f.readline())
        lines = []
        for i in range(n):
            lines.append(read_point_pair(f))
        rect = read_point_pair(f)
        show_rect_clip(rect, lines)
        f.close()
    elif method == 'poly':
        f = open(filename)
        n = int(f.readline())
        subPoly = read_poly(f, n)
        m = int(f.readline())
        clipPoly = read_poly(f, m)
        show_poly_clip(subPoly, clipPoly)
        f.close()

if __name__ == "__main__":
    main()

# clipRect =  [(100, 100), (300, 100), (300, 300), (100, 300)]

# testPoly =  [(50, 150), (200, 50), (350, 150), (350, 300), (250, 300), (200, 250), (150, 350), (100, 250), (100, 200)]

# show_poly_clip(testPoly, clipRect)
