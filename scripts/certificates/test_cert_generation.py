import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'risk_lms.settings')
django.setup()

from accounts.models import User
from courses.models import Course
from quizzes.models import QuizAttempt
from videos.models import VideoProgress
from django.utils import timezone

# Get MMalopa user and course
user = User.objects.get(username='MMalopa')
course = Course.objects.get(title='Risk And Compliance Fundamentals')

print(f'Testing certificate generation for: {user.get_full_name()}')
print(f'Course: {course.title}')

# Check current status
total_videos = course.videos.count()
completed_videos = VideoProgress.objects.filter(
    user=user,
    video__course=course,
    is_completed=True
).count()

print(f'Videos completed: {completed_videos}/{total_videos}')

# Check quiz attempts
quiz_attempts = QuizAttempt.objects.filter(
    user=user,
    course=course,
    completed_at__isnull=False
).order_by('-score')

print(f'Quiz attempts: {quiz_attempts.count()}')

if quiz_attempts.exists():
    best_attempt = quiz_attempts.first()
    print(f'Best score: {best_attempt.score}%')
    print(f'Passed: {best_attempt.passed}')

# Check existing certificates
from certificates.models import Certificate
existing_certs = Certificate.objects.filter(user=user, course=course)
print(f'Existing certificates: {existing_certs.count()}')

if existing_certs.exists():
    for cert in existing_certs:
        print(f'Certificate: {cert.certificate_number}, Score: {cert.overall_score}%')

# If eligible, generate certificate
if completed_videos >= total_videos and quiz_attempts.filter(passed=True).exists():
    print('\n=== User is eligible for certificate ===')
    
    from quizzes.views import check_and_generate_certificate
    certificate = check_and_generate_certificate(user, course)
    
    if certificate:
        print(f'Certificate generated: {certificate.certificate_number}')
        print(f'QR Code: {certificate.qr_code}')
        print(f'PDF File: {certificate.pdf_file}')
    else:
        print('Certificate already exists or generation failed')
else:
    print('\n=== User not eligible for certificate ===')
    print('Requirements: Complete all videos AND pass quiz with 80%+')