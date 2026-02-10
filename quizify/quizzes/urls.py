from django.urls import path
from .views import QuizListView, QuizDetailView, QuizAnswerView, MyQuizListView

app_name = 'quizzes'

urlpatterns = [
    path('', QuizListView.as_view(), name='list'),
    path('mine', MyQuizListView.as_view(), name='mine'),
    path('<int:quiz_id>', QuizDetailView.as_view(), name='detail'),
    path('<int:quiz_id>/answer', QuizAnswerView.as_view(), name='answer'),
]
