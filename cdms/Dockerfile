FROM python:3.14-slim

ARG APP_HOME=/app/

WORKDIR ${APP_HOME}

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update \
	&& apt-get install --no-install-recommends -y libpq-dev \
	&& rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

COPY requirements.txt ${APP_HOME}

RUN pip install --no-cache-dir -r requirements.txt

COPY . ${APP_HOME}

EXPOSE 8001

CMD ["python", "manage.py", "runserver", "0.0.0.0:8001"]
