FROM python:3.8

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

ENV CONSUMER_KEY=consumer_key
ENV CONSUMER_SECRET=consumer_secret


EXPOSE 5003

# Run app.py when the container launches
CMD ["python", "post.py"]
