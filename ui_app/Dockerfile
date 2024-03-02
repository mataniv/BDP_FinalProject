# Use an official Python runtime as a parent image
FROM python:3.8-slim

WORKDIR /app

COPY . /app

RUN pip install --trusted-host pypi.python.org -r requirements.txt

ENV OAUTH_TOKEN=oauth_token
ENV OAUTH_TOKEN_SECRET=oauth_token_secret
ENV VERIFIER=verifier

EXPOSE 5005

# Run app.py when the container launches
CMD ["python", "app.py"]
