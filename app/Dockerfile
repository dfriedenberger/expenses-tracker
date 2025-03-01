# Basis-Image
FROM python:3.13-slim

# Setze das Arbeitsverzeichnis im Container
WORKDIR /app

# Installiere benötigte Pakete für Locale-Unterstützung
RUN apt-get update && \
    apt-get install -y locales
    
# Locale de_DE.UTF-8 generieren
RUN sed -i -e 's/# de_DE.UTF-8 UTF-8/de_DE.UTF-8 UTF-8/' /etc/locale.gen
RUN dpkg-reconfigure --frontend=noninteractive locales


# Kopiere die Abhängigkeitsdatei und installiere die Pakete
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Kopiere den restlichen Anwendungscode
COPY . .

# Exponiere den Port, auf dem FastAPI läuft
EXPOSE 8000

# Startkommando für die FastAPI-App
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
