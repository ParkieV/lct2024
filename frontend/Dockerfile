# Используем базовый образ с Node.js
FROM node:20 as build

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем package.json и package-lock.json для установки зависимостей
COPY package*.json ./

# Устанавливаем зависимости
RUN npm install

# Копируем исходный код приложения в контейнер
COPY . .

# Выполняем сборку приложения
RUN npm run build

FROM caddy:2-alpine as serve

COPY --from=build /app/build /srv
