FROM python:3.11-slim

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt

RUN python db.py 

CMD uvicorn main:app --host 0.0.0.0 --port 8000 --reload 
