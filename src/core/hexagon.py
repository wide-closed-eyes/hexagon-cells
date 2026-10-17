import math
from collections import defaultdict

import h3
from shapely.geometry import Polygon

from src.config import config
from src.core.kml import KML


class H3CellsStorage:
    def __init__(self):
        self._state = self.generate_h3_cells()

    @staticmethod
    def generate_h3_cells() -> list[list]:
        # Получаем центральную ячейку
        center_cell = h3.latlng_to_cell(
            config.LAT_CENTER, config.LNG_CENTER, config.RESOLUTION
        )

        # Переводим центральную ячейку в координаты (lat, lng)
        center_coords = h3.cell_to_latlng(center_cell)

        k_rings = 16
        candidate_cells = h3.grid_disk(center_cell, k_rings)

        result = []
        for cell in candidate_cells:
            # Переводим текущую ячейку из хэша в координаты (lat, lng)
            cell_coords = h3.cell_to_latlng(cell)

            # Передаем в функцию координаты вместо строк
            distance = h3.great_circle_distance(center_coords, cell_coords, unit="km")

            if distance < config.RADIUS_KM:
                h3_int = int(cell, 16)
                level = ((h3_int // 512) % 74) - 120
                cell_id = ((h3_int // 512) % 100) + 1
                result.append([cell, level, cell_id])

        return result

    async def get_by_hex(self, hex_index: str) -> list[list]:
        """
        Возвращает элементы датасета, входящие в заданный гексагон.
        """
        if not h3.is_valid_cell(hex_index):
            raise ValueError(f"Invalid hex index: {hex_index}")

        target_res = h3.get_resolution(hex_index)

        if not self._state:
            return []

        data_res = h3.get_resolution(self._state[0][0])
        if target_res > data_res:
            raise ValueError(
                f"Resolution of 'hex' ({target_res}) must be <= {data_res}"
            )

        if target_res == data_res:
            for row in self._state:
                if row[0] == hex_index:
                    return [row]
            return []

        result = []
        for cell, level, cell_id in self._state:
            if h3.cell_to_parent(cell, target_res) == hex_index:
                result.append([cell, level, cell_id])

        return result

    async def get_avg(self, resolution: int) -> list[list]:
        """
        Возвращает массив [parent_h3, median_level, cell_id]:
        """
        if not (0 <= resolution <= 12):
            raise ValueError("resolution must be in [0, 12]")

        if not self._state:
            return []

        data_res = h3.get_resolution(self._state[0][0])
        if resolution > data_res:
            raise ValueError(
                f"resolution ({resolution}) cannot exceed data resolution ({data_res})"
            )

        # Группируем level по (parent, cell_id)
        groups: dict[tuple[str, int], list[int]] = defaultdict(list)
        for cell, level, cell_id in self._state:
            parent = h3.cell_to_parent(cell, resolution)
            groups[(parent, cell_id)].append(level)

        result = []
        for (parent, cell_id), levels in groups.items():
            median_level = await self._median_floor(levels)
            result.append([parent, median_level, cell_id])

        # Детерминированный порядок: cell_id, затем parent
        result.sort(key=lambda r: (r[2], r[0]))
        return result

    @staticmethod
    async def _median_floor(values: list[int]) -> int:
        """Медиана с округлением вниз"""
        s = sorted(values)
        n = len(s)
        mid = n // 2
        if n % 2 == 1:
            return s[mid]
        return math.floor((s[mid - 1] + s[mid]) / 2)

    async def get_bbox(self, border: list) -> list[list]:
        """
        Возвращает элементы датасета, гексагоны которых целиком лежат внутри
        полигона с границами заданными параметром border.
        """
        # Парсинг границы
        coords = []
        for point in border:
            lat_str, lon_str = point.strip().split("/")
            coords.append((float(lon_str), float(lat_str)))

        if len(coords) < 3:
            raise ValueError("border must contain at least 3 points")

        # Создание полигона
        border_poly = Polygon(coords)

        # Фильтр ячеек датасета
        result = []

        for cell, level, cell_id in self._state:
            boundary = h3.cell_to_boundary(cell)
            cell_poly = Polygon([(lng, lat) for lat, lng in boundary])

            # Проверка гексагон внутри полигона
            if border_poly.contains(cell_poly):
                result.append([cell, level, cell_id])

        return result

    async def get_bbox_kml(self, border: list) -> str:
        """Возвращает KML фаил с гексагонами, которые лежат внутри границы border"""
        await self.get_bbox(border)
        return await KML.get_kml(self._state)
