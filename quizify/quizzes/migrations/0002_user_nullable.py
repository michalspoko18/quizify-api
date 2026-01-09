"""
Migration to allow null user on UserQuizResult.
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quizzes', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userquizresult',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=models.deletion.CASCADE, to='quizify_auth.user'),
        ),
    ]
