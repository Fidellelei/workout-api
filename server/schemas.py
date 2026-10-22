from marshmallow import Schema, fields


class ExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    category = fields.Str(required=True)
    equipment_needed = fields.Bool(load_default=False)

    # Shown on GET /exercises/<id>: the workouts this exercise appears in
    workouts = fields.Nested(
        'WorkoutSchema', many=True, dump_only=True,
        only=('id', 'date', 'duration_minutes', 'notes')
    )


class WorkoutSchema(Schema):
    id = fields.Int(dump_only=True)
    date = fields.Date(required=True)
    duration_minutes = fields.Int(required=True)
    notes = fields.Str(allow_none=True)

    # Shown on GET /workouts/<id>: each exercise with its reps/sets/duration
    workout_exercises = fields.Nested(
        'WorkoutExerciseSchema', many=True, dump_only=True,
        exclude=('workout', 'workout_id')
    )


class WorkoutExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    workout_id = fields.Int(dump_only=True)
    exercise_id = fields.Int(dump_only=True)
    reps = fields.Int(allow_none=True)
    sets = fields.Int(allow_none=True)
    duration_seconds = fields.Int(allow_none=True)

    # Basic info only, so nested data can't loop back forever
    workout = fields.Nested(
        'WorkoutSchema', dump_only=True,
        only=('id', 'date', 'duration_minutes', 'notes')
    )
    exercise = fields.Nested(
        'ExerciseSchema', dump_only=True,
        only=('id', 'name', 'category', 'equipment_needed')
    )