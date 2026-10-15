"""Second hole test plate: keyed toggle holes, left to right
6.3 with a tiny tab, 12.0 and 12.2 with the din_panel tab (12.2 flat-marked).

Same minimal-filament idea as hole_test_plate: WALL rings, WALL webs.
Thickness matches the din_panel front plate so the tabs test the real fit.
"""

from cadgen import build123d as bd
from cadgen import step, stl, threemf

THICK = 2.0           # din_panel FRONT
WALL = 2.5
MARK = 1.0            # depth of the flat on the 12.2 ring
# (diameter, tab width, tab depth); tab points -X like din_panel (OFF side)
HOLES = [
    (6.3, 1.0, 0.5),   # tested size + very small tab
    (12.0, 2.0, 1.0),  # nominal, din_panel KEY_W / KEY_D
    (12.2, 2.0, 1.0),  # flat-marked
]


def keyed_hole(d, key_w, key_d):
    r = d / 2
    return bd.Cylinder(r, THICK * 2) - bd.Pos(-r + (key_d - 1) / 2, 0, 0) * bd.Box(key_d + 1, key_w, THICK * 2)


def plate():
    xs, x = [], 0.0
    for i, (d, _, _) in enumerate(HOLES):
        if i:
            x += HOLES[i - 1][0] / 2 + WALL + d / 2
        xs.append(x)
    outline = bd.Sketch() + [bd.Pos(x, 0) * bd.Circle(d / 2 + WALL) for x, (d, _, _) in zip(xs, HOLES)]
    end = xs[-1] + HOLES[-1][0] / 2 + WALL
    outline -= bd.Pos(end, 0) * bd.Rectangle(2 * MARK, 2 * end)
    body = bd.extrude(outline, amount=THICK)
    for x, hole in zip(xs, HOLES):
        body -= bd.Pos(x, 0, THICK / 2) * keyed_hole(*hole)
    return body


@step(out="../STEP/hole_test_plate_2.step")
@stl(out="../STL/hole_test_plate_2.stl")
@threemf(out="../3MF/hole_test_plate_2.3mf")
def hole_test_plate_2():
    body = plate()
    body.label = "hole_test_plate_2"
    return body


if __name__ == "__main__":
    hole_test_plate_2()
