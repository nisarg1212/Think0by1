from rest_framework import serializers
from .models import Question, ModelResponse

class ModelResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModelResponse
        fields = ['id', 'model_name', 'score', 'created_at', 'response_text', 'critique', 'final_answer']


class QuestionSerializer(serializers.ModelSerializer):
    # Nested serializer to include responses with the question
    responses = ModelResponseSerializer(many=True, read_only=True)
    
    class Meta:
        model = Question
        fields = ['id', 'prompt', 'critique', 'final_answer', 'created_at', 'responses']
        read_only_fields = ['created_at']
