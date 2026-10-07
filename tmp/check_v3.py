import sys
sys.path.insert(0, "src")
from cadgen import build123d as bd, read_step
import din_panel_labeled_3 as m

s = read_step("STEP/din_panel_labeled_3.step")
panel, text = s.children
bb = panel.bounding_box()
print("panel", [round(v, 2) for v in (bb.size.X, bb.size.Y, bb.size.Z)], "vol", round(panel.volume))
assert abs(bb.size.X - m.WIDTH) < 1e-3 and abs(bb.size.Y - m.LENGTH) < 1e-3
assert len(panel.solids()) == 1
# rail opening and groove at the back, interior room for 29.5 toggle body
def solid_at(x, z):  # probe at mid-pitch between components 3 and 4
    return panel.is_inside(bd.Vector(x, m.PITCH * 3, z))
c = m.WIDTH / 2
assert not solid_at(c - 15.9, m.DEPTH - 0.1) and solid_at(c - 16.1, m.DEPTH - 0.1)  # 32 opening
assert not solid_at(c - 17.7, m.GROOVE_Z + 0.75) and solid_at(c - 17.8, m.GROOVE_Z + 0.75)  # 35.5 groove
inner = m.WIDTH - 2 * m.WALL
print("interior", inner, "per side for 29.5 body", (inner - 29.5) / 2)
# toggle hole + notch at OFF (-X)
y = m.PITCH * 2.5
r = m.TOGGLE_HOLE / 2
assert panel.is_inside(bd.Vector(m.HOLE_X - r + 0.9, y, 1))  # tab reaches 1 mm in
assert not panel.is_inside(bd.Vector(m.HOLE_X - r + 1.1, y, 1))
assert not panel.is_inside(bd.Vector(m.HOLE_X + r - 0.5, y, 1))  # no tab at ON
assert not panel.is_inside(bd.Vector(m.HOLE_X - r + 0.5, y + 1.1, 1))  # tab 2 wide
# labels: on the face, inside the plate, no overlap with neighbours or hole clearance (r 9.5)
spans = {}
for i, (kind, lines) in enumerate(m.COMPONENTS):
    hx = m.HOLE_X
    for t, dx, sz in lines:
        g = bd.Text(t, sz, font_path=m.FONT).bounding_box()
        x0, x1 = hx + dx - g.size.Y / 2, hx + dx + g.size.Y / 2
        assert 1 < x0 and x1 < m.WIDTH - 1, t
        assert min(abs(x0 - hx), abs(x1 - hx)) > 9.5, t
        spans.setdefault(i, []).append((m.PITCH * (i + .5) - g.size.X / 2, m.PITCH * (i + .5) + g.size.X / 2))
w = [(min(a for a, _ in v), max(b for _, b in v)) for v in spans.values()]
gaps = [b[0] - a[1] for a, b in zip(w, w[1:])]
print("label gaps", [round(g, 1) for g in gaps])
assert min(gaps) >= 3 and w[0][0] > 0.5 and w[-1][1] < m.LENGTH - 0.5
tb = text.bounding_box()
assert abs(tb.min.Z + m.TEXT_HEIGHT) < 1e-3 and abs(tb.max.Z) < 1e-3
print("toggle body room to walls", m.HOLE_X - 29.5 / 2 - m.WALL, m.WIDTH - m.WALL - m.HOLE_X - 29.5 / 2)
print("OK")
