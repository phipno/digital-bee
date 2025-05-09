FROM python:3

# # Update and upgrade the package list
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "./data_collector.py" ]
