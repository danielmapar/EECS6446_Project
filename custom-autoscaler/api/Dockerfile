FROM ubuntu:18.04

RUN apt-get update && \
    apt-get install --no-install-recommends -y \
    python3 python3-pip python3-dev python3-setuptools python3-dev gcc 

RUN pip3 install pip --upgrade
RUN pip3 install setuptools --upgrade 

# We copy just the requirements.txt first to leverage Docker cache
COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip3 install -r requirements.txt

COPY . /app

EXPOSE 5000

ENTRYPOINT [ "python3" ]

CMD [ "app.py" ]