FROM osgeo/gdal:ubuntu-small-latest
WORKDIR /app
COPY requirements.txt requirements.txt
RUN apt update && apt install python3-pip libpq-dev --yes
RUN python3 -m pip install -r requirements.txt
EXPOSE 8888
CMD jupyter-notebook --ip 0.0.0.0 --allow-root
