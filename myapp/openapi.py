from fastapi.openapi.utils import get_openapi
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)


OpenAPISchema = {
    "title": "My app",
    "version": "1.0.0",
    "description": "python web framework base on FastAPI.",
    "openapi_tags": [{
        "name": "desktop",
        "description": "Manage desktops."
    }, {
        "name": "user",
        "description": "Manage users."
    }, {
        "name": "log",
        "description": "Manage log."
    }]
}


def custom_openapi(app):
    """
    重新定义swagger的一些参数，包括文档全局设置（title/version等）以及使用本地静态资源。
    """
    def my_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        openapi_schema = get_openapi(
            title=OpenAPISchema["title"],
            version=OpenAPISchema["version"],
            description=OpenAPISchema["description"],
            routes=app.routes,
            tags=OpenAPISchema["openapi_tags"]
        )
        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi = my_openapi

    @app.get("/docs", include_in_schema=False)
    async def custom_swagger_ui_html():
        return get_swagger_ui_html(
            openapi_url=app.openapi_url,
            title=OpenAPISchema["title"] + " - Swagger UI",
            oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
            swagger_js_url="/static/swagger-ui-bundle.js",
            swagger_css_url="/static/swagger-ui.css",
            swagger_favicon_url="/static/favicon.ico"
        )

    @app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
    async def swagger_ui_redirect():
        return get_swagger_ui_oauth2_redirect_html()

    @app.get("/redoc", include_in_schema=False)
    async def redoc_html():
        return get_redoc_html(
            openapi_url=app.openapi_url,
            title=OpenAPISchema["title"] + " - ReDoc",
            redoc_js_url="/static/redoc.standalone.js",
            redoc_favicon_url="/static/favicon.ico"
        )
