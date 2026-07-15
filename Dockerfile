<<<<<<< HEAD:Dockerfile
FROM node:22-bookworm-slim AS frontend-build

WORKDIR /build/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend ./
RUN npm run build

FROM python:3.12-slim
=======
FROM python:3.11-slim
>>>>>>> 9f27bf0 (保存我的本地修改):backend/python-capability-library/Dockerfile

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
<<<<<<< HEAD:Dockerfile
=======
RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*
>>>>>>> 9f27bf0 (保存我的本地修改):backend/python-capability-library/Dockerfile
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
COPY contracts ./contracts
<<<<<<< HEAD:Dockerfile
COPY third_party ./third_party
COPY --from=frontend-build /build/frontend/dist ./frontend/dist

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
=======

EXPOSE 8001
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
>>>>>>> 9f27bf0 (保存我的本地修改):backend/python-capability-library/Dockerfile
