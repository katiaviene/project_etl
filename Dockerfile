FROM python:3.10-slim

WORKDIR /app

COPY . /app/

RUN python3 -m venv /venv

RUN /venv/bin/pip install --upgrade pip
RUN /venv/bin/pip install -r requirements.txt
ENV PATH="/venv/bin:$PATH"
CMD ["python", "main.py"]
