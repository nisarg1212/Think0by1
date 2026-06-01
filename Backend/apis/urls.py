from django.urls import path
from apis import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'questions', views.QuestionViewSet)
router.register(r'responses', views.ModelResponseViewSet)

urlpatterns = router.urls
