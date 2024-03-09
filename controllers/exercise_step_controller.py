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

from models.exercise_step import ExerciseStep, ExerciseStepCreate, ExerciseStepDTO
from logger import logger


class ExerciseStepRepository(SQLAlchemyAsyncRepository[ExerciseStep]):
    """Exercise Step repository"""
    model_type = ExerciseStep


async def provide_exercise_step_repo(db_session: AsyncSession) -> ExerciseStepRepository:
    """This provides a simple example demonstrating how to override the join options
    for the repository."""
    return ExerciseStepRepository(session=db_session)


class ExerciseStepController(Controller):
    path = '/exercise-step'
    dependencies = {
        'exercise_step_repo': Provide(provide_exercise_step_repo),
    }
    exercise_step_controller_tag = ['Exercise Step - CRUD']

    @get(tags=exercise_step_controller_tag)
    async def list_exercise_step(
            self,
            exercise_step_repo: ExerciseStepRepository,
            limit_offset: LimitOffset,
    ) -> OffsetPagination[ExerciseStepDTO]:
        """## List Exercise Step Items"""
        try:
            order_by1 = OrderBy(field_name=ExerciseStep.name)
            results, total = await exercise_step_repo.list_and_count(limit_offset, order_by1)
            type_adapter = TypeAdapter(list[ExerciseStepDTO])
            return OffsetPagination[ExerciseStepDTO](
                items=type_adapter.validate_python(results),
                total=total,
                limit=limit_offset.limit,
                offset=limit_offset.offset,
            )
        except Exception as ex:
            raise HTTPException(detail=str(ex), status_code=status_codes.HTTP_404_NOT_FOUND)

    @get('/details/{exercise_step_id: int}', tags=exercise_step_controller_tag)
    async def get_exercise_step_details(self,
                                        exercise_step_repo: ExerciseStepRepository,
                                        exercise_step_id: int = Parameter(title='Exercise ID',
                                                                          description='Primary Key Of The Exercise To '
                                                                                      'Update.', ),
                                        ) -> ExerciseStepDTO:
        """## Get Details Of An Exercise Step Record"""
        try:
            obj = await exercise_step_repo.get_one(id=exercise_step_id)
            return ExerciseStepDTO.model_validate(obj)
        except Exception as ex:
            raise HTTPException(detail=str(ex), status_code=status_codes.HTTP_404_NOT_FOUND)

    @post(tags=exercise_step_controller_tag)
    async def create_exercise_step(self, exercise_step_repo: ExerciseStepRepository,
                                   data: ExerciseStepCreate, ) -> ExerciseStepDTO:
        """## Create A New Exercise Step"""
        try:
            _data = data.model_dump(exclude_unset=True, by_alias=False, exclude_none=True)
            obj = await exercise_step_repo.add(ExerciseStep(**_data))
            await exercise_step_repo.session.commit()
            return ExerciseStepDTO.model_validate(obj)
        except Exception as ex:
            raise HTTPException(detail=str(ex), status_code=status_codes.HTTP_404_NOT_FOUND)

    @put('/{exercise_step_id:int}', tags=exercise_step_controller_tag)
    async def update_exercise_step_put(
            self,
            exercise_step_repo: ExerciseStepRepository,
            data: ExerciseStepCreate,
            exercise_step_id: int = Parameter(title='Exercise ID',
                                              description='Primary Key Of The Exercise To Update.', ),
    ) -> ExerciseStepCreate:
        """## Update An Exercise Step"""
        try:
            _data = data.model_dump(exclude_unset=False, exclude_none=False)
            _data.update({'id': exercise_step_id})
            obj = await exercise_step_repo.update(ExerciseStep(**_data))
            await exercise_step_repo.session.commit()
            return ExerciseStepCreate.model_validate(obj)
        except Exception as ex:
            print('error')
            print(ex)
            raise HTTPException(detail=str(ex), status_code=status_codes.HTTP_404_NOT_FOUND)

    @patch('/{exercise_step_id:int}', tags=exercise_step_controller_tag)
    async def update_exercise_step_patch(
            self,
            exercise_step_repo: ExerciseStepRepository,
            data: ExerciseStepCreate,
            exercise_step_id: int = Parameter(title='Exercise ID',
                                              description='Primary Key Of The Exercise To Update.', ),
    ) -> ExerciseStepCreate:
        """## Update An Exercise Step"""
        try:
            _data = data.model_dump(exclude_unset=True, exclude_none=True)
            _data.update({'id': exercise_step_id})
            obj = await exercise_step_repo.update(ExerciseStep(**_data))
            await exercise_step_repo.session.commit()
            return ExerciseStepCreate.model_validate(obj)
        except Exception as ex:
            print('error')
            print(ex)
            raise HTTPException(detail=str(ex), status_code=status_codes.HTTP_404_NOT_FOUND)

    @delete('/delete/{exercise_step_ids:str}', tags=exercise_step_controller_tag)
    async def delete_exercise(
            self,
            exercise_step_repo: ExerciseStepRepository,
            exercise_step_ids: str = Parameter(title='Exercise IDs',
                                               description='Comma Separated List Primary Key Of The Exercises to Delete.', ),
    ) -> None:
        """## Delete Exercise Step From The System"""
        try:
            _ = await exercise_step_repo.delete_many(exercise_step_ids.split(','))
            await exercise_step_repo.session.commit()
        except Exception as ex:
            raise HTTPException(detail=str(ex), status_code=status_codes.HTTP_404_NOT_FOUND)
