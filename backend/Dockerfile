FROM python:3.7-slim
WORKDIR /app
COPY requirements.txt .
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt --no-cache-dir
RUN apt-get update
RUN apt-get install wkhtmltopdf
COPY ./foodgram .
CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0.0.0.0:8000"]