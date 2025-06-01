FROM python

# Устанавливаем переменные окружения
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Установка рабочей директории
WORKDIR /app

# Копируем зависимости
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

# Копируем всё в контейнер
COPY . .

# Открываем порт
EXPOSE 8000

# Команда запуска
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

