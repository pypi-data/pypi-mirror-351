FROM python:3.11-slim

WORKDIR /app

# Install the library (in development, use local version)
COPY .. /app
RUN pip install -e .[dev]

# Copy integration test server application
COPY . /app/integration-test-server

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "integration-test-server.main:app", "--host", "0.0.0.0", "--port", "8000"]