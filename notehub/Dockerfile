FROM python:latest

RUN pip install telebot && pip install psycopg2 && pip install sqlalchemy

COPY . /notehub
WORKDIR /notehub

CMD ["python3","main.py"]
