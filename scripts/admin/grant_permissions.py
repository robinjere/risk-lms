"""
Grant permissions to Head of Risk and Risk & Compliance Specialist users
"""
from accounts.models import User
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

print('='*70)
print('GRANTING PERMISSIONS')
print('='*70)
print()

# Get Head of Risk and Risk & Compliance Specialist users
users = User.objects.filter(role__in=['head_of_risk', 'risk_compliance_specialist'])

# Apps they need permissions for
apps = ['courses', 'videos', 'quizzes', 'certificates', 'progress']

for user in users:
    print(f'Setting permissions for: {user.get_full_name()} ({user.email})')
    
    # Get all permissions for the specified apps
    perms = Permission.objects.filter(content_type__app_label__in=apps)
    
    # Assign all permissions
    user.user_permissions.set(perms)
    
    # Ensure is_staff is True
    user.is_staff = True
    user.save()
    
    print(f'  ✅ Granted {perms.count()} permissions')
    print(f'  ✅ is_staff = {user.is_staff}')
    print()

print('='*70)
print('SUCCESS! Users can now upload content.')
print('='*70)
print()
print('Test by logging in at: http://127.0.0.1:8000/admin/')
print()
print('Users:')
for user in users:
    print(f'  - {user.email}')
