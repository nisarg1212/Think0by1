from rest_framework import viewsets
from .models import Question, ModelResponse
from .serializer import QuestionSerializer, ModelResponseSerializer

class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

    def perform_create(self, serializer):
        # 1. Save the new Question to the database
        question = serializer.save()

        # 2. Trigger the multi-agent peer review orchestration in the background
        from django_q.tasks import async_task
        from apis.tasks import run_orchestration_task
        
        # Offload to Django Q2 worker, returns immediately
        task_id = async_task(run_orchestration_task, question.id)


class ModelResponseViewSet(viewsets.ModelViewSet):
    queryset = ModelResponse.objects.all()
    serializer_class = ModelResponseSerializer
