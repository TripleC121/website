from rest_framework import viewsets

from .models import Exercise, Workout, WorkoutExercise
from .serializers import (
    ExerciseSerializer,
    WorkoutExerciseSerializer,
    WorkoutSerializer,
)


class ExerciseViewSet(viewsets.ModelViewSet):
    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer


class WorkoutViewSet(viewsets.ModelViewSet):
    queryset = Workout.objects.all()  # Add this line
    serializer_class = WorkoutSerializer


def perform_create(self, serializer):
    serializer.save(user=self.request.user)


def get_queryset(self):
    return Workout.objects.filter(user=self.request.user)


class WorkoutExerciseViewSet(viewsets.ModelViewSet):
    queryset = WorkoutExercise.objects.all()
    serializer_class = WorkoutExerciseSerializer
