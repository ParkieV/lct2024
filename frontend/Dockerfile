# Используем базовый образ с Node.js
FROM node:20 AS build

# Устанавливаем рабочую директорию в контейнере
WORKDIR /usr/src/app

# Копируем package.json и package-lock.json для установки зависимостей
COPY package.json package-lock.json ./

# Устанавливаем зависимости
RUN npm install

# Копируем исходный код приложения в контейнер
COPY . .

ENV NODE_TLS_REJECT_UNAUTHORIZED=0

# Выполняем сборку приложения
RUN npm run build

FROM caddy:2-alpine AS serve

COPY --from=build /usr/src/app/build /srv
