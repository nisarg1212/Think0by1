from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apis import views

router = DefaultRouter()
router.register(r'questions', views.QuestionViewSet, basename='question')
router.register(r'responses', views.ModelResponseViewSet, basename='modelresponse')

urlpatterns = [
    path('', include(router.urls)),
]
