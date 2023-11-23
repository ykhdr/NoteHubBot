FROM python:latest

RUN pip install telebot && pip install pymysql && pip install cryptography && pip install sqlalchemy

COPY . /notehub
WORKDIR /notehub

CMD ["python3","main.py"]
