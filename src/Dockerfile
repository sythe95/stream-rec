# Base Image (Lightweight Python)
FROM python:3.10-slim

# Set working directory inside container
WORKDIR /app

# Install System Dependencies (needed for some Python packages)
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Install Python Dependencies
# We list them explicitly to keep the image small and predictable
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    pandas \
    mlflow \
    boto3 \
    feast \
    redis \
    scikit-learn

# Copy your source code into the container
# We copy everything so the 'feature_repo' folder is included
COPY . /app

# Expose the port the app runs on
EXPOSE 8000

# Command to run the app
# host 0.0.0.0 is crucial for Docker networking!
CMD ["uvicorn", "predict_model:app", "--host", "0.0.0.0", "--port", "8000"]