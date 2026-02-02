FROM python:3.10-slim

WORKDIR /app

# Copy backend
COPY unity-companion-backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY unity-companion-backend/ .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
