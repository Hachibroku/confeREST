FROM python:3
# OS parameters
WORKDIR /app
COPY accounts accounts
COPY attendees attendees
COPY common common
COPY conference_go conference_go
COPY events events
COPY presentations presentations
COPY requirements.txt requirements.txt
COPY manage.py manage.py
RUN pip install -r requirements.txt
CMD gunicorn --bind 0.0.0.0:8000 conference_go.wsgi
