FROM python:3.8

RUN python -m pip install --upgrade pip
#RUN apt-get update && apt-get install -y gcc make-apt-transport-https ca-certificates build-essential

RUN python --version
RUN pip --version
#RUN pip install https://github.com/pyinstaller/pyinstaller/archive/develop.tar.gz
    
WORKDIR /code

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY / .

CMD ["python", "./mongo.py"]

