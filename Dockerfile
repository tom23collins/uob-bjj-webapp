# Python 3.12 has official ARM64 images and matches the versions required by
# the current dependency set (notably NumPy 2.x).
FROM python:3.12-slim-bookworm

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000
ENV PORT=5000

# Run as an unprivileged user in production.
RUN useradd --create-home --uid 10001 appuser \
    && chown -R appuser:appuser /app
USER appuser

CMD ["sh", "-c", "exec gunicorn --bind 0.0.0.0:${PORT} --workers 2 --threads 4 --timeout 60 wsgi:app"]
