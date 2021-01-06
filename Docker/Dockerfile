FROM ubuntu:21.04
ENV DEBIAN_FRONTEND="noninteractive" TZ="America/New_York" 
RUN apt update && apt install vim tzdata python3 python3-pip -y
RUN pip3 install flask