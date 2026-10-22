from flask import Flask, request, make_response
from flask_migrate import Migrate
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from models import db, Exercise, Workout, WorkoutExercise
from schemas import ExerciseSchema, WorkoutSchema, WorkoutExerciseSchema

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.sort_keys = False

migrate = Migrate(app, db)

db.init_app(app)

# List endpoints leave out nested data to keep responses small;
# single-item endpoints include it.
workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True, exclude=('workout_exercises',))
exercise_schema = ExerciseSchema()
exercises_schema = ExerciseSchema(many=True, exclude=('workouts',))
workout_exercise_schema = WorkoutExerciseSchema()


# ---------- Error handlers ----------

@app.errorhandler(ValidationError)
def handle_schema_error(error):
    """Request body failed a Marshmallow schema validation."""
    return make_response({'errors': error.messages}, 400)


@app.errorhandler(ValueError)
def handle_model_error(error):
    """A model @validates method rejected a value."""
    db.session.rollback()
    return make_response({'errors': [str(error)]}, 400)


@app.errorhandler(IntegrityError)
def handle_integrity_error(error):
    """A table constraint (unique, check, not null) rejected the data."""
    db.session.rollback()
    return make_response(
        {'errors': ['This conflicts with existing data, e.g. a duplicate exercise name '
                    'or an exercise already added to this workout.']},
        409
    )


@app.errorhandler(404)
def handle_not_found(error):
    return make_response({'error': error.description}, 404)


def get_json_body():
    # silent=True gives None instead of crashing on a missing/invalid body,
    # so the schema can report which fields are missing
    return request.get_json(silent=True) or {}


# ---------- Workouts ----------

@app.route('/workouts', methods=['GET'])
def get_workouts():
    workouts = Workout.query.order_by(Workout.date).all()
    return make_response(workouts_schema.dump(workouts), 200)


@app.route('/workouts/<int:id>', methods=['GET'])
def get_workout(id):
    workout = db.get_or_404(Workout, id, description=f'Workout {id} not found')
    return make_response(workout_schema.dump(workout), 200)


@app.route('/workouts', methods=['POST'])
def create_workout():
    data = workout_schema.load(get_json_body())
    workout = Workout(**data)
    db.session.add(workout)
    db.session.commit()
    return make_response(workout_schema.dump(workout), 201)


@app.route('/workouts/<int:id>', methods=['DELETE'])
def delete_workout(id):
    workout = db.get_or_404(Workout, id, description=f'Workout {id} not found')
    # cascade='all, delete-orphan' on the model also deletes its WorkoutExercises
    db.session.delete(workout)
    db.session.commit()
    return make_response('', 204)


# ---------- Exercises ----------

@app.route('/exercises', methods=['GET'])
def get_exercises():
    exercises = Exercise.query.order_by(Exercise.name).all()
    return make_response(exercises_schema.dump(exercises), 200)


@app.route('/exercises/<int:id>', methods=['GET'])
def get_exercise(id):
    exercise = db.get_or_404(Exercise, id, description=f'Exercise {id} not found')
    return make_response(exercise_schema.dump(exercise), 200)


@app.route('/exercises', methods=['POST'])
def create_exercise():
    data = exercise_schema.load(get_json_body())
    exercise = Exercise(**data)
    db.session.add(exercise)
    db.session.commit()
    return make_response(exercise_schema.dump(exercise), 201)


@app.route('/exercises/<int:id>', methods=['DELETE'])
def delete_exercise(id):
    exercise = db.get_or_404(Exercise, id, description=f'Exercise {id} not found')
    # cascade='all, delete-orphan' on the model also deletes its WorkoutExercises
    db.session.delete(exercise)
    db.session.commit()
    return make_response('', 204)


# ---------- Workout Exercises ----------

@app.route('/workouts/<int:workout_id>/exercises/<int:exercise_id>/workout_exercises',
           methods=['POST'])
def add_exercise_to_workout(workout_id, exercise_id):
    workout = db.get_or_404(Workout, workout_id, description=f'Workout {workout_id} not found')
    exercise = db.get_or_404(Exercise, exercise_id, description=f'Exercise {exercise_id} not found')

    data = workout_exercise_schema.load(get_json_body())
    workout_exercise = WorkoutExercise(workout=workout, exercise=exercise, **data)
    db.session.add(workout_exercise)
    db.session.commit()
    return make_response(workout_exercise_schema.dump(workout_exercise), 201)


if __name__ == '__main__':
    app.run(port=5555, debug=True)