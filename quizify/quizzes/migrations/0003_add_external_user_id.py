"""
Add external_user_id to UserQuizResult
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quizzes', '0002_user_nullable'),
    ]

    operations = [
        migrations.AddField(
            model_name='userquizresult',
            name='external_user_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
