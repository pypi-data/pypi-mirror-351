"""Defines base class for task."""

from datetime import datetime
from typing import Generic

from pydantic import BaseModel, ConfigDict, Field

from wse_exercises.core.mathem.enums import Exercises

from .interface import AnswerT, QuestionT, TaskConditionsT, TaskConfigT


class TaskConfig(BaseModel):
    """Task base config."""


class Task(
    BaseModel,
    Generic[TaskConfigT, TaskConditionsT, QuestionT, AnswerT],
):
    """Base class for DTO exercise task."""

    config: TaskConfigT
    conditions: TaskConditionsT
    question: QuestionT
    answer: AnswerT
    exercise_name: Exercises
    created: datetime = Field(default_factory=datetime.now)
    error_msg: str = Field(default='', frozen=True)

    model_config = ConfigDict(
        frozen=True,
    )
