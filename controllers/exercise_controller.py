from __future__ import annotations

from typing import TYPE_CHECKING

from litestar.exceptions import HTTPException
from litestar.pagination import OffsetPagination
from litestar.repository.filters import OrderBy

from litestar import get, status_codes
from litestar.contrib.sqlalchemy.repository import SQLAlchemyAsyncRepository
from litestar.controller import Controller
from litestar.di import Provide
from litestar.handlers.http_handlers.decorators import delete, post, put, patch
from litestar.params import Parameter
from litestar.repository.filters import LimitOffset
from pydantic import TypeAdapter

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

from models.exercise import Exercise, ExerciseCreate, ExerciseDTO
from logger import logger


class ExerciseRepository(SQLAlchemyAsyncRepository[Exercise]):
    """Exercise repository"""

    model_type = Exercise


async def provide_exercise_repo(db_session: AsyncSession) -> ExerciseRepository:
    """This provides a simple example demonstrating how to override the join options
    for the repository."""
    return ExerciseRepository(session=db_session)


class ExerciseController(Controller):
    path = '/exercise'
    dependencies = {
        'exercise_repo': Provide(provide_exercise_repo),
    }
    exercise_controller_tag = ['Exercise - CRUD']

    @get(tags=exercise_controller_tag)
    async def list_exercise(
            self,
            exercise_repo: ExerciseRepository,
            limit_offset: LimitOffset,
    ) -> OffsetPagination[ExerciseDTO]:
        """## List Exercise Items"""
        try:
            order_by1 = OrderBy(field_name=Exercise.name)
            results, total = await exercise_repo.list_and_count(limit_offset, order_by1)
            type_adapter = TypeAdapter(list[ExerciseDTO])
            return OffsetPagination[ExerciseDTO](
                items=type_adapter.validate_python(results),
                total=total,
                limit=limit_offset.limit,
                offset=limit_offset.offset,
            )
        except Exception as ex:
            raise HTTPException(detail=str(ex), status_code=status_codes.HTTP_404_NOT_FOUND)

    @get('/details/{exercise_id: int}', tags=exercise_controller_tag)
    async def get_exercise_details(self,
                                   exercise_repo: ExerciseRepository,
                                   exercise_id: int = Parameter(title='Exercise ID',
                                                                description='Primary Key Of The Exercise To Update.', ),
                                   ) -> ExerciseDTO:
        """## Get Details Of An Exercise Record"""
        try:
            obj = await exercise_repo.get_one(id=exercise_id)
            return ExerciseDTO.model_validate(obj)
        except Exception as ex:
            raise HTTPException(detail=str(ex), status_code=status_codes.HTTP_404_NOT_FOUND)

    @post(tags=exercise_controller_tag)
    async def create_exercise(self, exercise_repo: ExerciseRepository,
                              data: ExerciseCreate, ) -> ExerciseDTO:
        """## Create A New Exercise"""
        try:
            _data = data.model_dump(exclude_unset=True, by_alias=False, exclude_none=True)
            obj = await exercise_repo.add(Exercise(**_data))
            await exercise_repo.session.commit()
            return ExerciseDTO.model_validate(obj)
        except Exception as ex:
            raise HTTPException(detail=str(ex), status_code=status_codes.HTTP_404_NOT_FOUND)

    @put('/{exercise_id:int}', tags=exercise_controller_tag)
    async def update_exercise_put(
            self,
            exercise_repo: ExerciseRepository,
            data: ExerciseCreate,
            exercise_id: int = Parameter(title='Exercise ID', description='Primary Key Of The Exercise To Update.', ),
    ) -> ExerciseCreate:
        """## Update An Exercise"""
        try:
            _data = data.model_dump(exclude_unset=False, exclude_none=False)
            _data.update({'id': exercise_id})
            obj = await exercise_repo.update(Exercise(**_data))
            await exercise_repo.session.commit()
            return ExerciseCreate.model_validate(obj)
        except Exception as ex:
            raise HTTPException(detail=str(ex), status_code=status_codes.HTTP_404_NOT_FOUND)

    @patch('/{exercise_id:int}', tags=exercise_controller_tag)
    async def update_exercise_patch(
            self,
            exercise_repo: ExerciseRepository,
            data: ExerciseCreate,
            exercise_id: int = Parameter(title='Exercise ID', description='Primary Key Of The Exercise To Update.', ),
    ) -> ExerciseCreate:
        """## Update An Exercise"""
        try:
            _data = data.model_dump(exclude_unset=True, exclude_none=True)
            _data.update({'id': exercise_id})
            obj = await exercise_repo.update(Exercise(**_data))
            await exercise_repo.session.commit()
            return ExerciseCreate.model_validate(obj)
        except Exception as ex:
            raise HTTPException(detail=str(ex), status_code=status_codes.HTTP_404_NOT_FOUND)

    @delete('/delete/{exercise_id:str}', tags=exercise_controller_tag)
    async def delete_exercise(
            self,
            exercise_repo: ExerciseRepository,
            exercise_id: str = Parameter(title='Exercise IDs',
                                         description='Comma Separated List Primary Key Of The Exercises to Delete.', ),
    ) -> None:
        """## Delete Exercise From The System"""
        try:
            _ = await exercise_repo.delete_many(exercise_id.split(','))
            # _ = await exercise_repo.delete(exercise_id)
            await exercise_repo.session.commit()
        except Exception as ex:
            raise HTTPException(detail=str(ex), status_code=status_codes.HTTP_404_NOT_FOUND)
