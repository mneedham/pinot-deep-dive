FROM python:3.11

WORKDIR /usr/src/app

COPY requirements.txt ./
COPY model.py ./
COPY loop.py ./

RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python"]
