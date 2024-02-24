from __future__ import annotations

from typing import Optional

from sqlalchemy import String
from sqlalchemy.orm import mapped_column, Mapped, relationship

from models.base_model import BaseModel, Base
from models.exercise import Exercise


class ExerciseStep(Base):
    id: Mapped[int] = mapped_column(primary_key=True, name='step_id', sort_order=-10)
    sort_order: Mapped[int | None] = mapped_column(nullable=False, default=0, sort_order=0)
    name: Mapped[str] = mapped_column(String(length=30), nullable=False, sort_order=1)
    place_holder: Mapped[str] = mapped_column(String(100), nullable=True, sort_order=2)
    tool_tip: Mapped[str] = mapped_column(String(100), nullable=True, sort_order=3)
    image: str = mapped_column(String(100), nullable=True, sort_order=4)
    description: Mapped[str] = mapped_column(String(), nullable=True, sort_order=5)

    exercise: Mapped[Optional['Exercise']] = (
        relationship(foreign_keys='[Exercise.exercise_id]',
                     primaryjoin='ExerciseStep.exercise_id==Exercise.id')
    )

class ExerciseStepDTO(BaseModel):
    id: int | None
    sort_order: Optional[int] = 0
    name: str
    place_holder: Optional[str] = None
    tool_tip: Optional[str] = None
    image: Optional[str] = None
    description: Optional[str] = None


class ExerciseStepCreate(BaseModel):
    name: str
    sort_order: Optional[int] = 0
    place_holder: Optional[str] = None
    tool_tip: Optional[str] = None
    image: Optional[str] = None
    description: Optional[str] = None
