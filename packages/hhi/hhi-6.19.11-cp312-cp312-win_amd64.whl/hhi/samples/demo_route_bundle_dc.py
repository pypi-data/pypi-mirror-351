import gdsfactory as gf

from hhi import cells, tech


@gf.cell
def sample_route_bundle_dc():
    c = gf.Component()
    d1 = c << cells.HHI_DFB()
    p1 = c << cells.pad()
    p1.movey(150)
    _ = tech.route_bundle_dc(c, [d1.ports["e1"]], [p1.ports["e1"]], auto_taper=False)
    return c


if __name__ == "__main__":
    c = sample_route_bundle_dc()
    c.show()
