FROM python:alpine

RUN apk update && apk upgrade --no-cache
RUN apk add build-base libpq libpq-dev

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "./data_collector.py" ]
