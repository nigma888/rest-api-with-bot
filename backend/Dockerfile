FROM python:latest

WORKDIR /backend

COPY requirements.txt .
COPY entrypoint.sh .

ENV PYTHONDONTWRITEBYTECODE 1

RUN pip install --no-cache-dir --upgrade -r requirements.txt
RUN chmod +x entrypoint.sh

ENTRYPOINT [ "./entrypoint.sh" ]
