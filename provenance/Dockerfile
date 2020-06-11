FROM tiangolo/uvicorn-gunicorn-starlette:python3.7
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app
