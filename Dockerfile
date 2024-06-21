FROM python:3.12

WORKDIR /app

ADD . /app

RUN python -m pip install --upgrade pip \
    && python -m venv venv \
    && source venv/bin/activate \
    && pip install -r requirements.txt

EXPOSE 80

CMD ["venv/bin/python", "src/main.py"]