FROM node:22-alpine AS reviewed-activities

WORKDIR /review-console
COPY frontend/review-console/package.json frontend/review-console/package-lock.json ./
RUN npm ci
COPY frontend/review-console ./
COPY contracts /contracts
RUN npm run build

FROM node:22-alpine AS build
WORKDIR /app
COPY frontend/student-web/package.json frontend/student-web/package-lock.json ./
RUN npm ci
COPY frontend/student-web ./
COPY frontend/shared-activity-runtime /shared-activity-runtime
RUN npm run build

FROM nginx:1.27-alpine

COPY --from=build /app/dist /usr/share/nginx/html
COPY --from=reviewed-activities /review-console/dist /usr/share/nginx/html/template-console
COPY app/static /usr/share/nginx/html/static
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
