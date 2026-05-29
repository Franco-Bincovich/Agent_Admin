FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema necesarias para PyMuPDF y bcrypt
RUN apt-get update && apt-get install -y \
    gcc \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código
COPY . .

# Puerto de la aplicación
EXPOSE 8000

# Comando de inicio
# NOTA: con múltiples workers, slowapi rate limiting es in-memory por
# proceso. Límites efectivos = límite_configurado × workers.
# Para rate limiting exacto en producción, configurar Redis backend.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
