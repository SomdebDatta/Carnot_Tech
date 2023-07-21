FROM python:3.11-slim

COPY requirements.txt .

RUN pip install --no-cache-dir --user -r requirements.txt

ENV PATH=/root/.local/bin:$PATH

COPY . /app

WORKDIR /app

RUN rm requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]