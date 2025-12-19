import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'risk_lms.settings')
django.setup()

from quizzes.models import Question
from courses.models import Course

print('=== Quiz Questions by Course ===')
for course in Course.objects.all():
    print(f'Course: {course.title}')
    questions = Question.objects.filter(course=course)
    if questions:
        for q in questions:
            print(f'  Q: {q.question_text[:60]}...')
    else:
        print('  No questions found')
    print()