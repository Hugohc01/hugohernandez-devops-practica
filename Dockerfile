# Imagen de la API REST de la tienda online
# Construir:  docker build -t tienda-api:1.0 .
# Ejecutar:   docker run -p 8000:8000 tienda-api:1.0

# a) Imagen base ligera de Python 3.12
FROM python:3.12-slim

# Python sin ficheros .pyc y con la salida sin buffer (los logs salen al momento)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# b) Copiar primero solo las dependencias: si el codigo cambia pero
#    requirements.txt no, Docker reutiliza esta capa y no reinstala nada
COPY requirements.txt .

# c) Instalar las dependencias sin guardar la cache de pip (imagen mas pequena)
RUN pip install --no-cache-dir -r requirements.txt

# d) Copiar el codigo fuente de la API
COPY src/Tienda_online/ ./Tienda_online/

# e) Crear un usuario sin privilegios y darle permisos sobre el codigo,
#    para no ejecutar la aplicacion como root
RUN useradd --create-home --uid 1000 appuser \
    && chown -R appuser:appuser /app
USER appuser

WORKDIR /app/Tienda_online

# Puerto en el que escucha la API dentro del contenedor
EXPOSE 8000

# f) Comando de inicio: uvicorn escuchando en todas las interfaces (0.0.0.0),
#    necesario para poder acceder desde fuera del contenedor
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
