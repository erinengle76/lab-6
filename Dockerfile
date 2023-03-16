FROM python:3.8

WORKDIR /app

COPY requirements.txt
RUN pip3 install requirements.txt

COPY jones_erin_lab-6.py /app
CMD ["python3", "jones_erin_lab-6.py"]