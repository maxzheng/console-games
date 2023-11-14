FROM python:3-alpine

WORKDIR /console-games

COPY setup.py requirements.txt README.rst .
COPY games games

RUN pip install --no-cache-dir .

CMD ["play"]
