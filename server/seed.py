#!/usr/bin/env python3

from datetime import date

from app import app
from models import db, Exercise, Workout, WorkoutExercise

with app.app_context():
    print('Clearing old data...')
    # Delete the join table first so no rows point at missing workouts/exercises
    WorkoutExercise.query.delete()
    Workout.query.delete()
    Exercise.query.delete()
    db.session.commit()

    print('Creating exercises...')
    squat = Exercise(name='Barbell Squat', category='strength', equipment_needed=True)
    push_up = Exercise(name='Push-Up', category='strength', equipment_needed=False)
    running = Exercise(name='Treadmill Run', category='cardio', equipment_needed=True)
    plank = Exercise(name='Plank', category='balance', equipment_needed=False)
    hamstring = Exercise(name='Hamstring Stretch', category='flexibility', equipment_needed=False)
    db.session.add_all([squat, push_up, running, plank, hamstring])

    print('Creating workouts...')
    leg_day = Workout(date=date(2026, 10, 19), duration_minutes=60, notes='Heavy leg day')
    cardio_day = Workout(date=date(2026, 10, 20), duration_minutes=45, notes='Cardio and core')
    recovery = Workout(date=date(2026, 10, 21), duration_minutes=30, notes='Light recovery session')
    db.session.add_all([leg_day, cardio_day, recovery])

    print('Adding exercises to workouts...')
    db.session.add_all([
        WorkoutExercise(workout=leg_day, exercise=squat, sets=4, reps=8),
        WorkoutExercise(workout=leg_day, exercise=push_up, sets=3, reps=15),
        WorkoutExercise(workout=leg_day, exercise=hamstring, duration_seconds=60),
        WorkoutExercise(workout=cardio_day, exercise=running, duration_seconds=1800),
        WorkoutExercise(workout=cardio_day, exercise=plank, sets=3, duration_seconds=45),
        WorkoutExercise(workout=recovery, exercise=hamstring, sets=2, duration_seconds=90),
        WorkoutExercise(workout=recovery, exercise=plank, sets=2, duration_seconds=30),
    ])

    db.session.commit()
    print(f'Seeded {Exercise.query.count()} exercises, {Workout.query.count()} workouts, '
          f'{WorkoutExercise.query.count()} workout exercises.')