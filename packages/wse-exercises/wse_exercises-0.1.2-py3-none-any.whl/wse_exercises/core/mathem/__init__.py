"""WSE mathematical exercises."""

__all__ = [
    'AddingExercise',
    'DivisionExercise',
    'EXERCISES',
    'ExactOperandGenerator',
    'MultiplicationExercise',
    'RandomOperandGenerator',
    'SimpleMathExerciseConfig',
    'SubtractionExercise',
]

from wse_exercises.core.mathem.base.exercise import SimpleMathExerciseConfig
from wse_exercises.core.mathem.enums import Exercises
from wse_exercises.core.mathem.exercises import (
    AddingExercise,
    DivisionExercise,
    MultiplicationExercise,
    SubtractionExercise,
)
from wse_exercises.core.mathem.services.operand_generator import (
    ExactOperandGenerator,
    RandomOperandGenerator,
)

EXERCISES = {
    Exercises.ADDING: AddingExercise,
    Exercises.DIVISION: DivisionExercise,
    Exercises.MULTIPLICATION: MultiplicationExercise,
    Exercises.SUBTRACTION: SubtractionExercise,
}
