from rest_framework import viewsets
from .models import Question, ModelResponse
from .serializer import QuestionSerializer, ModelResponseSerializer

class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

    def perform_create(self, serializer):
        # 1. Save the new Question to the database
        question = serializer.save()

        # 2. Trigger the multi-agent peer review orchestration
        from apis.services.orchestrator import AgentOrchestrator
        orchestrator = AgentOrchestrator()
        orchestrator.run(question.id)


class ModelResponseViewSet(viewsets.ModelViewSet):
    queryset = ModelResponse.objects.all()
    serializer_class = ModelResponseSerializer
