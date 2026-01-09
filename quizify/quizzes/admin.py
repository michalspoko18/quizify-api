from django.contrib import admin
from .models import Quiz, Question, Answer, UserQuizResult


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 0


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ("title", "created_at")
    search_fields = ("title",)
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("quiz", "text")
    search_fields = ("text",)
    inlines = [AnswerInline]


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ("question", "text", "is_correct")
    list_filter = ("is_correct",)
    search_fields = ("text",)


@admin.register(UserQuizResult)
class UserQuizResultAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "quiz",
        "percentage",
        "correct_answers",
        "total_questions",
        "passed",
        "created_at",
    )
    list_filter = ("passed", "quiz")
    search_fields = ("user__email", "quiz__title")
