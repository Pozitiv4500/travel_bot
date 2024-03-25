import os
import datetime
import requests
from staticmap import StaticMap, Line, IconMarker

# Функция для получения маршрута с GraphHopper API
async def get_route_points(points):
    try:
        url = "https://graphhopper.com/api/1/route"
        key = os.getenv('MAPS_KEY')

        query = {"key": key}
        payload = {
            "points": list(points),
            "vehicle": "car",
            "locale": "ru",
            "instructions": True,
            "calc_points": True,
            "points_encoded": False
        }
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, json=payload, headers=headers, params=query)
        data = response.json()

        points = data['paths'][0]['points']['coordinates']
        return points
    except:
        return None



# Создание статической карты с помощью staticmap
async def create_static_map(route_points, trip_points):
    m = StaticMap(800, 600)

    # Добавляем линию маршрута
    line = Line(route_points, 'blue', 5)
    m.add_line(line)

    # Флаг для определения первой точки
    first_point = True

    # Добавляем маркеры на всех точках маршрута
    for point in trip_points:
        if first_point:
            marker = IconMarker((point['longitude'], point['latitude']), 'IconMarker/webpeditor_sticker_green.webp', 34, 60)
            first_point = False
        else:
            marker = IconMarker((point['longitude'], point['latitude']), 'IconMarker/webpeditor_sticke_red.webp', 34, 60)
        m.add_marker(marker)

    current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    # Рендерим карту и сохраняем изображение
    image = m.render()
    image_path = f'Images/route_map_{current_time}.png'
    image.save(image_path)

    return image_path
