from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Exercise(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_gym_exercise = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Workout(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    is_gym_workout = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username}'s workout on {self.date}"

class WorkoutExercise(models.Model):
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE, related_name='exercises')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    sets = models.IntegerField()
    reps = models.IntegerField()
    weight = models.FloatField(null=True, blank=True)  # For gym exercises
    duration = models.DurationField(null=True, blank=True)  # For home bodyweight exercises

    def __str__(self):
        return f"{self.exercise.name} - {self.sets}x{self.reps}"
