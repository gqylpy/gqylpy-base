FROM python:3.6

LABEL version='latest'
LABEL maintainer='137326237@qq.com'

COPY ./ /root/untitled/

WORKDIR /root/untitled/

RUN pip install -r requirements.txt -i https://pypi.douban.com/simple

CMD ["python", "go.py"]

# docker build -t untitled:latest .
