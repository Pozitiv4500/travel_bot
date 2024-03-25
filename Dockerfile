FROM python:3.11.8-alpine3.19

# Устанавливаем рабочую директорию в /app
WORKDIR /app

# Копируем зависимости проекта (файл requirements.txt)
COPY requirements.txt .

# Устанавливаем зависимости проекта
RUN pip install -r requirements.txt

# Копируем все файлы проекта в текущую директорию в образе
COPY . .

# Запускаем бот
CMD ["python", "bot.py"]