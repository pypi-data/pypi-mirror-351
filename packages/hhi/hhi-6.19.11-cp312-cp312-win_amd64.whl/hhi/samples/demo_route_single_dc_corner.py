import gdsfactory as gf

from hhi import cells, tech


@gf.cell
def sample_route_single_dc_corner():
    """FIXME: route_single_dc_corner not implemented"""
    c = gf.Component()
    d1 = c << cells.HHI_DFB()
    p1 = c << cells.pad()
    p1.movey(150)
    _ = tech.route_single_dc(
        c, d1.ports["e1"], d1.ports["e1"], auto_taper=False, bend="wire_corner45"
    )
    return c


if __name__ == "__main__":
    c = sample_route_single_dc_corner()
    c.show()
