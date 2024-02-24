from typing import Annotated

import anyio
from litestar import Controller, post, get
from litestar.datastructures import UploadFile
from litestar.enums import RequestEncodingType
from litestar.params import Body, Parameter


class MyAPIController(Controller):
    """
    sample doc string
    """

    path = 'api/v1'

    @post(path="/upload-file", tags=['My Tag'])
    async def handle_file_upload(self,
                                 data: Annotated[list[UploadFile], Body(media_type=RequestEncodingType.MULTI_PART)],
                                 ) -> list[str]:
        """
        ### Sample file upload
        #### put markdown here

        param data: form data

        return:

        **list of uploaded files**
        """
        file_names: list[str] = []
        for file in data:
            content = await file.read()
            await anyio.Path(file.filename).write_bytes(content)
            file_names.append(file.filename)

        return file_names

    @get(path='/sample/{variable:str}')
    async def display_variable(self, variable: str) -> str:
        """

        :param variable:
        :return:
        """
        return variable

    @get(path='/querystring')
    async def display_querystring(self,
                                  variable: str = Parameter(
                                      title='Variable',
                                      description='## sample variable ##')
                                  ) -> str:
        """

        :param variable:
        :return:
        """
        return variable
