# H3 Cells API

Сервис на FastAPI для тестирования работы с гексагонами.
Используемые библиотеки: h3, shapely, simplekml. 
В качестве тестовых данных был взят круг радиусом 7 км с центром 56° с.ш., 38° в.д. Каждая ячейка датасета
описывается парой `[h3_index, level, cell_id]`, где `level` и `cell_id`
вычисляются по следующим формулам:
* level: integer в диапазоне -47... -120 равный ( (h3_index / 512) % 74) - 120.
* cell_id: integer в диапазоне 1...100 равный ( (h3_index / 512) % 100) + 1.
* (% - это остаток от деления, / - это целочисленное деление)

## Запуск

Нативный запуск при помощи poetry:
```bash
poetry install --only main --no-root
poetry env activate
poetry run uvicorn main:app --host 127.0.0.1 --port 8000
```

Запуск через docker-compose с удалением контейнера после нажатия CTRL+C
```bash
docker compose up; docker compose down
```

### Тесты

Для запуска pytest потребуется установить отдельную группу зависимостей
```bash
poetry install --only main,test --no-root
poetry env activate
poetry run pytest tests/api.py -v 
```