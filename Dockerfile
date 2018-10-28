FROM frolvlad/alpine-python3

ENV APPHOME=/app
WORKDIR "$APPHOME"

COPY "./" "$APPHOME"
RUN pip install -r requirements.txt

CMD ["python3", "app.py"]
