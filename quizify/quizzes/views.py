from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .serializers import QuizSerializer

from .models import Quiz, UserQuizResult
from django.db.models import Count, Avg, Sum, Max
from django.contrib.auth import get_user_model
from auth.serializers import UserSerializer


class QuizListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        quizzes = Quiz.objects.annotate(questions_count=Count("questions")).all()
        summarized = [
            {
                "id": quiz.id,
                "title": quiz.title,
                "description": quiz.description,
                "questionsCount": getattr(quiz, "questions_count", 0),
            }
            for quiz in quizzes
        ]
        return Response(summarized, status=status.HTTP_200_OK)

    def post(self, request):
        owner = None
        # Prefer authenticated user
        if getattr(request.user, "is_authenticated", False):
            owner = request.user
        else:
            # Allow frontend to supply owner id in request payload
            owner_id = (
                request.data.get("ownerId")
                or request.data.get("owner_id")
                or request.data.get("userId")
                or request.data.get("user_id")
            )
            # Also accept ownerGoogleId (frontend may supply Google `sub`)
            owner_google = (
                request.data.get("ownerGoogleId")
                or request.data.get("owner_google_id")
                or request.data.get("ownerGoogle")
                or request.data.get("owner_google")
            )
            if owner_id:
                try:
                    User = get_user_model()
                    owner = User.objects.filter(pk=owner_id).first()
                except Exception:
                    owner = None
            # If owner not found by PK, try resolving by Google id
            if not owner and owner_google:
                try:
                    User = get_user_model()
                    owner = User.objects.filter(google_id=owner_google).first()
                except Exception:
                    owner = None

        if not owner:
            return Response({"detail": "Owner id is required when not authenticated."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = QuizSerializer(data=request.data, context={"user": owner})

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        quiz = serializer.save()
        return Response(QuizSerializer(quiz).data, status=status.HTTP_201_CREATED)


class MyQuizListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        owner = request.user if getattr(request.user, "is_authenticated", False) else None
        if not owner:
            owner_id = (
                request.query_params.get("ownerId")
                or request.query_params.get("owner_id")
                or request.query_params.get("userId")
                or request.query_params.get("user_id")
            )
            owner_google = (
                request.query_params.get("ownerGoogleId")
                or request.query_params.get("owner_google_id")
                or request.query_params.get("ownerGoogle")
                or request.query_params.get("owner_google")
            )

            User = get_user_model()
            if owner_id:
                owner = User.objects.filter(pk=owner_id).first()
            if not owner and owner_google:
                owner = User.objects.filter(google_id=owner_google).first()

        if not owner:
            return Response(
                {"detail": "Owner id is required when not authenticated."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        quizzes = (
            Quiz.objects.filter(owner=owner)
            .annotate(questions_count=Count("questions"))
            .order_by("-created_at")
        )

        payload = [
            {
                "id": quiz.id,
                "title": quiz.title,
                "description": quiz.description,
                "owner": quiz.owner_id,
                "questionsCount": getattr(quiz, "questions_count", 0),
            }
            for quiz in quizzes
        ]

        return Response(payload, status=status.HTTP_200_OK)


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

    def put(self, request, quiz_id: int):
        quiz = get_object_or_404(Quiz.objects.prefetch_related("questions__answers"), pk=quiz_id)
        # owner check
        if not getattr(request.user, "is_authenticated", False) or quiz.owner_id != getattr(request.user, "id", None):
            return Response({"detail": "You do not have permission to modify this quiz."}, status=status.HTTP_403_FORBIDDEN)

        serializer = QuizSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        quiz = serializer.update(quiz, serializer.validated_data)
        return Response(QuizSerializer(quiz).data, status=status.HTTP_200_OK)

    def delete(self, request, quiz_id: int):
        quiz = get_object_or_404(Quiz, pk=quiz_id)
        # Allow deletion when:
        # - the request is authenticated and request.user is the owner, OR
        # - the frontend provides ownerId/ownerGoogleId via query params that match the quiz owner
        allowed = False

        if getattr(request.user, "is_authenticated", False):
            if quiz.owner_id == getattr(request.user, "id", None) or quiz.owner_id == getattr(request.user, "pk", None):
                allowed = True

        if not allowed:
            owner_id = (
                request.query_params.get("ownerId")
                or request.query_params.get("owner_id")
                or request.query_params.get("userId")
                or request.query_params.get("user_id")
            )
            owner_google = (
                request.query_params.get("ownerGoogleId")
                or request.query_params.get("owner_google_id")
                or request.query_params.get("ownerGoogle")
                or request.query_params.get("owner_google")
            )

            if owner_id and str(quiz.owner_id) == str(owner_id):
                allowed = True
            elif owner_google:
                try:
                    if getattr(quiz.owner, "google_id", None) and str(quiz.owner.google_id) == str(owner_google):
                        allowed = True
                except Exception:
                    # If quiz.owner is not present or has no google_id, skip
                    pass

        if not allowed:
            return Response({"detail": "You do not have permission to delete this quiz."}, status=status.HTTP_403_FORBIDDEN)

        quiz.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


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
        # Persist result (allow anonymous results)
        try:
            UserQuizResult.objects.create(
                user=(request.user if getattr(request.user, 'is_authenticated', False) else None),
                external_user_id=request.data.get('userId') or request.data.get('user_id'),
                quiz=quiz,
                percentage=round(percentage),
                correct_answers=correct,
                total_questions=total,
                passed=percentage >= 50,
            )
        except Exception:
            # Don't fail the whole request if saving result fails
            pass

        return Response(result, status=status.HTTP_200_OK)


class RankingView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        # Expected payload: { quizId, score/percentage, correctAnswers, totalQuestions, passed }
        data = request.data or {}
        quiz_id = data.get("quizId") or data.get("quiz_id")
        if not quiz_id:
            return Response({"message": "quizId is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            quiz = Quiz.objects.get(pk=quiz_id)
        except Quiz.DoesNotExist:
            return Response({"message": "Quiz not found"}, status=status.HTTP_404_NOT_FOUND)

        percentage = data.get("percentage") or data.get("score") or 0
        correct_answers = data.get("correctAnswers") or data.get("correct_answers") or 0
        total_questions = data.get("totalQuestions") or data.get("total_questions") or 0
        passed = bool(data.get("passed", percentage >= 50))

        result = UserQuizResult.objects.create(
            user=(request.user if getattr(request.user, 'is_authenticated', False) else None),
            external_user_id=data.get('userId') or data.get('user_id'),
            quiz=quiz,
            percentage=int(percentage),
            correct_answers=int(correct_answers),
            total_questions=int(total_questions),
            passed=passed,
        )

        return Response({
            "id": result.id,
            "quizId": quiz.id,
            "percentage": result.percentage,
            "correctAnswers": result.correct_answers,
            "totalQuestions": result.total_questions,
            "passed": result.passed,
        }, status=status.HTTP_201_CREATED)

    def get(self, request):
        """Return aggregated ranking data.

        Query params:
        - type: 'global' (default), 'me', 'popular'
        - limit: integer limit for lists
        - userId: external user id for 'me' lookup (optional)
        """
        qtype = request.query_params.get("type", "global")
        try:
            limit = int(request.query_params.get("limit", 10) or 10)
        except (TypeError, ValueError):
            limit = 10

        User = get_user_model()

        if qtype == "popular":
            # Most popular quizzes
            qs = (
                UserQuizResult.objects.values("quiz__id", "quiz__title")
                .annotate(times_completed=Count("id"), average_score=Avg("percentage"))
                .order_by("-times_completed")[:limit]
            )

            payload = [
                {
                    "quizId": item["quiz__id"],
                    "quizTitle": item.get("quiz__title"),
                    "timesCompleted": item.get("times_completed", 0),
                    "averageScore": round(item.get("average_score") or 0),
                }
                for item in qs
            ]

            return Response(payload, status=status.HTTP_200_OK)

        if qtype == "me":
            # User stats for authenticated user or external userId
            user = request.user if getattr(request.user, "is_authenticated", False) else None
            external = request.query_params.get("userId") or request.query_params.get("user_id")

            if user:
                qs = UserQuizResult.objects.filter(user=user)
            elif external:
                qs = UserQuizResult.objects.filter(external_user_id=external)
            else:
                return Response(
                    {
                        "totalQuizzes": 0,
                        "averageScore": 0,
                        "bestScore": 0,
                        "totalCorrect": 0,
                        "totalQuestions": 0,
                    },
                    status=status.HTTP_200_OK,
                )

            aggs = qs.aggregate(
                total=Count("id"),
                average=Avg("percentage"),
                best=Max("percentage"),
                correct=Sum("correct_answers"),
                questions=Sum("total_questions"),
            )

            payload = {
                "totalQuizzes": aggs.get("total") or 0,
                "averageScore": round(aggs.get("average") or 0),
                "bestScore": aggs.get("best") or 0,
                "totalCorrect": aggs.get("correct") or 0,
                "totalQuestions": aggs.get("questions") or 0,
            }

            return Response(payload, status=status.HTTP_200_OK)

        # default: global ranking
        # Group by external_user_id when present, otherwise by user id
        # We'll build a map keyed by a stable identifier
        results = (
            UserQuizResult.objects.values("external_user_id", "user")
            .annotate(
                quizzes_completed=Count("id"),
                average_score=Avg("percentage"),
                total_score=Sum("percentage"),
            )
            .order_by("-average_score", "-total_score")
        )

        payload = []
        for item in results:
            if len(payload) >= limit:
                break
            ext = item.get("external_user_id")
            user_pk = item.get("user")

            userId = None
            userName = None
            userNick = None

            if ext:
                # External identifier (e.g. Google `sub`) — try to resolve to a local User
                userId = ext
                try:
                    u = User.objects.filter(google_id=ext).first()
                    if u:
                        userName = getattr(u, "email", None) or getattr(u, "username", None)
                        userNick = UserSerializer(u).data.get("nick")
                except Exception:
                    userName = None
                    userNick = None
            elif user_pk:
                # Use plain string PK to match frontend `store.sub`
                userId = str(user_pk)
                try:
                    u = User.objects.filter(pk=user_pk).first()
                    if u:
                        userName = getattr(u, "email", None) or getattr(u, "username", None)
                        userNick = UserSerializer(u).data.get("nick")
                except Exception:
                    userName = None
                    userNick = None
            else:
                # skip completely anonymous entries without any identifier
                continue

            payload.append(
                {
                    "userId": userId,
                    "userName": userName,
                    "userNick": userNick,
                    "quizzesCompleted": item.get("quizzes_completed", 0),
                    "averageScore": round(item.get("average_score") or 0),
                    "totalScore": int(item.get("total_score") or 0),
                }
            )

        return Response(payload, status=status.HTTP_200_OK)
