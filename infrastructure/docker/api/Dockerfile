FROM python:3.12-slim

WORKDIR /app

# Copy only requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the api application
COPY apps/api/ .

# Create a non-root user to run the app (optional but recommended)
RUN adduser --disabled-password --gecos '' appuser
USER appuser

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]