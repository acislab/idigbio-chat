# Based on https://github.com/docker/awesome-compose/blob/18f59bdb09ecf520dd5758fbf90dec314baec545/nginx-wsgi-flask/flask/Dockerfile

FROM ubuntu:24.04

RUN apt-get update -y\
 && apt-get install -y\
      postgresql\
      libpq-dev\
      python3-pip\
      python3.12-venv

# Permissions and nonroot user for tightened security
RUN adduser --disabled-password nonroot
RUN mkdir /home/app/ && chown -R nonroot:nonroot /home/app
RUN mkdir -p /var/log/flask-app && touch /var/log/flask-app/flask-app.err.log && touch /var/log/flask-app/flask-app.out.log
RUN chown -R nonroot:nonroot /var/log/flask-app
WORKDIR /home/app
USER nonroot

# Copy all the files to the container
COPY --chown=nonroot:nonroot . .

# venv
ENV VIRTUAL_ENV=/home/app/venv

# Python setup
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN pip3 install -r requirements.txt

# Define the port number the container should expose
EXPOSE 8989

WORKDIR /home/app/backend

CMD ["python3", "app.py"]