# Imagen base: Python 3.9-slim
FROM python:3.9-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema necesarias para compilar drivers de MySQL
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements.txt
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY . .

# Exponer puerto 5000
EXPOSE 5000

# Variable de entorno para Python sin buffer (mejor para logs en Docker)
ENV PYTHONUNBUFFERED=1

# Comando para ejecutar el servidor Flask
CMD ["python", "-u", "server.py"]
