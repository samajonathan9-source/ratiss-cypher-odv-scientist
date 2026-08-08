FROM python:3.11-slim
RUN apt-get update && apt-get install -y docker.io curl && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p /app/workspace /app/data
EXPOSE 7860
CMD ["chainlit", "run", "app.py", "--port", "7860", "--host", "0.0.0.0"]
