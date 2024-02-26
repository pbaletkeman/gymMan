from __future__ import annotations

from typing import TYPE_CHECKING

from litestar.exceptions import HTTPException
from litestar.pagination import OffsetPagination
from litestar.repository.filters import OrderBy

from litestar import get, HttpMethod, route, status_codes
from litestar.contrib.sqlalchemy.repository import SQLAlchemyAsyncRepository
from litestar.controller import Controller
from litestar.di import Provide
from litestar.handlers.http_handlers.decorators import delete, post
from litestar.params import Parameter
from litestar.repository.filters import LimitOffset
from pydantic import TypeAdapter

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

from models.exercise import Exercise, ExerciseCreate, ExerciseDTO
from logger import logger


class ExerciseRepository(SQLAlchemyAsyncRepository[Exercise]):
    """Exercise repository."""

    model_type = Exercise


async def provide_exercise_repo(db_session: AsyncSession) -> ExerciseRepository:
    """This provides a simple example demonstrating how to override the join options
    for the repository."""
    return ExerciseRepository(session=db_session)


def provide_limit_offset_pagination(
    current_page: int = Parameter(ge=1, query="currentPage", default=1, required=False),
    page_size: int = Parameter(
        query="pageSize",
        ge=1,
        default=10,
        required=False,
    ),
) -> LimitOffset:
    """Add offset/limit pagination.

    Return type consumed by `Repository.apply_limit_offset_pagination()`.

    Parameters
    ----------
    current_page : int
        LIMIT to apply to select.
    page_size : int
        OFFSET to apply to select.
    """
    return LimitOffset(page_size, page_size * (current_page - 1))


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
        """## List exercise items."""
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
                                                                description='The exercise to update.', ),
                                   ) -> ExerciseDTO:
        """## Get details of an Exercise record."""
        try:
            obj = await exercise_repo.get_one(id=exercise_id)
            return ExerciseDTO.model_validate(obj)
        except Exception as ex:
            raise HTTPException(detail=str(ex), status_code=status_codes.HTTP_404_NOT_FOUND)

    @post(tags=exercise_controller_tag)
    async def create_exercise(self, exercise_repo: ExerciseRepository,
                              data: ExerciseCreate, ) -> ExerciseDTO:
        """## Create a new exercise."""
        try:
            _data = data.model_dump(exclude_unset=True, by_alias=False, exclude_none=True)
            obj = await exercise_repo.add(Exercise(**_data))
            await exercise_repo.session.commit()
            return ExerciseDTO.model_validate(obj)
        except Exception as ex:
            raise HTTPException(detail=str(ex), status_code=status_codes.HTTP_404_NOT_FOUND)

    @route('/{exercise_id:int}',
           http_method=[HttpMethod.PUT, HttpMethod.PATCH],
           tags=exercise_controller_tag)
    async def update_exercise(
            self,
            exercise_repo: ExerciseRepository,
            data: ExerciseCreate,
            exercise_id: int = Parameter(title='Exercise ID', description='The exercise to update.', ),
    ) -> ExerciseCreate:
        """## Update an exercise."""
        try:
            _data = data.model_dump(exclude_unset=True, exclude_none=True)
            _data.update({'id': exercise_id})
            obj = await exercise_repo.update(Exercise(**_data))
            await exercise_repo.session.commit()
            return ExerciseCreate.model_validate(obj)
        except Exception as ex:
            raise HTTPException(detail=str(ex), status_code=status_codes.HTTP_404_NOT_FOUND)

    @delete('/{exercise_id:int}', tags=exercise_controller_tag)
    async def delete_exercise_tag(
            self,
            exercise_repo: ExerciseRepository,
            exercise_id: int = Parameter(title='Exercise ID',
                                         description='The exercise to delete.', ),
    ) -> None:
        """## Delete an exercise from the system."""
        try:
            _ = await exercise_repo.delete(exercise_id)
            await exercise_repo.session.commit()
        except Exception as ex:
            raise HTTPException(detail=str(ex), status_code=status_codes.HTTP_404_NOT_FOUND)
