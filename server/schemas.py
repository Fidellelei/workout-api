from marshmallow import Schema, fields, validate, validates, validates_schema, ValidationError

from models import VALID_CATEGORIES


class ExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    category = fields.Str(required=True, validate=validate.OneOf(VALID_CATEGORIES))
    equipment_needed = fields.Bool(load_default=False)

    # Shown on GET /exercises/<id>: the workouts this exercise appears in
    workouts = fields.Nested(
        'WorkoutSchema', many=True, dump_only=True,
        only=('id', 'date', 'duration_minutes', 'notes')
    )

    @validates('name')
    def validate_name_not_blank(self, value):
        if not value.strip():
            raise ValidationError('Name cannot be blank.')


class WorkoutSchema(Schema):
    id = fields.Int(dump_only=True)
    date = fields.Date(required=True)
    duration_minutes = fields.Int(required=True, validate=validate.Range(min=1))
    notes = fields.Str(allow_none=True, validate=validate.Length(max=500))

    # Shown on GET /workouts/<id>: each exercise with its reps/sets/duration
    workout_exercises = fields.Nested(
        'WorkoutExerciseSchema', many=True, dump_only=True,
        exclude=('workout', 'workout_id')
    )


class WorkoutExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    workout_id = fields.Int(dump_only=True)
    exercise_id = fields.Int(dump_only=True)
    reps = fields.Int(allow_none=True, validate=validate.Range(min=1))
    sets = fields.Int(allow_none=True, validate=validate.Range(min=1))
    duration_seconds = fields.Int(allow_none=True, validate=validate.Range(min=1))

    # Basic info only, so nested data can't loop back forever
    workout = fields.Nested(
        'WorkoutSchema', dump_only=True,
        only=('id', 'date', 'duration_minutes', 'notes')
    )
    exercise = fields.Nested(
        'ExerciseSchema', dump_only=True,
        only=('id', 'name', 'category', 'equipment_needed')
    )

    @validates_schema
    def validate_has_reps_or_duration(self, data, **kwargs):
        # An exercise entry is meaningless without either reps or a duration
        if data.get('reps') is None and data.get('duration_seconds') is None:
            raise ValidationError('Provide reps or duration_seconds (or both).')