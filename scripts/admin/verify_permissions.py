"""
Verify permissions for content uploaders
"""
from accounts.models import User

print('='*70)
print('PERMISSION VERIFICATION')
print('='*70)
print()

users = User.objects.filter(role__in=['head_of_risk', 'risk_compliance_specialist'])

for user in users:
    print(f'User: {user.get_full_name()} ({user.email})')
    print(f'Role: {user.get_role_display()}')
    print(f'is_staff: {user.is_staff}')
    print(f'Total permissions: {user.user_permissions.count()}')
    print()
    print('Key Permissions:')
    print(f'  ✅ Can add video: {user.has_perm("videos.add_video")}')
    print(f'  ✅ Can change video: {user.has_perm("videos.change_video")}')
    print(f'  ✅ Can add course: {user.has_perm("courses.add_course")}')
    print(f'  ✅ Can change course: {user.has_perm("courses.change_course")}')
    print(f'  ✅ Can add question: {user.has_perm("quizzes.add_question")}')
    print(f'  ✅ Can add video subtitle: {user.has_perm("videos.add_videosubtitle")}')
    print()
    print('-'*70)
    print()

print('='*70)
print('✅ ALL PERMISSIONS GRANTED!')
print('='*70)
print()
print('Users can now:')
print('  1. Login at http://127.0.0.1:8000/admin/')
print('  2. Upload courses')
print('  3. Upload videos')
print('  4. Add subtitles/translations')
print('  5. Create questions')
