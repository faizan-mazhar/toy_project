FROM python:3.11.4-buster as builder

WORKDIR /app

# Copy rquired code files
COPY article ./article
COPY project ./project
COPY user ./user
COPY manage.py ./
COPY requirement.txt ./

RUN pip install -r requirement.txt

EXPOSE 8000
CMD ["python", "main.py"]
