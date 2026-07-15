FROM node:22-bookworm-slim AS frontend-build

WORKDIR /build/frontend/review-console
COPY frontend/review-console/package.json frontend/review-console/package-lock.json ./
RUN npm ci
COPY frontend/review-console ./
COPY contracts /build/contracts
RUN npm run build

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
COPY contracts ./contracts
COPY third_party ./third_party
COPY --from=frontend-build /build/frontend/review-console/dist ./frontend/review-console/dist

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
