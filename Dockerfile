FROM python:3.9.9

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /code

RUN pip freeze > requirements.txt
COPY requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt --trusted-host pypi.org --trusted-host files.pythonhosted.org

COPY ./core /code/

CMD [ "python", "manage.py" ]