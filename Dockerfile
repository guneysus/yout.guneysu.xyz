FROM guneysu/python:3.6
ADD requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

ADD src /app/
WORKDIR /app

RUN apk add ffmpeg -U
CMD python main.py --port=8002 --debug=true


