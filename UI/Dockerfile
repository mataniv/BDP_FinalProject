FROM python:3.10

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

# Make port 5004 available to the world outside this container
EXPOSE 5004

# Run app.py when the container launches
CMD ["python", "UI.py"]