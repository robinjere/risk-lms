#!/usr/bin/env python
"""Debug script to test quiz conditions"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'risk_lms.settings')
django.setup()

from videos.models import InteractiveCourse, InteractiveCourseProgress
from quizzes.models import Question
from accounts.models import User

print("=" * 60)
print("QUIZ DEBUG ANALYSIS")
print("=" * 60)

# Get interactive course
ic = InteractiveCourse.objects.first()
print(f"\nInteractive Course: {ic.title if ic else 'None'}")
print(f"Total Slides: {ic.total_slides if ic else 'N/A'}")

# Check questions
questions = Question.objects.filter(interactive_course=ic) if ic else []
print(f"\nQuestions for this course: {questions.count()}")
if questions.count() > 0:
    for q in questions:
        print(f"  - {q.question_text[:60]}...")
        print(f"    Options: {q.options.count()}")
else:
    print("  WARNING: No questions assigned to this interactive course!")

# Check user progress
print("\n" + "=" * 60)
print("USER PROGRESS RECORDS")
print("=" * 60)

for user in User.objects.filter(role='banker'):
    progress = InteractiveCourseProgress.objects.filter(
        user=user, 
        interactive_course=ic
    ).first() if ic else None
    
    if progress:
        print(f"\n{user.username} ({user.get_full_name()}):")
        print(f"  Current Slide: {progress.current_slide}")
        print(f"  Highest Reached: {progress.highest_slide_reached}")
        print(f"  Content Completed: {progress.content_completed}")
        print(f"  Quiz Passed: {progress.quiz_passed}")
        print(f"  Quiz Score: {progress.quiz_score}")
        
        # Check if can take quiz
        can_take = progress.content_completed and questions.count() > 0
        print(f"  Can Take Quiz: {can_take}")
    else:
        print(f"\n{user.username}: No progress record")

print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)

if questions.count() == 0:
    print("\n⚠️  ISSUE FOUND: No questions in the question bank!")
    print("   Users cannot take quiz because there are no questions.")
else:
    print(f"\n✓ {questions.count()} questions available for quiz")
