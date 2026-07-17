FROM node:22-alpine AS build

WORKDIR /app

COPY teacher-web/package.json teacher-web/package-lock.json ./
RUN npm ci

COPY teacher-web ./
RUN npm run build

FROM nginx:1.27-alpine

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80