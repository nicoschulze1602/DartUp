# 1. Basis-Python-Image
FROM python:3.12-slim

# 2. Arbeitsverzeichnis im Container
WORKDIR /app

# 3. Requirements zuerst kopieren (damit Docker Cache nutzt)
COPY requirements.txt .

# 4. Dependencies installieren
RUN pip install --no-cache-dir -r requirements.txt

# 5. Restlichen Code kopieren
COPY . .

# 6. Default command → API starten
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]