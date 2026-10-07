"""Thin test plate to try hole fits: 6.1 and 6.3 toggle holes, 16 mm button hole.

Minimal filament: each hole gets a WALL-thick ring, holes share a WALL-thick
web, and the outline is just the union of the rings.
The flat cut on the 6.1 ring tells it apart from the 6.3.
"""

import math

from cadgen import build123d as bd
from cadgen import step, stl, threemf

THICK = 3.0
WALL = 2.5            # ring and web width, ~6 perimeters at 0.4 mm nozzle
SMALL_TOP = 6.1       # toggle bushing trial, flat-marked
SMALL_BOTTOM = 6.3    # toggle bushing trial
BIG = 16.0            # button, straight bore
MARK = 1.0            # depth of the flat on the 6.1 ring


def plate():
    rt, rb, rB = SMALL_TOP / 2, SMALL_BOTTOM / 2, BIG / 2
    yt, yb = rt + WALL / 2, -(rb + WALL / 2)
    # big hole sits WALL away from the larger small hole, level with the gap between them
    d = rB + WALL + max(rt, rb)
    bx = math.sqrt(d**2 - max(yt, -yb) ** 2)
    holes = [(0, yt, rt), (0, yb, rb), (bx, 0, rB)]
    outline = bd.Sketch() + [bd.Pos(x, y) * bd.Circle(r + WALL) for x, y, r in holes]
    # flat on the far side of the 6.1 ring
    outline -= bd.Pos(-(rt + WALL), 0) * bd.Rectangle(2 * MARK, 2 * (yt + rt + WALL), align=(bd.Align.CENTER, bd.Align.MIN))
    body = bd.extrude(outline, amount=THICK)
    for x, y, r in holes:
        body -= bd.Pos(x, y, THICK / 2) * bd.Cylinder(r, THICK * 2)
    return body


@step(out="../STEP/hole_test_plate.step")
@stl(out="../STL/hole_test_plate.stl")
@threemf(out="../3MF/hole_test_plate.3mf")
def hole_test_plate():
    body = plate()
    body.label = "hole_test_plate"
    return body


if __name__ == "__main__":
    hole_test_plate()
