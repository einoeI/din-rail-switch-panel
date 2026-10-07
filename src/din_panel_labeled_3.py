"""DIN rail panel v3: button / button / big toggle / big toggle / button.

Big toggles (KN3C style) have a 29.5 x 15.6 mm body behind the plate, long side
across the rail (lever moves up/down). The old 32 mm interior left no room for
the screw terminals, so the box is widened and, like Raspberry Pi DIN mounts,
the box no longer has to match the rail: the rail clip sits on two rear lips
that keep the old (tested) 35.5 mm slide-on groove and 32 mm rail opening.

X across the rail (up on the panel), Y along the rail,
Z front plate (0) to rail (back). Labels are raised 0.6 mm on the front face,
a separate body for a second colour.
"""

from cadgen import build123d as bd
from cadgen import srgb, step, stl, threemf

# Rail profile, from the tested din_panel
DEPTH = 54.3          # front face to back of rail lips
FRONT = 2.0           # front plate thickness
RAIL_GROOVE = 35.5    # 35 mm rail + clearance
GROOVE_Z = 50.8       # groove starts here
GROOVE_H = 1.5        # 1 mm rail flange + clearance
BUTTON_HOLE = 16.3    # 16 mm button, calibration knob

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
TEXT_HEIGHT = 0.6     # raised above the front face (3 layers at 0.2)

WIDTH = 50.0          # was 40; 29.5 body leaves ~6 mm per side for terminals
WALL = 4.0
RAIL_OPENING = 32.0   # old interior width, so the rail engages the same 1.5 mm per side
LIP_Z = GROOVE_Z - 2.0  # rear lip front face; 45 deg chamfer below it, printable face down
PITCH = 35.0          # widest label (30.9 mm) + gap
HOLE_X = 23.0         # hole centres, a bit low so the two-line tops fit

TOGGLE_HOLE = 12.3    # 12 mm bushing, +0.3 like the tested 16.3 button hole; NOT TESTED
KEY_W = 2.0           # anti-rotation tab into the hole (bushing keyway), at OFF (down, -X)
KEY_D = 1.0

TITLE, SMALL = 3.5, 3.0
TOP = 17.5            # every title on one line
# (hole, [(text, x offset from hole centre, font size)]) left to right
COMPONENTS = [
    ("button", [("MAIN POWER", TOP, TITLE), ("LIGHT = ON", -12.5, SMALL)]),
    ("button", [("PUSH TO START", TOP, TITLE), ("3S FOR RESET", 13.0, SMALL), ("SERVER STATUS", -12.5, TITLE)]),
    ("toggle", [("SIMULATION", TOP, TITLE)]),
    ("toggle", [("ARM", TOP, TITLE)]),
    ("button", [("REACTOR TRIP", TOP, TITLE)]),
]
LENGTH = PITCH * len(COMPONENTS)


def box(x0, x1, y0, y1, z0, z1):
    return bd.Pos(x0, y0, z0) * bd.Box(x1 - x0, y1 - y0, z1 - z0, align=bd.Align.MIN)


def body():
    c, o, ch = WIDTH / 2, RAIL_OPENING / 2, RAIL_OPENING / 2 - (WIDTH / 2 - WALL)
    cavity = bd.Polyline(
        (WALL, FRONT), (WIDTH - WALL, FRONT), (WIDTH - WALL, LIP_Z + ch), (c + o, LIP_Z),
        (c + o, DEPTH), (c - o, DEPTH), (c - o, LIP_Z), (WALL, LIP_Z + ch), close=True,
    )
    profile = bd.Rectangle(WIDTH, DEPTH, align=bd.Align.MIN) - bd.make_face(cavity)
    # profile is in XY; lay it into XZ and extrude along +Y
    solid = bd.extrude(bd.Plane.XZ * profile, amount=-LENGTH)
    g0 = c - RAIL_GROOVE / 2
    solid -= box(g0, WIDTH - g0, 0, LENGTH, GROOVE_Z, GROOVE_Z + GROOVE_H)
    for i, (kind, _) in enumerate(COMPONENTS):
        at = bd.Pos(HOLE_X, PITCH * (i + 0.5), FRONT / 2)
        if kind == "button":
            solid -= at * bd.Cylinder(BUTTON_HOLE / 2, FRONT * 2)
        else:
            r = TOGGLE_HOLE / 2
            solid -= at * (bd.Cylinder(r, FRONT * 2) - bd.Pos(-r + (KEY_D - 1) / 2, 0, 0) * bd.Box(KEY_D + 1, KEY_W, FRONT * 2))
    return solid


def labels():
    shapes = []
    for i, (kind, lines) in enumerate(COMPONENTS):
        for text, dx, size in lines:
            plane = bd.Plane(origin=(HOLE_X + dx, PITCH * (i + 0.5), 0), x_dir=(0, 1, 0), z_dir=(0, 0, -1))
            glyphs = bd.Text(text, size, font_path=FONT, align=(bd.Align.CENTER, bd.Align.CENTER))
            shapes.append(bd.extrude(plane * glyphs, amount=TEXT_HEIGHT))
    return bd.Compound(shapes)


@step(out="../STEP/din_panel_labeled_3.step")
@stl(out="../STL/din_panel_labeled_3.stl")
@threemf(out="../3MF/din_panel_labeled_3.3mf")
def din_panel_labeled_3():
    panel = body()
    panel.label = "din_panel"
    panel.color = srgb("#2E3742")
    text = labels()
    text.label = "labels"
    text.color = srgb("#F2F2F2")
    return bd.Compound(children=[panel, text], label="din_panel_labeled_3")


if __name__ == "__main__":
    din_panel_labeled_3()
