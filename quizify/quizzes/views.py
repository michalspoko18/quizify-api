import json
from pathlib import Path
from typing import Dict, Any

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions


DATA_PATH = Path(__file__).resolve().parent / "data" / "quizzes.json"


def load_quizzes() -> list[Dict[str, Any]]:
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


class QuizListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        quizzes = load_quizzes()
        summarized = [
            {
                "id": q["id"],
                "title": q["title"],
                "description": q.get("description"),
            }
            for q in quizzes
        ]
        return Response(summarized, status=status.HTTP_200_OK)


class QuizDetailView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, quiz_id: int):
        quizzes = load_quizzes()
        for q in quizzes:
            if q.get("id") == quiz_id:
                return Response(q, status=status.HTTP_200_OK)
        return Response(
            {"message": "Nie znaleziono quizu."},
            status=status.HTTP_404_NOT_FOUND,
        )


class QuizAnswerView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, quiz_id: int):
        quizzes = load_quizzes()
        quiz = next((q for q in quizzes if q.get("id") == quiz_id), None)
        if not quiz:
            return Response(
                {"message": "Nie znaleziono quizu."},
                status=status.HTTP_404_NOT_FOUND,
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

        total = len(quiz.get("questions", []))
        correct = 0
        incorrect_details = []

        for q in quiz.get("questions", []):
            selected = answers_map.get(q.get("id"))
            if selected is None:
                continue
            is_correct = False
            correct_answer_text = None
            user_answer_text = None
            for a in q.get("answers", []):
                if a.get("isCorrect"):
                    correct_answer_text = a.get("text")
                if a.get("id") == selected:
                    user_answer_text = a.get("text")
                    if a.get("isCorrect"):
                        is_correct = True
            if is_correct:
                correct += 1
            else:
                incorrect_details.append(
                    {
                        "question": q.get("question"),
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
