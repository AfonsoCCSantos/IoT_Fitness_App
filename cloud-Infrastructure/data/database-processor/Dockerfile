# Base image
FROM python:3.9

# Set working directory
WORKDIR /databaseprocessor

# Copy files
COPY app.py /databaseprocessor
COPY requirements.txt /databaseprocessor

# Install dependencies
RUN pip install -r requirements.txt

# Run the application
EXPOSE 8500
ENTRYPOINT ["gunicorn", "-b", "0.0.0.0:8500", "--access-logfile", "-", "--error-logfile", "-", "--timeout", "120"]
CMD ["app:app"]