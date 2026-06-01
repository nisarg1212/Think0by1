from django.db import models

class Question(models.Model):
    
    prompt = modeles.textField(blank=True)

    critique = models.TextField(blank=True)

    final_answer = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.prompt[:50]

class ModelResponse(models.Model):

    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name=resp)

    model_name = models.CharField(max_length=100)

    score = models.FloatField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    
