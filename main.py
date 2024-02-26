"""
this is a module doc string
"""
from typing import TYPE_CHECKING

from litestar import Litestar
from litestar.contrib.mako import MakoTemplateEngine
from litestar.di import Provide
from litestar.openapi import OpenAPIConfig, OpenAPIController
from litestar.params import Parameter
from litestar.repository._filters import LimitOffset
from litestar.static_files import StaticFilesConfig
from litestar.template import TemplateConfig

from litestar.contrib.sqlalchemy.plugins import AsyncSessionConfig, SQLAlchemyAsyncConfig, SQLAlchemyInitPlugin
import logging

from controllers.exercise_controller import ExerciseController, provide_limit_offset_pagination
from controllers.my_controller import MyAPIController
from models.base_model import Base
from models.exercise import Exercise
from models.exercise_step import ExerciseStep

from logger import logger

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class OpenAPIControllerExtra(OpenAPIController):
    """
    used to set the favicon
    """
    favicon_url = '/static-files/favicon.ico'


session_config = AsyncSessionConfig(expire_on_commit=False)
sqlalchemy_config = SQLAlchemyAsyncConfig(
    connection_string="sqlite+aiosqlite:///test.sqlite", session_config=session_config)
# Create 'db_session' dependency.
sqlalchemy_plugin = SQLAlchemyInitPlugin(config=sqlalchemy_config)


async def on_startup() -> None:
    """Initializes the database."""
    async with sqlalchemy_config.get_engine().begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


app = Litestar(
    route_handlers=[MyAPIController, ExerciseController],
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
    plugins=[SQLAlchemyInitPlugin(config=sqlalchemy_config)],
    dependencies={"limit_offset": Provide(provide_limit_offset_pagination, sync_to_thread=False)},
)
