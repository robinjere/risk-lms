import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'risk_lms.settings')
django.setup()

from accounts.models import User
from courses.models import Course
from quizzes.views import check_and_generate_certificate

# Get MMalopa user and course
user = User.objects.get(username='MMalopa')
course = Course.objects.get(title='Risk And Compliance Fundamentals')

print(f'User: {user.get_full_name()}')
print(f'Course: {course.title}')

# Check if eligible for certificate
certificate = check_and_generate_certificate(user, course)

if certificate:
    print(f'Certificate generated: {certificate.certificate_number}')
    print(f'Score: {certificate.overall_score}%')
    print(f'Verification URL: {certificate.verification_url}')
    print(f'QR Code: {certificate.qr_code}')
    print(f'PDF File: {certificate.pdf_file}')
else:
    print('Certificate not generated - requirements not met')
    
    # Check requirements
    from videos.models import VideoProgress
    from quizzes.models import QuizAttempt
    
    total_videos = course.videos.count()
    completed_videos = VideoProgress.objects.filter(
        user=user,
        video__course=course,
        is_completed=True
    ).count()
    
    print(f'Videos completed: {completed_videos}/{total_videos}')
    
    passed_attempts = QuizAttempt.objects.filter(
        user=user,
        course=course,
        passed=True
    ).count()
    
    print(f'Passed quiz attempts: {passed_attempts}')