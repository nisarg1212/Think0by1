from rest_framework import viewsets
from .models import Question, ModelResponse
from .serializer import QuestionSerializer, ModelResponseSerializer

class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

class ModelResponseViewSet(viewsets.ModelViewSet):
    queryset = ModelResponse.objects.all()
    serializer_class = ModelResponseSerializer
