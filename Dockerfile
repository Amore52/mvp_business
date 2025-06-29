FROM python:3.13-slim
WORKDIR /app
COPY team_management/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
WORKDIR /app/team_management
COPY . /app
RUN python manage.py migrate
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]