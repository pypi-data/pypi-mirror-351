"""Base interface."""

from datetime import datetime
from typing import Protocol, TypeVar

from wse_exercises.core.mathem.enums import Exercises

AnswerT = TypeVar('AnswerT')
QuestionT = TypeVar('QuestionT')
TaskConfigT = TypeVar('TaskConfigT')
TaskConditionsT = TypeVar('TaskConditionsT')


class ITask(Protocol[TaskConfigT, TaskConditionsT, QuestionT, AnswerT]):
    """The interface of the task."""

    config: TaskConfigT
    conditions: TaskConditionsT
    question: QuestionT
    answer: AnswerT
    exercise_name: Exercises
    error_msg: str
    created: datetime
