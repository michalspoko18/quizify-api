from rest_framework import serializers
from .models import Quiz, Question, Answer


class AnswerSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    text = serializers.CharField(max_length=300)
    is_correct = serializers.BooleanField(default=False)


class QuestionSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    text = serializers.CharField(max_length=500)
    answers = AnswerSerializer(many=True)

    def validate_answers(self, value):
        if not isinstance(value, list) or len(value) < 2:
            raise serializers.ValidationError("Each question must have at least 2 answers")
        correct = [a for a in value if a.get("is_correct")]
        if len(correct) < 1:
            raise serializers.ValidationError("Each question must have at least one correct answer")
        return value


class QuizSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(allow_blank=True, required=False)
    questions = QuestionSerializer(many=True)

    def validate_questions(self, value):
        if not isinstance(value, list) or len(value) < 1:
            raise serializers.ValidationError("Quiz must contain at least one question")
        return value

    def create(self, validated_data):
        user = self.context.get("user")
        questions = validated_data.pop("questions", [])
        quiz = Quiz.objects.create(owner=user, **validated_data)
        for q in questions:
            answers = q.pop("answers", [])
            question = Question.objects.create(quiz=quiz, **q)
            for a in answers:
                Answer.objects.create(question=question, **a)
        return quiz

    def update(self, instance, validated_data):
        # Replace title/description and fully replace questions/answers
        instance.title = validated_data.get("title", instance.title)
        instance.description = validated_data.get("description", instance.description)
        instance.save()

        # Delete existing questions & answers and recreate from payload
        instance.questions.all().delete()
        questions = validated_data.get("questions", [])
        for q in questions:
            answers = q.pop("answers", [])
            question = Question.objects.create(quiz=instance, **q)
            for a in answers:
                Answer.objects.create(question=question, **a)
        return instance

    def to_representation(self, instance):
        return {
            "id": instance.id,
            "title": instance.title,
            "description": instance.description,
            "owner": getattr(instance.owner, "id", None),
            "questions": [
                {
                    "id": q.id,
                    "text": q.text,
                    "answers": [
                        {"id": a.id, "text": a.text, "is_correct": a.is_correct}
                        for a in q.answers.all()
                    ],
                }
                for q in instance.questions.all()
            ],
        }
