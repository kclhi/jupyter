FROM tiangolo/uvicorn-gunicorn-starlette:python3.7
COPY lib /lib
WORKDIR /lib/python-pgt
RUN python setup.py bdist_wheel
RUN pip install dist/pgt-0.1-py3-none-any.whl
WORKDIR /
COPY requirements.txt /
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app
