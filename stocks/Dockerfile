# FROM python:alpine3.12
WORKDIR ./app
COPY stocks.py .
RUN pip install Flask requests pymongo
ENV FLASK_APP=stocks.py
ENV FLASK_RUN_PORT=8000
ENV NINJA_API_KEY=JtneO16sSFCqKQ8bJqYLEA==yqfESh50NJdz5O5Q
EXPOSE 8000
CMD ["flask", "run", "--host=0.0.0.0"]


