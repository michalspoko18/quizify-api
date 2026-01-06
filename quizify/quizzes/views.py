from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from .models import Quiz


class QuizListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        quizzes = Quiz.objects.all()
        summarized = [
            {
                "id": quiz.id,
                "title": quiz.title,
                "description": quiz.description,
            }
            for quiz in quizzes
        ]
        return Response(summarized, status=status.HTTP_200_OK)


class QuizDetailView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, quiz_id: int):
        quiz = get_object_or_404(Quiz.objects.prefetch_related(
            "questions__answers"
        ), pk=quiz_id)

        payload = {
            "id": quiz.id,
            "title": quiz.title,
            "description": quiz.description,
            "questions": [
                {
                    "id": question.id,
                    "question": question.text,
                    "answers": [
                            {
                                "id": answer.id,
                                "text": answer.text,
                            }
                        for answer in question.answers.all()
                    ],
                }
                for question in quiz.questions.all()
            ],
        }

        return Response(payload, status=status.HTTP_200_OK)


class QuizAnswerView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, quiz_id: int):
        quiz = get_object_or_404(
            Quiz.objects.prefetch_related("questions__answers"),
            pk=quiz_id,
        )

        # Accept payload:
        # - { answers: [{ questionId, answerId }, ...] }
        # - { answers: { [questionId]: answerId } }
        submitted = request.data.get("answers") or []
        answers_map = {}
        if isinstance(submitted, list):
            answers_map = {
                item.get("questionId"): item.get("answerId")
                for item in submitted
            }
        elif isinstance(submitted, dict):
            answers_map = submitted

        # Normalize keys and values: JSON object keys become strings,
        # but question IDs in DB are integers. Convert numeric-string keys
        # and numeric-string values to ints for correct matching.
        normalized = {}
        if isinstance(answers_map, dict):
            for k, v in answers_map.items():
                try:
                    key = int(k)
                except (TypeError, ValueError):
                    key = k
                try:
                    val = int(v)
                except (TypeError, ValueError):
                    val = v
                normalized[key] = val
        answers_map = normalized

        total = quiz.questions.count()
        correct = 0
        incorrect_details = []

        for question in quiz.questions.all():
            selected = answers_map.get(question.id)
            if selected is None:
                continue
            is_correct = False
            correct_answer_text = None
            user_answer_text = None
            for answer in question.answers.all():
                if answer.is_correct:
                    correct_answer_text = answer.text
                if answer.id == selected:
                    user_answer_text = answer.text
                    if answer.is_correct:
                        is_correct = True
            if is_correct:
                correct += 1
            else:
                incorrect_details.append(
                    {
                        "question": question.text,
                        "userAnswer": user_answer_text,
                        "correctAnswer": correct_answer_text,
                    }
                )

        percentage = (correct / total * 100) if total else 0
        result = {
            "quizId": quiz_id,
            "totalQuestions": total,
            "correctAnswers": correct,
            "wrongAnswers": total - correct,
            "percentage": round(percentage),
            "passed": percentage >= 50,
            "incorrectDetails": incorrect_details,
        }
        return Response(result, status=status.HTTP_200_OK)
