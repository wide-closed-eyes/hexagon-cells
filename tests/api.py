import h3


def test_hex_not_empty_and_contains_expected(client):
    resp = client.get("/hex", params={"hex": "8a11aa648367fff"})
    assert resp.status_code == 200

    data = resp.json()
    assert data, "Ответ /hex не должен быть пустым"

    # Пример из ТЗ: обе ячейки должны присутствовать в ответе
    expected = [
        ["8c11aa6483601ff", -120, 93],
        ["8c11aa6483603ff", -119, 94],
    ]
    for row in expected:
        assert row in data, f"Ожидалась строка {row} в ответе /hex"

    # Все возвращённые ячейки действительно входят в заданный гексагон
    target_res = h3.get_resolution("8a11aa648367fff")
    for cell, _, _ in data:
        assert h3.cell_to_parent(cell, target_res) == "8a11aa648367fff"


def test_avg_res0_not_empty_and_contains_expected(client):
    resp = client.get("/avg", params={"resolution": 0})
    assert resp.status_code == 200

    data = resp.json()
    assert data, "Ответ /avg не должен быть пустым"

    # Пример из ТЗ: cell_id=1 и cell_id=2 должны быть в ответе
    by_cell_id = {row[2]: row for row in data}
    assert 1 in by_cell_id, "Ожидался cell_id=1 в ответе /avg"
    assert 2 in by_cell_id, "Ожидался cell_id=2 в ответе /avg"

    assert by_cell_id[1][0] == "8011fffffffffff"
    assert by_cell_id[1][1] == -84
    assert by_cell_id[2][0] == "8011fffffffffff"
    assert by_cell_id[2][1] == -83


def test_bbox_not_empty(client):
    border = "55.95/37.9,55.95/38.1,56.05/38.1,56.05/37.9"
    resp = client.get("/bbox", params={"border": border})
    assert resp.status_code == 200

    data = resp.json()
    assert data, "Ответ /bbox не должен быть пустым"
    for row in data:
        assert len(row) == 3


def test_bbox_kml_not_empty_file(client):
    border = "55.95/37.9,55.95/38.1,56.05/38.1,56.05/37.9"
    resp = client.get("/bbox_kml", params={"border": border})
    assert resp.status_code == 200

    # Файл отдаётся как скачивание
    assert resp.headers["content-type"].startswith(
        "application/vnd.google-earth.kml+xml"
    )
    assert "attachment" in resp.headers["content-disposition"]

    # Содержимое не пустое и является KML файлом
    assert resp.text.strip()
    assert "<kml" in resp.text
