# Imagen base ligera de Python
FROM python:3.11-slim

# Crear y entrar al directorio de la app
WORKDIR /app

# Copiar el código de la aplicación
COPY app.py .

# Exponer el puerto donde correrá el servidor
EXPOSE 8080

# Ejecutar la aplicación
CMD ["python", "app.py"]