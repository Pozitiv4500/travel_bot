from config import POSTGRES_URI
import asyncpg

async def db_start():
    global conn

    conn = await asyncpg.connect(POSTGRES_URI)

    await conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT PRIMARY KEY,
            age INTEGER,
            home_name TEXT,
            latitude FLOAT,
            longitude FLOAT,
            bio TEXT,
            time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            username TEXT
        );
    """)
    await conn.execute("""
            CREATE TABLE IF NOT EXISTS Trips (
                trip_id SERIAL PRIMARY KEY,
                trip_name VARCHAR(255) UNIQUE NOT NULL,
                trip_description TEXT,
                user_id BIGINT REFERENCES Users(user_id)
            );
        """)
    await conn.execute("""
                CREATE TABLE IF NOT EXISTS Locations (
                    location_id SERIAL PRIMARY KEY,
                    trip_id BIGINT,
                    location_name TEXT,
                    latitude FLOAT,
                    longitude FLOAT,
                    visit_date DATE,
                    visit_end DATE,
                    FOREIGN KEY (trip_id) REFERENCES Trips(trip_id)
                );
            """)
    await conn.execute("""
                    CREATE TABLE IF NOT EXISTS TripParticipants (
                    participant_id SERIAL PRIMARY KEY,
                    trip_id BIGINT REFERENCES Trips(trip_id),
                    user_id BIGINT REFERENCES Users(user_id)
                    );
                """)


async def create_profile(user_id, age, home_name, latitude, longitude, bio, username):
    user = await conn.fetchrow("SELECT 1 FROM users WHERE user_id = $1", user_id)
    if not user:
        await conn.execute(
            """
            INSERT INTO users (user_id, age, home_name, latitude, longitude, bio, username)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            """,
            user_id, age, home_name, latitude, longitude, bio, username
        )

async def create_trip_db(user_id, trip_name, trip_description=None):

        await conn.execute(
            """
            INSERT INTO Trips (trip_name, trip_description,user_id)
            VALUES ($1, $2, $3)
            """,
            trip_name, trip_description, user_id
        )


async def check_user_exists(user_id):
    user = await conn.fetchrow("SELECT 1 FROM users WHERE user_id = $1", user_id)
    return user is not None


async def edit_profile(user_id, age=None, home_name=None, latitude=None, longitude=None, bio=None):
    update_fields = []
    if age is not None:
        update_fields.append(f"age = {age}")
    if home_name is not None:
        update_fields.append(f"home_name = '{home_name}'")
    if latitude is not None:
        update_fields.append(f"latitude = {latitude}")

    if longitude is not None:
        update_fields.append(f"longitude = {longitude}")
    if bio is not None:
        update_fields.append(f"bio = '{bio}'")

    if update_fields:
        update_query = ", ".join(update_fields)
        await conn.execute(f"UPDATE users SET {update_query} WHERE user_id = $1", user_id)
        return True
    else:
        return False
async def create_location(trip_name, location_name, latitude, longitude, visit_date, visit_end):
    trip_id = await get_trip_id_by_name(trip_name)

    query = """
        INSERT INTO Locations (trip_id,location_name, latitude, longitude, visit_date, visit_end)
        VALUES ($1, $2, $3, $4, $5, $6)
    """
    try:
        # Создаем запись о локации в базе данных
        await conn.execute(query, trip_id, location_name, latitude, longitude, visit_date, visit_end)
    except Exception as e:
        print(f"Ошибка при создании локации: {e}")


async def get_trip_id_by_name(trip_name):
    query = """
        SELECT trip_id FROM Trips WHERE trip_name = $1
    """
    try:
        trip_id = await conn.fetchval(query, trip_name)
        return trip_id
    except Exception as e:
        print(f"Ошибка при получении идентификатора путешествия: {e}")
        return None


async def get_user_trip_names(user_id):
    try:
        query = "SELECT trip_name FROM Trips WHERE user_id = $1"
        trip_names = await conn.fetch(query, user_id)
        return [trip['trip_name'] for trip in trip_names]
    except Exception as e:
        print(f"Error fetching trip names for user {user_id}: {e}")
        return []
async def get_user_trip_names_format(user_id):
    try:
        query = "SELECT trip_id, trip_name FROM Trips WHERE user_id = $1"
        trip_data = await conn.fetch(query, user_id)
        return [{'trip_id': trip['trip_id'], 'trip_name': trip['trip_name']} for trip in trip_data]
    except Exception as e:
        print(f"Error fetching trip names for user {user_id}: {e}")
        return []


async def get_trip_points(trip_id):
    query = """
        SELECT location_id, location_name, latitude, longitude, visit_date, visit_end
        FROM Locations
        WHERE trip_id = $1
        ORDER BY location_id
    """

    trip_points = await conn.fetch(query, int(trip_id))
    return trip_points


async def get_user_trips_with_locations(user_id):
    query = """
        SELECT Trips.trip_id, Trips.trip_name, Trips.trip_description,Locations.location_name, Locations.latitude, Locations.longitude, Locations.visit_date, Locations.visit_end
        FROM Trips
        INNER JOIN Locations ON Trips.trip_id = Locations.trip_id
        WHERE Trips.user_id = $1
        ORDER BY Trips.trip_id
    """
    try:
        trips_data = await conn.fetch(query, user_id)
        return trips_data
    except Exception as e:
        print(f"Ошибка при получении путешествий пользователя: {e}")
        return []


async def check_trip_existence(trip_name):
    query = """
        SELECT EXISTS(SELECT 1 FROM Trips WHERE trip_name = $1)
    """
    try:
        trip_exists = await conn.fetchval(query, trip_name)
        return trip_exists
    except Exception as e:
        print(f"Ошибка при проверке существования путешествия: {e}")
        return False


async def format_trip_message(trips_data):
    if not trips_data:
        return "У вас пока нет созданных путешествий."

    trip_message = "Путешествия:\n"
    current_trip_id = None
    for trip in trips_data:
        if trip['trip_id'] != current_trip_id:
            if current_trip_id is not None:
                trip_message += "\n"  # Добавляем пустую строку между путешествиями
            trip_message += f"🌍 Путешествие: {trip['trip_name']}\n"
            trip_message += f"   Описание: {trip['trip_description'] or '-'}\n"
            trip_message += "   Локации:\n"
            current_trip_id = trip['trip_id']
        trip_message += f"      - Место: {trip['location_name']} \n         -Дата посещения: {trip['visit_date']} \n         -Дата окончания посещения: {trip['visit_end']}\n"

    return trip_message

async def get_user_data(user_id):
    query = """
        SELECT age, home_name, bio
        FROM users
        WHERE user_id = $1
    """

    user_data = await conn.fetchrow(query, user_id)

    if user_data:
        age = user_data['age']
        home_name = user_data['home_name']
        bio = user_data['bio'] if user_data['bio'] is not None else "-"
        return {
            'age': age,
            'home_name': home_name,
            'bio': bio
        }
    else:
        return None

async def edit_trip_mod(trip_id, field, new_value):


    # Обновляем указанное поле путешествия в базе данных
    if field == 'name':
        await conn.execute("UPDATE trips SET trip_name = $1 WHERE trip_id = $2", new_value, int(trip_id))
    elif field == 'description':
        await conn.execute("UPDATE trips SET trip_description = $1 WHERE trip_id = $2", new_value, int(trip_id))

async def add_trip_point(trip_id, location_name, latitude, longitude, visit_date, visit_end):
    try:
        # Выполняем запрос на добавление новой точки маршрута в базу данных
        await conn.execute(
            "INSERT INTO Locations (trip_id, location_name, latitude, longitude, visit_date, visit_end) VALUES ($1, $2, $3, $4, $5, $6)",
            int(trip_id), location_name, latitude, longitude, visit_date, visit_end
        )
    except Exception as e:
        # Обрабатываем возможные ошибки при выполнении запроса
        print(f"Error adding trip point: {e}")
        raise e

async def delete_trip_point(point_id):
    try:

        # Выполняем запрос на удаление точки маршрута из базы данных
        await conn.execute("DELETE FROM Locations WHERE id = $1", point_id)
    except Exception as e:
        # Обрабатываем возможные ошибки при выполнении запроса
        print(f"Error deleting trip point: {e}")
        raise e

async def delete_trip_point_by_id(point_id):
    try:
        # Выполняем запрос на удаление точки маршрута из базы данных по её идентификатору
        await conn.execute(
            "DELETE FROM Locations WHERE location_id = $1",
            int(point_id)
        )
    except Exception as e:
        # В случае ошибки при удалении точки маршрута выводим сообщение в консоль
        print(f"Error deleting trip point: {e}")
        raise e
async def delete_trip_by_id(trip_id):
    try:
        # Удаляем все локации, связанные с данной поездкой
        await conn.execute("DELETE FROM Locations WHERE trip_id = $1", int(trip_id))
        # Затем удаляем саму поездку
        await conn.execute("DELETE FROM Trips WHERE trip_id = $1", int(trip_id))
    except Exception as e:
        print(f"Error deleting trip: {e}")
        raise e

async def add_friend_to_trip(username, trip_id):

        # Проверяем существует ли пользователь с указанным никнеймом
        query = "SELECT user_id FROM users WHERE username = $1"
        user_id = await conn.fetchval(query, username.replace("@", ""))
        if not user_id:
            return False, 1  # Код ошибки 1: Пользователь с указанным никнеймом не найден
        user_id=int(user_id)
        trip_id=int(trip_id)
        # Проверяем, является ли пользователь участником путешествия
        query = "SELECT EXISTS(SELECT 1 FROM TripParticipants WHERE user_id = $1 AND trip_id = $2)"
        is_member = await conn.fetchval(query, user_id, trip_id)
        if is_member:
            return True, 2  # Код ошибки 2: Пользователь уже является участником путешествия

        # Проверяем, является ли пользователь создателем путешествия
        query = "SELECT EXISTS(SELECT 1 FROM trips WHERE user_id = $1 AND trip_id = $2)"
        is_creator = await conn.fetchval(query, user_id, trip_id)
        if is_creator:
            return False, 3  # Код ошибки 3: Пользователь является создателем путешествия

        # Добавляем пользователя в участники путешествия
        query = "INSERT INTO TripParticipants (user_id, trip_id) VALUES ($1, $2)"
        await conn.execute(query, user_id, trip_id)

        return True, 0  # Успешное добавление пользователя в путешествие

async def get_friends_trips_names(user_id):
    try:
        query = """
                SELECT trips.trip_name
                FROM trips
                INNER JOIN TripParticipants ON trips.trip_id = TripParticipants.trip_id
                WHERE TripParticipants.user_id = $1
                """
        trip_names = await conn.fetch(query, user_id)
        return [trip['trip_name'] for trip in trip_names]
    except Exception as e:
        print(f"Ошибка при получении названий путешествий друзей для пользователя {user_id}: {e}")
        return []
async def get_joined_trips_info(user_id):
    query = """
        SELECT Trips.trip_id, Trips.trip_name, Trips.trip_description, Locations.location_name, Locations.latitude, Locations.longitude, Locations.visit_date, Locations.visit_end
        FROM Trips
        INNER JOIN Locations ON Trips.trip_id = Locations.trip_id
        INNER JOIN TripParticipants ON Trips.trip_id = TripParticipants.trip_id
        WHERE TripParticipants.user_id = $1
        ORDER BY Trips.trip_id
    """
    try:
        trips_data = await conn.fetch(query, int(user_id))
        return trips_data
    except Exception as e:
        print(f"Ошибка при получении путешествий пользователя: {e}")
        return []
