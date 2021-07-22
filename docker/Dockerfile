FROM python:3.8.6

RUN apt-get update && apt-get install -y \
    nano

WORKDIR /opt/
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ADD requirements.txt ./
RUN pip3 install -r requirements.txt

# Entrypoint
CMD ["python", "-u", "create_fake_data.py"]
