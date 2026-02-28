FROM python:3.10-slim
# Pre-install the libraries you need
RUN pip install --no-cache-dir requests pandas numpy textblob