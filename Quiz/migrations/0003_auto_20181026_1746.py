# Generated by Django 2.0.9 on 2018-10-26 17:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Quiz', '0002_score_taken_on'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quiz',
            name='no_of_ques',
            field=models.IntegerField(default=0),
        ),
    ]