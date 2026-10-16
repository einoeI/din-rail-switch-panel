"""DIN rail panel v3: button / button / small toggle / big toggle / big toggle / button.

Big toggles (KN3C style) have a 29.5 x 15.6 mm body behind the plate, long side
across the rail (lever moves up/down). The old 32 mm interior left no room for
the screw terminals, so the box is widened and, like Raspberry Pi DIN mounts,
the box no longer has to match the rail: the rail clip sits on two rear lips
that keep the old (tested) 35.5 mm slide-on groove and 32 mm rail opening.

X across the rail (up on the panel), Y along the rail,
Z front plate (0) to rail (back). Structure only - no engraved/raised text;
labels are added later in Bambu Studio.
"""

import struct
import zipfile

from cadgen import build123d as bd
from cadgen import srgb, step

# Rail profile, from the tested din_panel
DEPTH = 54.3          # front face to back of rail lips
FRONT = 2.0           # front plate thickness
RAIL_GROOVE = 35.5    # 35 mm rail + clearance
GROOVE_Z = 50.8       # groove starts here
GROOVE_H = 1.5        # 1 mm rail flange + clearance
BUTTON_HOLE = 16.3    # 16 mm button, calibration knob

WIDTH = 60.0          # was 50; extended for the push-button label clearance
WALL = 4.0
RAIL_OPENING = 32.0   # old interior width, so the rail engages the same 1.5 mm per side
LIP_Z = GROOVE_Z - 2.0  # rear lip front face; 45 deg chamfer below it, printable face down
PITCH = 35.0          # hole spacing along the rail
HOLE_X = 29.4         # hole centres, across the rail

TOGGLE_HOLE = 12.3    # 12 mm bushing, +0.3 like the tested 16.3 button hole; NOT TESTED
KEY_W = 2.0           # anti-rotation tab into the hole (bushing keyway), at OFF (down, -X)
KEY_D = 1.0

SMALL_TOGGLE_HOLE = 6.3  # small toggle bushing, tested (dimensions.md)
SMALL_KEY_W = 1.0
SMALL_KEY_D = 0.5

# hole kind per component, left to right: main power, modbus server, HIL/
# standalone, simulation, manual trip/arming, reactor trip
COMPONENTS = ["button", "button", "toggle_small", "toggle", "toggle", "button"]
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
    for i, kind in enumerate(COMPONENTS):
        at = bd.Pos(HOLE_X, PITCH * (i + 0.5), FRONT / 2)
        if kind == "button":
            solid -= at * bd.Cylinder(BUTTON_HOLE / 2, FRONT * 2)
        else:
            d, kw, kd = (TOGGLE_HOLE, KEY_W, KEY_D) if kind == "toggle" else (SMALL_TOGGLE_HOLE, SMALL_KEY_W, SMALL_KEY_D)
            r = d / 2
            solid -= at * (bd.Cylinder(r, FRONT * 2) - bd.Pos(-r + (kd - 1) / 2, 0, 0) * bd.Box(kd + 1, kw, FRONT * 2))
    return solid


@step(out="../STEP/din_panel_labeled_3.step")
def din_panel_labeled_3():
    panel = body()
    panel.label = "din_panel"
    panel.color = srgb("#CC0000")
    return panel


# cadgen's own `@stl`/`@threemf` mesh engine occasionally caps one hole with a
# spurious flat disc of triangles (confirmed on this file, position-dependent,
# reproducible on cadgen 0.7.15 and 0.7.21) even though the STEP/BREP is
# correct - build123d's own .tessellate() on the same shape is clean, so the
# mesh files are built from that directly instead of the shared mesh engine.
def write_stl(path, shape):
    verts, tris = shape.tessellate(1e-3, 0.1)
    with open(path, "wb") as f:
        f.write(b"\0" * 80)
        f.write(struct.pack("<I", len(tris)))
        for i1, i2, i3 in tris:
            v1, v2, v3 = verts[i1], verts[i2], verts[i3]
            ax, ay, az = v2.X - v1.X, v2.Y - v1.Y, v2.Z - v1.Z
            bx, by, bz = v3.X - v1.X, v3.Y - v1.Y, v3.Z - v1.Z
            nx, ny, nz = ay * bz - az * by, az * bx - ax * bz, ax * by - ay * bx
            mag = (nx * nx + ny * ny + nz * nz) ** 0.5 or 1.0
            f.write(struct.pack("<3f", nx / mag, ny / mag, nz / mag))
            for v in (v1, v2, v3):
                f.write(struct.pack("<3f", v.X, v.Y, v.Z))
            f.write(struct.pack("<H", 0))


def write_3mf(path, shape, color):
    verts, tris = shape.tessellate(1e-3, 0.1)
    vxml = "".join(f'<vertex x="{v.X}" y="{v.Y}" z="{v.Z}"/>' for v in verts)
    txml = "".join(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in tris)
    model = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">'
        f'<resources><basematerials id="1"><base name="material-0" displaycolor="{color}"/></basematerials>'
        f'<object id="2" type="model" pid="1" pindex="0">'
        f"<mesh><vertices>{vxml}</vertices><triangles>{txml}</triangles></mesh></object></resources>"
        '<build><item objectid="2"/></build></model>'
    )
    content_types = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'
    )
    rels = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Target="/3D/3dmodel.model" Id="rel-1" '
        'Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'
    )
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types)
        z.writestr("_rels/.rels", rels)
        z.writestr("3D/3dmodel.model", model)


if __name__ == "__main__":
    din_panel_labeled_3()
    panel = body()
    write_stl("../STL/din_panel_labeled_3.stl", panel)
    write_3mf("../3MF/din_panel_labeled_3.3mf", panel, "#CC0000FF")
