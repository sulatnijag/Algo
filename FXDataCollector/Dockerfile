FROM python:3.9.1

WORKDIR /usr/src/app

COPY requirements.txt .

RUN pip3 install --no-cache-dir -r requirements.txt

CMD python3 ./FXDataCollector/capture_fx_prices.py