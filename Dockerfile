# Imagen base ligera de Python
FROM alexisvg2520/holamundobase:1

# Crear y entrar al directorio de la app
WORKDIR /app

# Copiar el código de la aplicación
COPY app.py .

RUN chown -R appuser:appgroup /app

USER appuser

# Exponer el puerto donde correrá el servidor
EXPOSE 8080

# Ejecutar la aplicación
CMD ["python", "app.py"]