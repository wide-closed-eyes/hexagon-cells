import h3
import simplekml


class KML:
    @classmethod
    async def get_kml(self, cells):
        kml = simplekml.Kml(name="H3 bbox")

        for cell, level, cell_id in cells:
            boundary = h3.cell_to_boundary(cell)
            coords = [(lng, lat) for lat, lng in boundary]
            coords.append(coords[0])

            pol = kml.newpolygon(name=cell)
            pol.description = f"level={level}, cell_id={cell_id}"
            pol.outerboundaryis = coords

        return kml.kml()
