### https://t.me/Travel_Prod_bot

### Конечный список шагов для запуска моего приложения

1. **Склонируйте репозиторий**: Сначала склонируйте репозиторий моего проекта с GitHub.

2. **Установите Docker и Docker Compose**: Убедитесь, что на вашем компьютере установлены Docker и Docker Compose. Если они еще не установлены, вы можете скачать их с официального сайта Docker.

3. **Запустите контейнеры**: После успешной сборки образа выполните команду `docker-compose up -d`, чтобы запустить контейнеры моего приложения в фоновом режиме.

После выполнения этих шагов моё приложение должно успешно запуститься. Вы можете проверить его работу, перейдя по ссылке https://t.me/Travel_Prod_bot.

### Информация о устройстве моего `docker-compose.yml`

- **Версия Docker Compose**: Файл начинается с указания версии Docker Compose, которую он использует. В моём случае это `version: '3.8'`.

- **Сервисы**:
  - **telegram-bot**: Описывает сервис для запуска вашего бота Telegram. Он использует Docker образ, собранный из текущего Dockerfile в корневой директории проекта. Сервис настроен на автоматический перезапуск (`restart: always`). В разделе `environment` указаны переменные окружения, необходимые для работы бота (например, токен бота Telegram и данные для подключения к PostgreSQL).
  - **db**: Описывает сервис для запуска базы данных PostgreSQL. Он использует официальный Docker образ PostgreSQL. Также настроен на автоматический перезапуск и содержит переменные окружения для настройки базы данных.

- **Переменные окружения**: В разделе `environment` каждого сервиса указаны переменные окружения, необходимые для работы приложения. Эти переменные используются внутри контейнеров для настройки приложений.


**Демонстрация работы приложения: Как использовать нашего Telegram бота**

Наш Telegram бот предназначен для удобного планирования и отслеживания путешествий, поиска достопримечательностей, кафе и других интересных мест во время путешествий.

### Демонстрация работы приложения: Как использовать нашего Telegram бота

Мой Telegram бот предназначен для удобного планирования путешествий.

**Основные функции:**

1. **Регистрация:**
- Через компьютер с указанием геопозиции

https://github.com/Central-University-IT-prod/backend-Pozitiv4500/assets/123630113/53a0fe19-f7c0-4d81-8e24-a57e6ab3e1c3


- Через телефон с отправкой геопозиции

https://github.com/Central-University-IT-prod/backend-Pozitiv4500/assets/123630113/6f79aced-1ee9-441b-9387-c38f888e0741

2. **Редактирование информации о себе:**
- Через компьютер с указанием геопозиции
https://github.com/Central-University-IT-prod/backend-Pozitiv4500/assets/123630113/e9bf7a00-b71a-4c56-99a7-a122174ba947



### Описание внешних интеграций

#### 1. Telegram API:
   - **Описание**: Используется для создания и управления телеграм-ботом.
   - **Почему выбрали**: Telegram API обеспечивает простоту взаимодействия с пользователем, а также широкие возможности для разработки функциональности чат-бота.

#### 2. PostgreSQL:
   - **Описание**: Реляционная база данных, используемая для хранения информации о пользователях, путешествиях и других данных, необходимых для функционирования бота.
   - **Почему выбрали**: PostgreSQL выбрана в качестве базы данных из-за своей надежности, масштабируемости, скорости и богатого функционала.

#### 3. OpenWeatherMap API:
   - **Описание**: Предоставляет информацию о погоде для заданных географических координат.
   - **Почему выбрали**: OpenWeatherMap API позволяет получать актуальные данные о погоде, которые могут быть использованы для предоставления пользователю информации о текущей погоде и прогнозе на ближайшие дни.

#### 4. Foursquare API:
   - **Описание**: Предоставляет доступ к информации о достопримечательностях, кафе и других местах в указанных географических координатах.
   - **Почему выбрали**: Foursquare API используется для получения данных о местоположениях, таких как достопримечательности и кафе, вокруг заданной локации. Это позволяет предоставить пользователям дополнительную информацию о местах, которые они могут посетить во время путешествия.

#### 5. GraphHopper API:
   - **Описание**: Предоставляет сервис построения маршрутов и карт на основе географических данных.
   - **Почему выбрали**: GraphHopper API используется для создания интерактивных карт с отмеченными местами, достопримечательностями и кафе, а также для построения оптимальных маршрутов между ними. Это обогащает пользовательский опыт и позволяет более наглядно представить информацию о путешествиях.


### Описание API

#### Telegram API:
   - **sendMessage**: Метод для отправки текстовых сообщений пользователю.
   - **editMessageText**: Метод для редактирования текстовых сообщений.
   - **answerCallbackQuery**: Метод для ответа на callback-запросы от пользователя.
   - **answerInlineQuery**: Метод для отправки ответов на встроенные запросы (inline queries).
   - **sendPhoto**: Метод для отправки фотографий пользователю.
   - **sendDocument**: Метод для отправки документов пользователю.
   - **...и многое другое**: Telegram API предоставляет широкий набор методов для взаимодействия с ботом и управления чатами, которые позволяют реализовать различные функциональные возможности бота.

#### OpenWeatherMap API:
   - **Current Weather Data**: Метод для получения текущей погоды по координатам.
   - **One Call API**: Метод для получения прогноза погоды на несколько дней вперед по координатам.

#### Foursquare API:
   - **Places API**: Метод для поиска местоположений (достопримечательностей, кафе и т. д.) по координатам.
   - **Venue Details API**: Метод для получения дополнительной информации о конкретном местоположении (например, описания, часы работы и т. д.).





### Схема данных в СУБД:

1. **Таблица "users"**:
   - **user_id**: Уникальный идентификатор пользователя (PRIMARY KEY).
   - **age**: Возраст пользователя.
   - **home_name**: Название домашнего местоположения пользователя.
   - **latitude**: Широта домашнего местоположения пользователя.
   - **longitude**: Долгота домашнего местоположения пользователя.
   - **bio**: Биография пользователя.
   - **time**: Время создания записи (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP).
   - **username**: Имя пользователя.

2. **Таблица "Trips"**:
   - **trip_id**: Уникальный идентификатор путешествия (SERIAL, PRIMARY KEY).
   - **trip_name**: Название путешествия (UNIQUE, NOT NULL).
   - **trip_description**: Описание путешествия.
   - **user_id**: Ссылка на пользователя, создавшего путешествие (FOREIGN KEY REFERENCES Users(user_id)).

3. **Таблица "Locations"**:
   - **location_id**: Уникальный идентификатор местоположения (SERIAL, PRIMARY KEY).
   - **trip_id**: Ссылка на путешествие, к которому относится местоположение (FOREIGN KEY REFERENCES Trips(trip_id)).
   - **location_name**: Название местоположения.
   - **latitude**: Широта местоположения.
   - **longitude**: Долгота местоположения.
   - **visit_date**: Дата начала посещения.
   - **visit_end**: Дата окончания посещения.

4. **Таблица "TripParticipants"**:
   - **participant_id**: Уникальный идентификатор участника путешествия (SERIAL, PRIMARY KEY).
   - **trip_id**: Ссылка на путешествие, в котором участвует участник (FOREIGN KEY REFERENCES Trips(trip_id)).
   - **user_id**: Ссылка на пользователя, участвующего в путешествии (FOREIGN KEY REFERENCES Users(user_id)).

5. **Таблица "TripNotes"**:
   - **note_id**: Уникальный идентификатор заметки (SERIAL, PRIMARY KEY).
   - **trip_id**: Ссылка на путешествие, к которому относится заметка (FOREIGN KEY REFERENCES Trips(trip_id)).
   - **user_id**: Ссылка на пользователя, создавшего заметку (FOREIGN KEY REFERENCES Users(user_id)).
   - **message_type**: Тип сообщения (текстовое сообщение, фотография, документ и т. д.).
   - **File_id**: Идентификатор файла, связанного с заметкой.
   - **note_date**: Дата создания заметки (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP).
   - **is_private**: Флаг приватности заметки (TRUE, если заметка приватная, FALSE, если общедоступная).
  
![PosgreSQL](https://github.com/Central-University-IT-prod/backend-Pozitiv4500/assets/123630113/2823c93c-90b2-456a-91b8-48f70eee27ce)

