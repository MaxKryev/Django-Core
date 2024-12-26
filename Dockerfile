FROM python:3.12

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libpq-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /django_app

COPY requirements.txt /django_app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY . /django_app

COPY create_superuser.sh /django_app/create_superuser.sh
RUN chmod +x /django_app/create_superuser.sh

ENTRYPOINT ["/django_app/create_superuser.sh"]

CMD ["sh", "/django_app/create_superuser.sh"]
