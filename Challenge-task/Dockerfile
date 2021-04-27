#FROM python:3.8-alpine
FROM python:3.9-slim-buster
WORKDIR /app 
COPY . /app
#RUN apt-get update -y && apt-get install apt-file -y && apt-file update -y && apt-get install -y python3-dev build-essential

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

#RUN pip install --upgrade pyls -i https://pypi.python.org/simple
#RUN apk add --no-cache --virtual .build-deps gcc musl-dev \
    #&& pip install --no-cache-dir -r requirements.txt \
    #&& apk del .build-deps
#RUN pip install -r requirements.txt
#RUN pip3 install --trusted-host pypi.python.org -r requirements.txt
#RUN pip3 install --ignore-installed six watson-developer-cloud
EXPOSE 5000
ENV FLASK_APP=launch.py
#CMD python ./launch.py
CMD ["flask", "run", "--host", "0.0.0.0"]




