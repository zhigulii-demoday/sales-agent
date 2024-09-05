import asyncio
import sys
from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from api.routes import router as api_router

from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.staticfiles import StaticFiles

from messages.emai_scripts import wait_for_reply
from messages.telegram_scripts import main_listener

app = FastAPI(
    debug=False,
    title='API',
    openapi_url="/api/v2/openapi.json",
    docs_url=None,
    redoc_url=None,
    swagger_ui_parameters={'syntaxHighlight': False}
)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(main_listener())
    asyncio.create_task(wait_for_reply())

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
    )


@app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()


@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Документация",
        redoc_js_url="/static/redoc.standalone.js",
    )
    
    
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# app.add_event_handler("startup", init_logging)

# app.router.route_class = BodyLoggingRoute
app.include_router(api_router, prefix='')
