# Use a specific Python version for reproducibility
FROM python:3.11-slim-bullseye

# Label the image with metadata
LABEL maintainer="Naveen Kumar (naveenroy008@gmail.com)"
LABEL description="IMCP (Insecure Model Context Protocol) - Educational AI security framework"
LABEL version="1.0.0"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=5000 \
    FLASK_APP=app.py \
    FLASK_ENV=development \
    MOCK_MODE=False

# Create a non-root user to run the application
RUN addgroup --system imcp && \
    adduser --system --ingroup imcp imcp

# Set the working directory and change ownership
WORKDIR /app
RUN chown -R imcp:imcp /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy requirements file and install dependencies
COPY --chown=imcp:imcp requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY --chown=imcp:imcp . .

# Create the dotenv file if it doesn't exist
RUN touch .env

# Switch to the non-root user
USER imcp

# Expose the port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/ || exit 1

# Run the application
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0"]