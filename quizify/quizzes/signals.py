from django.db.models.signals import post_migrate
from django.dispatch import receiver

from .models import Quiz, Question, Answer


@receiver(post_migrate)
def seed_quizzes(sender, **kwargs):
    # Only seed for quizzes app
    if sender.label != "quizzes":
        return

    if Quiz.objects.exists():
        return

    quiz = Quiz.objects.create(
        title="Podstawy HTML i CSS",
        description=(
            "Sprawdź swoją wiedzę z frontendu: semantyka HTML i "
            "stylowanie CSS."
        ),
    )

    q1 = Question.objects.create(
        quiz=quiz,
        text=(
            "Który znacznik HTML jest semantycznie poprawny do nagłówka "
            "strony?"
        ),
    )
    Answer.objects.bulk_create([
        Answer(question=q1, text="<div>", is_correct=False),
        Answer(question=q1, text="<header>", is_correct=True),
        Answer(question=q1, text="<section>", is_correct=False),
        Answer(question=q1, text="<footer>", is_correct=False),
    ])

    q2 = Question.objects.create(
        quiz=quiz,
        text=(
            "Jaka własność CSS odpowiada za rozmieszczenie elementów w osi "
            "głównej w Flexbox?"
        ),
    )
    Answer.objects.bulk_create([
        Answer(question=q2, text="align-items", is_correct=False),
        Answer(question=q2, text="justify-content", is_correct=True),
        Answer(question=q2, text="flex-grow", is_correct=False),
        Answer(question=q2, text="place-items", is_correct=False),
    ])

    q3 = Question.objects.create(
        quiz=quiz,
        text=(
            "Które zapytanie media w CSS zastosuje styl dla ekranów o "
            "szerokości do 768px?"
        ),
    )
    Answer.objects.bulk_create([
        Answer(
            question=q3,
            text="@media (min-width: 768px)",
            is_correct=False,
        ),
        Answer(question=q3, text="@media (max-width: 768px)", is_correct=True),
        Answer(question=q3, text="@media (width: 768px)", is_correct=False),
        Answer(
            question=q3,
            text="@media (between: 480px, 768px)",
            is_correct=False,
        ),
    ])
