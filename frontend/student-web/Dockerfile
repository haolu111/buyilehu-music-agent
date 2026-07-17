FROM node:22-alpine AS build

WORKDIR /app

COPY student-web/package.json student-web/package-lock.json ./
RUN npm ci

COPY student-web ./
RUN npm run build

FROM nginx:1.27-alpine

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80