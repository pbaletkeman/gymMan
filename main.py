"""
this is a module doc string
"""
from typing import TYPE_CHECKING

from litestar import Litestar
from litestar.contrib.mako import MakoTemplateEngine
from litestar.openapi import OpenAPIConfig, OpenAPIController
from litestar.static_files import StaticFilesConfig
from litestar.template import TemplateConfig

from controllers.my_controller import MyAPIController

if TYPE_CHECKING:

    from sqlalchemy.ext.asyncio import AsyncSession


class OpenAPIControllerExtra(OpenAPIController):
    """
    used to set the favicon
    """
    favicon_url = '/static-files/favicon.ico'


async def on_startup():
    """
    sample start up script
    """


app = Litestar(
    route_handlers=[MyAPIController],
    on_startup=[on_startup],
    openapi_config=OpenAPIConfig(
        title='My API', version='1.0.0',
        root_schema_site='elements',
        path='/docs',
        create_examples=False,
        openapi_controller=OpenAPIControllerExtra,
        use_handler_docstrings=True,
    ),
    static_files_config=[StaticFilesConfig(
        path='static-files',  # path used in links
        directories=['static-files']  # path on the server
    )],
    template_config=TemplateConfig(engine=MakoTemplateEngine, directory="templates"),
)


# uvicorn main:app
