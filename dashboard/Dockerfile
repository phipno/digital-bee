FROM python:alpine

RUN apk update && apk upgrade --no-cache
RUN apk add build-base libpq libpq-dev

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD [ "python3", "-m", "flask", "run", "--host=0.0.0.0", "--debug"]
