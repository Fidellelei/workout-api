# Workout Tracker API

A Flask REST API for a workout tracking application used by personal trainers. Trainers can create workouts and reusable exercises, then add exercises to workouts with sets, reps, and/or a duration.

Built with Flask, SQLAlchemy, Flask-Migrate, and Marshmallow, with validation at three levels: database table constraints, model validations, and schema validations.

## Tech Stack

- Python 3.12 (3.8.13+ supported)
- Flask 2.2.2
- Flask-SQLAlchemy 3.0.3 / SQLAlchemy 2.0
- Flask-Migrate 3.1.0
- Marshmallow 3.20.1
- SQLite

## Project Structure

```
workout-api/
├── Pipfile
├── Pipfile.lock
├── README.md
└── server/
    ├── app.py          # Flask app, error handlers, and routes
    ├── models.py       # SQLAlchemy models, relationships, constraints, model validations
    ├── schemas.py      # Marshmallow schemas and schema validations
    ├── seed.py         # Resets the database and adds example data
    └── migrations/     # Alembic migration files
```

## Installation

1. Clone the repository and move into it:

```bash
   git clone https://github.com/Fidellelei/workout-api.git
   cd workout-api
```

2. Install dependencies and activate the virtual environment:

```bash
   pipenv install
   pipenv shell
```

3. Move into the server folder and point Flask at the app:

```bash
   cd server
   export FLASK_APP=app.py
```

4. Create the database by running the migrations:

```bash
   flask db upgrade head
```

5. Seed the database with example data (this clears existing data first, so it can be rerun at any time):

```bash
   python seed.py
```

## Running the App

From the `server/` folder, with the virtual environment active:

```bash
flask run --port 5555
```

or

```bash
python app.py
```

The API runs at `http://localhost:5555`.

## Endpoints

### Workouts

| Method | Endpoint | Description |
|---|---|---|
| GET | `/workouts` | List all workouts. |
| GET | `/workouts/<id>` | Show a single workout with its exercises, including the reps, sets, and duration for each. |
| POST | `/workouts` | Create a workout. |
| DELETE | `/workouts/<id>` | Delete a workout and its associated workout exercises. |

**POST /workouts** request body:

```json
{
  "date": "2026-10-22",
  "duration_minutes": 40,
  "notes": "Evening session"
}
```

### Exercises

| Method | Endpoint | Description |
|---|---|---|
| GET | `/exercises` | List all exercises. |
| GET | `/exercises/<id>` | Show a single exercise and the workouts it appears in. |
| POST | `/exercises` | Create an exercise. |
| DELETE | `/exercises/<id>` | Delete an exercise and its associated workout exercises. |

**POST /exercises** request body:

```json
{
  "name": "Lunge",
  "category": "strength",
  "equipment_needed": false
}
```

`category` must be one of `strength`, `cardio`, `flexibility`, or `balance`.

### Workout Exercises

| Method | Endpoint | Description |
|---|---|---|
| POST | `/workouts/<workout_id>/exercises/<exercise_id>/workout_exercises` | Add an exercise to a workout with reps, sets, and/or duration. |

Request body (at least `reps` or `duration_seconds` is required):

```json
{
  "sets": 3,
  "reps": 12,
  "duration_seconds": null
}
```

### Responses and Errors

| Status | Meaning |
|---|---|
| 200 | Success |
| 201 | Created |
| 204 | Deleted (no content) |
| 400 | Invalid data (schema or model validation failed) |
| 404 | Workout or exercise not found |
| 409 | Conflict with existing data (e.g. duplicate exercise name, or exercise already in the workout) |

## Validations

**Table constraints**
- Required columns are `NOT NULL` (exercise name/category, workout date/duration, workout and exercise IDs on the join table).
- Exercise names are unique.
- Workout `duration_minutes` must be greater than 0.
- `reps`, `sets`, and `duration_seconds` must be greater than 0 when provided.
- The same exercise can't be added to the same workout twice.

**Model validations**
- Exercise name cannot be blank.
- Exercise category must be an allowed category.
- Workout duration must be a positive whole number.
- `reps`, `sets`, and `duration_seconds` must be positive whole numbers when provided.

**Schema validations**
- Exercise name must be 1–100 characters and not blank; category must be an allowed category.
- Workout `duration_minutes` must be at least 1; `notes` at most 500 characters.
- `reps`, `sets`, and `duration_seconds` must be at least 1.
- A workout exercise must include `reps` or `duration_seconds`.