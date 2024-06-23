from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse


from .src.routers import v1_router

description = """
Сервис для взаимодействия с ML частью проекта. Разработано в рамках задачи №2 хакатона "Лидеры цифровой трансформации 2024" командой "МИСИС Два Миллиона". 

## Описание ML сервиса
ML сервис предназначен для работы с данными о закупках и остатках товаров.
Сервис предоставляет возможность прогнозирования закупок, поиска похожих товаров, а также аналитики по выбранному пользователем товару.

**Важно! Все ручки требуют передачи уникального индентификатора пользователя. В нашем решении туда передается telegram ID**
"""

tags_metadata = [
    {
        "name": "v1",
        "description": "Все эндпоинты ML сервиса",
    },
    {
        "name": "Matching Service",
        "description": """
Эндпоинты для поиска похожих товаров и инициализации модели с выбранным товаром
        
## /v1/ml/matching/show_reference
Поиск похожих в справочнике товаров по введенному запросу

## /v1/ml/matching/set_user_pick
Инициализация модели с выбранным пользователем товаром

***Внимание! Без вызова данного запроса не будут работать запросы к API во вкладках Forecast Service, Other Endpoints, Analytics Endpoints for User Pick!***
        """,
    },
    {
        "name": "Forecast Service",
        "description": """
Эндпоинты для прогнозирования

## /v1/ml/forecast/forecast
Прогнозирование следующих закупок выбранного товара

Принимает на вход period (1 - год, 2 - квартал, 3 - месяц)
        """,
    },
    {
        "name": "Other Endpoints",
        "description": """
Другие эндпоинты ML сервиса

## /v1/ml/other/leftover_name
Получить похожий на выбранный товар остаток на складе

## /v1/ml/other/check_regularity
Проверка товара на регулярность в закупках

## /v1/ml/other/get_user_pick_info
Получить информацию о выбранном товаре (СТЕ, Код, Наименование)
        """
    },
    {
        "name": "Analytics Endpoints for User Pick",
        "description": """
Эндпоинты аналитики для выбранного пользователем товара

## /v1/ml/analytics/leftover_info
Получить информацию об остатках похожего товара на складе

Возращает json со статусом запроса (Success или Wrong plot), датафреймом и изображением графика (в base64 формате)

## /v1/ml/analytics/history
Вернуть N последних закупок выбранного товара

Возращает json с файлом excel в base64 формате

## /v1/ml/analytics/debit_credit_info
Получить информацию об ОС ведомости с выбранным товаром

Ожидает bool параметр credit (True - сумма, False - количество)

Возращает json со статусом запроса (Success или Wrong plot), датафреймом кредита/дебета, и изображением графика (в base64 формате)

## /v1/ml/analytics/purchase_stats
Получить статистику закупок по выбранному товару по годам, кварталам или месяцам

Принимает на вход period (1 - год, 2 - квартал, 3 - месяц) и summa (True - сумма, False - количество)

Возращает json со статусом запроса (Success или Wrong plot), датафреймом и изображением графика (в base64 формате)
        """
    },
    {
        "name": "Analytics Endpoints for Everything",
        "description": """
Аналитика для всех товаров

## /v1/ml/analytics_all/history
Вернуть N последних закупок всех товаров

Возращает json с файлом excel в base64 формате

## /v1/ml/analytics_all/purchase_stats
Получить статистику закупок по всем товарам по годам, кварталам или месяцам

Принимает на вход period (1 - год, 2 - квартал, 3 - месяц) и summa (True - сумма, False - количество)

Возращает json со статусом запроса (Success или Wrong plot), датафреймом и изображением графика (в base64 формате)

        """
    },
    {
        "name": "Speech2Text Endpoints",
        "description": """
Сервис для расшифровки голосовых запросов

## /v1/ml/s2t/transcribe
Расшифровка голосового запроса

Принимает в теле на вход аудио файл зашифрованный в base64 формате

Возвращает расшифровку данного аудио
        """
    },
]

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


def create_application():
    return FastAPI(
        title="ML API",
        description=description,
        version="1.0.1",
        responses={404: {"description": "Not Found!"}},
        default_response_class=ORJSONResponse,
        lifespan=lifespan,
        openapi_tags=tags_metadata,
        root_path="/api_ml"
    )

app = create_application()

origins = [
    'http://localhost',
    'http://localhost:8080',
    '*'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)


def _configure():
    app.include_router(v1_router)

_configure()