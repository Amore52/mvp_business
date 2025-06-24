# Базовый образ с Python 3.13
FROM python:3.13-slim

# Рабочая директория
WORKDIR /team_management

# Копируем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# Копируем весь проект
COPY . .

# Открываем порт
EXPOSE 8000

# Запуск приложения через gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "your_project.wsgi"]