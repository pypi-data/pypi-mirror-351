"""Defines base exercise class."""

from pydantic import BaseModel

from wse_exercises.core.mathem.enums import Exercises


class ExerciseConfig(BaseModel):
    """Exercise base config."""


class TaskRequest(BaseModel):
    """Request an exercise with a given configuration.

    :param Exercises name: Exercise name.
    :param ExerciseConfig config: Exercise configuration.
    """

    name: Exercises
    config: ExerciseConfig
