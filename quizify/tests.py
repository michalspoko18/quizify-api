from django.test import TestCase
from rest_framework.test import APIClient

from quizzes.models import Quiz, Question, Answer


class QuizAPITestCase(TestCase):
    def setUp(self):
        # create a quiz with one question and three answers
        self.quiz = Quiz.objects.create(title="Test Quiz", description="Desc")
        self.question = Question.objects.create(quiz=self.quiz, text="What is 2+2?")
        Answer.objects.create(question=self.question, text="3", is_correct=False)
        Answer.objects.create(question=self.question, text="4", is_correct=True)
        Answer.objects.create(question=self.question, text="5", is_correct=False)

        self.client = APIClient()

    def test_quiz_detail_returns_questions_and_answers_from_db(self):
        resp = self.client.get(f"/api/quizzes/{self.quiz.id}")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()

        # Basic shape
        self.assertIn("id", data)
        self.assertIn("questions", data)
        self.assertEqual(data["id"], self.quiz.id)
        self.assertEqual(len(data["questions"]), 1)

        q = data["questions"][0]
        self.assertIn("answers", q)
        self.assertEqual(q["question"], self.question.text)

        # Ensure answers come from DB and do NOT include isCorrect flag
        answers = q["answers"]
        self.assertEqual(len(answers), 3)
        for a in answers:
            self.assertIn("id", a)
            self.assertIn("text", a)
            self.assertNotIn("isCorrect", a)

    def test_answer_endpoint_accepts_string_keys_and_counts_correct(self):
        # Prepare a quiz with one question and clear answers
        quiz = Quiz.objects.create(title="Answer Quiz", description="Desc")
        q = Question.objects.create(quiz=quiz, text="Capital of PL?")
        a1 = Answer.objects.create(question=q, text="Berlin", is_correct=False)
        a2 = Answer.objects.create(question=q, text="Warsaw", is_correct=True)

        client = APIClient()

        # Send answers as a dict with string keys (typical JSON object)
        payload = {"answers": {str(q.id): a2.id}}
        resp = client.post(f"/api/quizzes/{quiz.id}/answer", payload, format="json")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data.get("correctAnswers"), 1)

    def test_authenticated_user_answer_saves_result(self):
        # Create user and authenticate client
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.create_user(email="u@example.com", password="pass", username="u1")

        quiz = Quiz.objects.create(title="Save Quiz", description="Desc")
        q = Question.objects.create(quiz=quiz, text="2+2?")
        a1 = Answer.objects.create(question=q, text="3", is_correct=False)
        a2 = Answer.objects.create(question=q, text="4", is_correct=True)

        client = APIClient()
        client.force_authenticate(user=user)

        payload = {"answers": {str(q.id): a2.id}}
        resp = client.post(f"/api/quizzes/{quiz.id}/answer", payload, format="json")
        self.assertEqual(resp.status_code, 200)

        # Check that a UserQuizResult was created
        from quizzes.models import UserQuizResult
        results = UserQuizResult.objects.filter(user=user, quiz=quiz)
        self.assertEqual(results.count(), 1)
        r = results.first()
        self.assertEqual(r.correct_answers, 1)

    def test_ranking_endpoint_saves_result(self):
        # Create a user and quiz
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.create_user(email="r@example.com", password="pass", username="r1")

        quiz = Quiz.objects.create(title="Rank Quiz", description="Desc")

        client = APIClient()
        client.force_authenticate(user=user)

        payload = {
            "quizId": quiz.id,
            "percentage": 80,
            "correctAnswers": 4,
            "totalQuestions": 5,
            "passed": True,
        }

        resp = client.post("/api/ranking", payload, format="json")
        self.assertEqual(resp.status_code, 201)

        from quizzes.models import UserQuizResult
        results = UserQuizResult.objects.filter(user=user, quiz=quiz)
        self.assertEqual(results.count(), 1)
        r = results.first()
        self.assertEqual(r.percentage, 80)

    def test_anonymous_ranking_save_allowed(self):
        quiz = Quiz.objects.create(title="Anon Quiz", description="Desc")
        client = APIClient()
        payload = {
            "quizId": quiz.id,
            "percentage": 50,
            "correctAnswers": 1,
            "totalQuestions": 2,
            "passed": False,
        }
        resp = client.post("/api/ranking", payload, format="json")
        self.assertEqual(resp.status_code, 201)

        from quizzes.models import UserQuizResult
        results = UserQuizResult.objects.filter(quiz=quiz)
        self.assertEqual(results.count(), 1)
        self.assertIsNone(results.first().user)

    def test_anonymous_with_userId_saves_external_id(self):
        quiz = Quiz.objects.create(title="Anon Quiz 2", description="Desc")
        client = APIClient()
        payload = {
            "quizId": quiz.id,
            "userId": "external-123",
            "percentage": 60,
            "correctAnswers": 3,
            "totalQuestions": 5,
            "passed": True,
        }
        resp = client.post("/api/ranking", payload, format="json")
        self.assertEqual(resp.status_code, 201)

        from quizzes.models import UserQuizResult
        results = UserQuizResult.objects.filter(quiz=quiz)
        self.assertEqual(results.count(), 1)
        self.assertIsNone(results.first().user)
        self.assertEqual(results.first().external_user_id, "external-123")
