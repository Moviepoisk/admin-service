FROM python:3.12
EXPOSE 8000
# create the app user
RUN addgroup --system app && adduser --system --group app

WORKDIR /app/

# https://docs.python.org/3/using/cmdline.html#envvar-PYTHONDONTWRITEBYTECODE
# Prevents Python from writing .pyc files to disk
ENV PYTHONDONTWRITEBYTECODE 1

# ensures that the python output is sent straight to terminal (e.g. your container log)
# without being first buffered and that you can see the output of your application (e.g. django logs)
# in real time. Equivalent to python -u: https://docs.python.org/3/using/cmdline.html#cmdoption-u
ENV PYTHONUNBUFFERED 1
ENV ENVIRONMENT prod
ENV TESTING 0


# Copy poetry.lock* in case it doesn't exist in the repo
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY ./app /app
RUN chmod +x run.sh

ENV PYTHONPATH=/app

# chown all the files to the app user
RUN chown -R app:app $HOME

USER app

CMD ["./run.sh"]
