FROM python:3.11.11

RUN apt-get update && apt-get install -y \
    nano

# Conditionally trust the custom DataHub *Dev/Test-only* Certificate Authority (CA) for iRODS-SSL-connections
ADD ssl-dev/test_only_dev_irods_dh_ca_cert.pem /tmp/test_only_dev_irods_dh_ca_cert.pem
ARG SSL_ENV
# Note: Python docker image is Debian-based. So, 'dash' as /bin/sh.
#       Strict POSIX-compliant.
RUN if [ $SSL_ENV != "acc" ] && [ $SSL_ENV != "prod" ]; then \
        echo "Adding custom DataHub iRODS-CA-certificate to the CA-rootstore (FOR DEV & TEST ONLY!)..." ; \
        cp /tmp/test_only_dev_irods_dh_ca_cert.pem /usr/local/share/ca-certificates/test_only_dev_irods_dh_ca_cert.crt ; \
        update-ca-certificates ; \
    else \
        echo "Not in dev environment: Skipping update of the CA-rootstore" ; \
    fi

WORKDIR /opt/
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ADD docker/requirements.txt ./
RUN pip3 install -r requirements.txt
RUN chmod 777 -R /usr/local/lib/python*

# Entrypoint
CMD ["python", "-u", "create_fake_data.py"]
