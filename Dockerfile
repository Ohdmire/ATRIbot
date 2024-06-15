FROM python:3.10-alpine
LABEL authors="ATRIbot"

WORKDIR /app

COPY requirements.txt /app/

RUN pip install\
    -i https://pypi.tuna.tsinghua.edu.cn/simple\
    --trusted-host pypi.tuna.tsinghua.edu.cn\
    --default-timeout=60\
    --no-cache-dir\
    -r requirements.txt

COPY . /app/

ARG PORT=8008
ARG MONGO_URI
ARG OSU_CLIENT_ID
ARG OSU_CLIENT_SECRET

ENV PORT=${PORT}
ENV MONGO_URI=${MONGO_URI}
ENV OSU_CLIENT_ID=${OSU_CLIENT_ID}
ENV OSU_CLIENT_SECRET=${OSU_CLIENT_SECRET}

EXPOSE ${PORT}

ENTRYPOINT ["python", "main.py"]